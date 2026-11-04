"""As avulsas e o checklist contra o SQLite migrado de verdade: mapeamento, `version` própria de
cada linha, o dono que nunca é tocado, a exclusão lógica e a leitura em uma consulta por tabela."""

from datetime import UTC, date, datetime
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import event, select
from sqlalchemy.exc import IntegrityError
from tests.conftest import FixedClock
from tests.modules.schedule.catalog import marco_id

from wedding.modules.schedule.application.ports import WeddingDate
from wedding.modules.schedule.application.schedule_map import ScheduleReader
from wedding.modules.schedule.domain.entities import ChecklistItem, Task
from wedding.modules.schedule.domain.values import OwnerKind, TaskState
from wedding.modules.schedule.infrastructure.mapping import start_mappers
from wedding.modules.schedule.infrastructure.tables import (
    checklist_items,
    milestones,
    schedule_tasks,
)
from wedding.modules.schedule.infrastructure.uow import SqlScheduleUnitOfWork
from wedding.platform.bootstrap.tables import load_tables
from wedding.platform.db.engine import create_db_engine, create_session_factory
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.errors import VersionConflict
from wedding.shared_kernel.profile import ProfileKind

API_DIR = Path(__file__).parents[3]
NOIVO = Actor(user_id=uuid4(), profile=ProfileKind.NOIVO)
NOIVA = Actor(user_id=uuid4(), profile=ProfileKind.NOIVA)


