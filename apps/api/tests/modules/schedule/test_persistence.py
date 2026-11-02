"""O cronograma contra o SQLite migrado de verdade: mapeamento, leitura e bloqueio otimista."""

from datetime import date
from pathlib import Path
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from tests.conftest import FixedClock
from tests.modules.schedule.catalog import MARCOS, marco_id

from wedding.modules.schedule.domain.entities import Milestone, MilestoneChange
from wedding.modules.schedule.domain.values import ManualState
from wedding.modules.schedule.infrastructure.mapping import start_mappers
from wedding.modules.schedule.infrastructure.tables import milestone_changes, milestones
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

    yield uow
    engine.dispose()


def test_le_as_fases_os_marcos_e_as_dependencias_da_semente(banco):
    with banco() as uow:
        fases = [(f.position, f.title) for f in uow.schedule.list_phases()]
        versoes = {m.version for m in uow.schedule.list_milestones()}
        total_de_marcos = len(uow.schedule.list_milestones())
        dependencias = uow.schedule.dependencies()
    assert sorted(fases)[0] == (0, "Marco Zero")
    assert len(fases) == 5
    assert total_de_marcos == len(MARCOS) == 29
    assert len(dependencias) == 31
    assert versoes == {1}


def test_marco_lido_traz_os_campos_do_dominio(banco):
    with banco() as uow:
        marco = uow.schedule.get_milestone(marco_id("C11"))
        assert marco is not None
        assert marco.title == "Fechar a Música"
        assert marco.responsible is ProfileKind.AMBOS
        assert marco.category_id is not None
        assert (marco.note, marco.target_date, marco.manual_state) == (None, None, None)
        assert uow.schedule.get_milestone(uuid4()) is None


def test_editar_persiste_sobe_a_version_e_grava_o_autor_da_sessao(banco):
    with banco(NOIVA) as uow:
        marco = uow.schedule.get_milestone(marco_id("C06"))
        assert marco is not None
        marco.edit(ProfileKind.NOIVA, "nota", date(2027, 1, 15))
        marco.set_manual_state(ManualState.IN_PROGRESS)
        uow.commit()
    with banco() as uow:
        lido = uow.schedule.get_milestone(marco_id("C06"))
        assert lido is not None
        assert (lido.responsible, lido.note, lido.target_date, lido.manual_state) == (
            ProfileKind.NOIVA,
            "nota",
            date(2027, 1, 15),
            ManualState.IN_PROGRESS,
        )
        assert lido.version == 2
        linha = uow.session.execute(
            select(milestones.c.updated_by, milestones.c.window_start_before).where(
                milestones.c.id == marco_id("C06")
            )
        ).one()
    assert linha.updated_by == NOIVA.user_id
    # A janela sugerida sobrevive à edição: o mapeamento não a toca.
    assert linha.window_start_before == 14


def test_duas_edicoes_sobre_a_mesma_version_a_segunda_vira_conflito(banco):
    primeira, segunda = banco(NOIVO), banco(NOIVA)
    with primeira as a, segunda as b:
        x = a.schedule.get_milestone(marco_id("C01"))
        y = b.schedule.get_milestone(marco_id("C01"))
        assert x is not None
        assert y is not None
        x.edit(ProfileKind.NOIVO, None, None)
        y.edit(ProfileKind.NOIVA, None, None)
        a.commit()
        with pytest.raises(VersionConflict):
            b.commit()


def test_o_historico_grava_antes_depois_perfil_e_ignorou(banco):
    with banco(NOIVA) as uow:
        uow.schedule.add_change(
            MilestoneChange(
                id=uuid4(),
                milestone_id=marco_id("C03"),
                state_before=None,
                state_after=ManualState.DONE,
                ignored_block=True,
                profile=ProfileKind.NOIVA,
            )
        )
        uow.commit()
    with banco() as uow:
        linha = uow.session.execute(select(milestone_changes)).one()
    assert (linha.state_before, linha.state_after) == (None, ManualState.DONE)
    assert (linha.ignored_block, linha.profile) == (True, ProfileKind.NOIVA)
    assert linha.created_by == NOIVA.user_id


def test_o_banco_recusa_historico_sem_mudanca_ou_de_perfil_ambos(banco):
    def tentar(**campos):
        with banco() as uow:
            uow.schedule.add_change(
                MilestoneChange(
                    id=uuid4(),
                    milestone_id=marco_id("C03"),
                    state_before=campos.get("antes"),
                    state_after=campos.get("depois"),
                    ignored_block=False,
                    profile=campos.get("perfil", ProfileKind.NOIVO),
                )
            )
            uow.commit()

    with pytest.raises(IntegrityError):
        tentar(antes=ManualState.DONE, depois=ManualState.DONE)
    with pytest.raises(IntegrityError):
        tentar(antes=None, depois=None)
    with pytest.raises(IntegrityError):
        tentar(depois=ManualState.DONE, perfil=ProfileKind.AMBOS)


def test_marco_excluido_e_o_vinculo_dele_somem_da_leitura(banco):
    with banco() as uow:
        uow.session.execute(
            text("UPDATE milestones SET deleted_at = '2026-10-27' WHERE id = :id"),
            {"id": marco_id("C06").hex},
        )
        uow.commit()
    with banco() as uow:
        ids = {m.id for m in uow.schedule.list_milestones()}
        vinculos = uow.schedule.dependencies()
        assert uow.schedule.get_milestone(marco_id("C06")) is None
    assert marco_id("C06") not in ids
    assert len(ids) == 28
    assert all(marco_id("C06") not in (d.milestone_id, d.depends_on_id) for d in vinculos)
    # C06 depende de C05 (1) e é dependência de C07..C11, C14, C15, C20, C21, C24 (10).
    assert len(vinculos) == 31 - 11


def test_o_banco_recusa_estado_de_marco_desconhecido_e_janela_incoerente(banco):
    with banco() as uow:
        for sql in (
            "UPDATE milestones SET manual_state = 'Atrasado' WHERE id = :id",
            "UPDATE milestones SET window_start_before = 1, window_end_before = 4,"
            " window_unit = 'meses' WHERE id = :id",
            "UPDATE milestones SET window_unit = NULL WHERE id = :id AND window_unit IS NOT NULL",
            "UPDATE milestones SET responsible = 'Todos' WHERE id = :id",
        ):
            with pytest.raises(IntegrityError):
                uow.session.execute(text(sql), {"id": marco_id("C06").hex})
            uow.session.rollback()


def test_entidade_nova_de_marco_nasce_com_a_version_um(banco):
    with banco() as uow:
        fase = uow.schedule.list_phases()[0]
        novo_id = uuid4()
        uow.session.add(Milestone(id=novo_id, phase_id=fase.id, title="Marco Exemplo", position=99))
        uow.commit()
    with banco() as uow:
        lido = uow.schedule.get_milestone(novo_id)
        assert lido is not None
        assert lido.version == 1
        assert lido.responsible is ProfileKind.AMBOS