@pytest.fixture
def banco(tmp_path, clock: FixedClock):
    load_tables()
    start_mappers()
    url = f"sqlite:///{tmp_path / 'cronograma.db'}"
    config = Config(str(API_DIR / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", url)
    command.upgrade(config, "head")
    engine = create_db_engine(url)
    sessions = create_session_factory(engine)

    def uow(ator=NOIVO):
        return SqlScheduleUnitOfWork(sessions, clock, ator)

    uow.engine = engine  # type: ignore[attr-defined]
    yield uow
    engine.dispose()


def _tarefa(**campos) -> Task:
    padrao = {"id": uuid4(), "title": "Pesquisar Alianças", "responsible": ProfileKind.NOIVA}
    return Task(**{**padrao, **campos})


def _item(dono: UUID, tipo=OwnerKind.MILESTONE, texto="Pedir orçamento", posicao=0):
    return ChecklistItem.of_owner(uuid4(), tipo, dono, texto, posicao)


def test_a_avulsa_nova_persiste_com_a_version_um_e_o_autor_da_sessao(banco):  # F-CRN-06
    tarefa = _tarefa(note="nota", target_date=date(2027, 3, 1))
    with banco(NOIVA) as uow:
        uow.schedule.add_task(tarefa)
        uow.commit()
    with banco() as uow:
        lida = uow.schedule.get_task(tarefa.id)
        assert lida is not None
        assert (lida.title, lida.responsible, lida.note, lida.target_date, lida.state) == (
            "Pesquisar Alianças",
            ProfileKind.NOIVA,
            "nota",
            date(2027, 3, 1),
            TaskState.TODO,
        )
        assert lida.version == 1
        linha = uow.session.execute(
            select(schedule_tasks.c.created_by).where(schedule_tasks.c.id == tarefa.id)
        ).one()
    assert linha.created_by == NOIVA.user_id


def test_o_estado_da_avulsa_grava_o_texto_com_feminino(banco):
    tarefa = _tarefa(state=TaskState.DONE)
    with banco() as uow:
        uow.schedule.add_task(tarefa)
        uow.commit()
    with banco() as uow:
        gravado = uow.session.execute(select(schedule_tasks.c.state)).scalar_one()
    assert gravado == "Concluída"


def test_editar_a_avulsa_sobe_a_version_e_duas_edicoes_na_mesma_version_conflitam(banco):
    tarefa = _tarefa()
    with banco() as uow:
        uow.schedule.add_task(tarefa)
        uow.commit()
    primeira, segunda = banco(NOIVO), banco(NOIVA)
    with primeira as a, segunda as b:
        x, y = a.schedule.get_task(tarefa.id), b.schedule.get_task(tarefa.id)
        assert x is not None
        assert y is not None
        x.set_state(TaskState.IN_PROGRESS)
        y.set_state(TaskState.DONE)
        a.commit()
        with pytest.raises(VersionConflict):
            b.commit()
    with banco() as uow:
        assert uow.schedule.get_task(tarefa.id).version == 2  # type: ignore[union-attr]


def test_avulsa_excluida_some_da_lista_mas_o_restaurar_a_encontra(banco, clock):
    tarefa, outra = _tarefa(), _tarefa(title="Outra")
    with banco() as uow:
        uow.schedule.add_task(tarefa)
        uow.schedule.add_task(outra)
        uow.commit()
    with banco(NOIVA) as uow:
        uow.schedule.get_task(tarefa.id).delete(clock.now(), NOIVA.user_id)  # type: ignore[union-attr]
        uow.commit()
    with banco() as uow:
        assert [t.id for t in uow.schedule.list_tasks()] == [outra.id]
        assert uow.schedule.get_task(tarefa.id) is None
        achada = uow.schedule.get_task(tarefa.id, include_deleted=True)
        assert achada is not None
        assert (achada.deleted_at, achada.deleted_by) == (clock.now(), NOIVA.user_id)


def test_o_item_de_marco_e_o_de_avulsa_persistem_com_version_propria(banco):  # F-CRN-07
    tarefa = _tarefa()
    de_marco = _item(marco_id("C06"), texto="Do marco")
    de_avulsa = _item(tarefa.id, OwnerKind.TASK, "Da avulsa")
    with banco() as uow:
        uow.schedule.add_task(tarefa)
        uow.schedule.add_checklist_item(de_marco)
        uow.commit()
    with banco() as uow:  # o item da avulsa só entra depois: a avulsa já existe
        uow.schedule.add_checklist_item(de_avulsa)
        uow.commit()
    with banco() as uow:
        do_marco = uow.schedule.live_items_of(OwnerKind.MILESTONE, marco_id("C06"))
        da_avulsa = uow.schedule.live_items_of(OwnerKind.TASK, tarefa.id)
        assert [(i.text, i.done, i.position, i.version) for i in do_marco] == [
            ("Do marco", False, 0, 1)
        ]
        assert [(i.text, i.owner_kind, i.owner_id) for i in da_avulsa] == [
            ("Da avulsa", OwnerKind.TASK, tarefa.id)
        ]
        assert uow.schedule.live_items_of(OwnerKind.TASK, marco_id("C06")) == []


def test_marcar_o_item_sobe_a_version_do_item_e_nunca_a_do_marco(banco):  # F-CRN-07, regra 4
    item = _item(marco_id("C06"))
    with banco() as uow:
        uow.schedule.add_checklist_item(item)
        uow.commit()
    with banco() as uow:
        uow.schedule.get_checklist_item(item.id).edit("Pedir orçamento", True)  # type: ignore[union-attr]
        uow.commit()
    with banco() as uow:
        assert uow.schedule.get_checklist_item(item.id).version == 2  # type: ignore[union-attr]
        marco = uow.schedule.get_milestone(marco_id("C06"))
        assert marco is not None
        assert marco.version == 1


def test_dois_itens_do_mesmo_marco_editados_ao_mesmo_tempo_nao_conflitam(banco):
    a, b = (
        _item(marco_id("C06"), texto="A", posicao=0),
        _item(marco_id("C06"), texto="B", posicao=1),
    )
    with banco() as uow:
        uow.schedule.add_checklist_item(a)
        uow.schedule.add_checklist_item(b)
        uow.commit()
    primeira, segunda = banco(NOIVO), banco(NOIVA)
    with primeira as x, segunda as y:
        x.schedule.get_checklist_item(a.id).edit("A", True)  # type: ignore[union-attr]
        y.schedule.get_checklist_item(b.id).edit("B", True)  # type: ignore[union-attr]
        x.commit()
        y.commit()


def test_o_mesmo_item_editado_ao_mesmo_tempo_conflita(banco):
    item = _item(marco_id("C06"))
    with banco() as uow:
        uow.schedule.add_checklist_item(item)
        uow.commit()
    primeira, segunda = banco(NOIVO), banco(NOIVA)
    with primeira as x, segunda as y:
        x.schedule.get_checklist_item(item.id).edit("Pedir orçamento", True)  # type: ignore[union-attr]
        y.schedule.get_checklist_item(item.id).edit("Outro texto", False)  # type: ignore[union-attr]
        x.commit()
        with pytest.raises(VersionConflict):
            y.commit()


def test_item_removido_some_da_leitura_e_a_ordem_e_por_posicao_e_id(banco, clock):
    dono = marco_id("C06")
    ids = [UUID(int=30), UUID(int=10), UUID(int=20), UUID(int=40)]
    itens = [
        ChecklistItem.of_owner(ids[0], OwnerKind.MILESTONE, dono, "terceiro", 1),
        ChecklistItem.of_owner(ids[1], OwnerKind.MILESTONE, dono, "empate b", 1),
        ChecklistItem.of_owner(ids[2], OwnerKind.MILESTONE, dono, "primeiro", 0),
        ChecklistItem.of_owner(ids[3], OwnerKind.MILESTONE, dono, "removido", 2),
    ]
    with banco() as uow:
        for item in itens:
            uow.schedule.add_checklist_item(item)
        uow.commit()
    with banco() as uow:
        uow.schedule.get_checklist_item(ids[3]).delete(clock.now(), NOIVO.user_id)  # type: ignore[union-attr]
        uow.commit()
    with banco() as uow:
        vivos = uow.schedule.live_items_of(OwnerKind.MILESTONE, dono)
        assert [i.text for i in vivos] == ["primeiro", "empate b", "terceiro"]
        assert uow.schedule.get_checklist_item(ids[3]) is None
        assert {i.id for i in uow.schedule.list_checklist_items()} == set(ids[:3])


def test_a_leitura_de_itens_inclui_os_de_dono_excluido_e_o_leitor_os_descarta(banco, clock):
    item = _item(marco_id("C06"))
    with banco() as uow:
        uow.schedule.add_checklist_item(item)
        uow.schedule.get_milestone(marco_id("C06")).delete(clock.now(), NOIVO.user_id)  # type: ignore[union-attr]
        uow.commit()
    with banco() as uow:
        assert [i.id for i in uow.schedule.list_checklist_items()] == [item.id]
        assert uow.schedule.get_milestone(marco_id("C06")) is None


def test_o_banco_recusa_item_sem_dono_com_dois_donos_texto_em_branco_e_posicao_negativa(banco):
    with banco() as uow:
        tarefa = _tarefa()
        uow.schedule.add_task(tarefa)
        uow.commit()
        sessao = uow.session
        base = {
            "created_at": datetime(2026, 11, 4, tzinfo=UTC),
            "updated_at": datetime(2026, 11, 4, tzinfo=UTC),
            "version": 1,
            "done": False,
            "text": "Item Exemplo",
            "position": 0,
        }
        invalidas = [
            {"milestone_id": None, "task_id": None},
            {"milestone_id": marco_id("C06"), "task_id": tarefa.id},
            {"milestone_id": marco_id("C06"), "task_id": None, "text": "   "},
            {"milestone_id": marco_id("C06"), "task_id": None, "position": -1},
        ]
        for extra in invalidas:
            with pytest.raises(IntegrityError), sessao.begin_nested():
                sessao.execute(checklist_items.insert().values(id=uuid4(), **{**base, **extra}))


def test_o_banco_recusa_estado_e_responsavel_desconhecidos_da_avulsa(banco):
    with banco() as uow:
        agora = datetime(2026, 11, 4, tzinfo=UTC)
        base = {"created_at": agora, "updated_at": agora, "version": 1}
        for extra in (
            {"state": "Concluído", "responsible": "Noiva"},  # o masculino é do marco
            {"state": "A fazer", "responsible": "Ninguém"},
        ):
            with pytest.raises(IntegrityError), uow.session.begin_nested():
                uow.session.execute(
                    schedule_tasks.insert().values(
                        id=uuid4(), title="Tarefa Exemplo", **base, **extra
                    )
                )


def test_o_banco_nao_deixa_apagar_o_dono_que_tem_itens(banco):
    with banco() as uow:
        uow.schedule.add_checklist_item(_item(marco_id("C06")))
        uow.commit()
    with banco() as uow, pytest.raises(IntegrityError):
        uow.session.execute(milestones.delete().where(milestones.c.id == marco_id("C06")))


class _Mapa:
    def categories(self, actor):
        return {}


class _SemData:
    def wedding_date(self, actor):
        return WeddingDate(defined=False, exact=None)


def _consultas_de_leitura(banco, tabela: str, clock) -> int:
    """Quantos SELECT tocam `tabela` numa leitura completa do cronograma."""
    contagem = SimpleNamespace(n=0)

    @event.listens_for(banco.engine, "before_cursor_execute")
    def conta(conn, cursor, statement, parameters, context, executemany):
        if statement.lstrip().upper().startswith("SELECT") and f"FROM {tabela}" in statement:
            contagem.n += 1

    reader = ScheduleReader(_Mapa(), _SemData(), clock)  # type: ignore[arg-type]
    with banco() as uow:
        reader.read(uow.schedule, NOIVO)
    event.remove(banco.engine, "before_cursor_execute", conta)
    return contagem.n


@pytest.mark.parametrize("tabela", ["schedule_tasks", "checklist_items"])
def test_a_leitura_carrega_avulsas_e_itens_em_uma_consulta_cada_sem_n_mais_1(banco, clock, tabela):
    outras = [_tarefa(title=f"Avulsa {n}") for n in range(5)]
    with banco() as uow:
        for tarefa in outras:
            uow.schedule.add_task(tarefa)
        uow.commit()
    with banco() as uow:
        for tarefa in outras:
            uow.schedule.add_checklist_item(_item(tarefa.id, OwnerKind.TASK))
        for codigo in ("C01", "C02", "C03"):
            uow.schedule.add_checklist_item(_item(marco_id(codigo)))
        uow.commit()
    assert _consultas_de_leitura(banco, tabela, clock) == 1


def test_o_mapeamento_nao_regrava_o_dono_so_por_tocar_nos_itens(banco):
    item = _item(marco_id("C06"))
    with banco() as uow:
        uow.schedule.add_checklist_item(item)
        uow.commit()
    with banco() as uow:
        antes = uow.session.execute(
            select(milestones.c.updated_at, milestones.c.version).where(
                milestones.c.id == marco_id("C06")
            )
        ).one()
        uow.schedule.get_checklist_item(item.id).edit("Pedir orçamento", True)  # type: ignore[union-attr]
        uow.commit()
        depois = uow.session.execute(
            select(milestones.c.updated_at, milestones.c.version).where(
                milestones.c.id == marco_id("C06")
            )
        ).one()
    assert tuple(antes) == tuple(depois)
