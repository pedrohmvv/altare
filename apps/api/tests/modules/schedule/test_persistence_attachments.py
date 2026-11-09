"""Os anexos (F-CRN-08) contra o SQLite migrado de verdade: mapeamento, o instante e o autor do
histórico básico, a `version` própria, o dono que nunca é tocado, a exclusão lógica e a leitura em
uma consulta só."""

from datetime import timedelta
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import event, select, text
from sqlalchemy.exc import IntegrityError
from tests.conftest import FixedClock
from tests.modules.schedule.catalog import marco_id

from wedding.modules.schedule.application.ports import WeddingDate
from wedding.modules.schedule.application.schedule_map import ScheduleReader
from wedding.modules.schedule.domain.attachments import AttachedFile, Attachment, AttachmentKind
from wedding.modules.schedule.domain.entities import Milestone, Task
from wedding.modules.schedule.domain.values import OwnerKind
from wedding.modules.schedule.infrastructure.mapping import start_mappers
from wedding.modules.schedule.infrastructure.tables import attachments, milestones
from wedding.modules.schedule.infrastructure.uow import SqlScheduleUnitOfWork
from wedding.platform.bootstrap.tables import load_tables
from wedding.platform.db.engine import create_db_engine, create_session_factory
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.errors import VersionConflict
from wedding.shared_kernel.profile import ProfileKind

API_DIR = Path(__file__).parents[3]
NOIVO = Actor(user_id=uuid4(), profile=ProfileKind.NOIVO)
NOIVA = Actor(user_id=uuid4(), profile=ProfileKind.NOIVA)
ARQUIVO = uuid4()


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
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO file_assets (id, created_at, updated_at, version, original_name,"
                " content_type, size_bytes, sha256) VALUES (:id, '2026-11-04', '2026-11-04', 1,"
                " 'contrato-exemplo.pdf', 'application/pdf', 2048, 'abc')"
            ),
            {"id": ARQUIVO.hex},
        )

    def uow(ator=NOIVO):
        return SqlScheduleUnitOfWork(sessions, clock, ator)

    uow.engine = engine  # type: ignore[attr-defined]
    yield uow
    engine.dispose()


def _link(dono=None, tipo=OwnerKind.MILESTONE, **campos) -> Attachment:
    padrao = {
        "id": uuid4(),
        "owner_kind": tipo,
        "owner_id": dono or marco_id("C06"),
        "profile": ProfileKind.NOIVO,
        "url": "https://exemplo.com/mesa",
        "title": "Mesa",
        "comment": None,
    }
    return Attachment.new_link(**{**padrao, **campos})


def _arquivo(dono=None, tipo=OwnerKind.MILESTONE, **campos) -> Attachment:
    padrao = {
        "id": uuid4(),
        "owner_kind": tipo,
        "owner_id": dono or marco_id("C06"),
        "profile": ProfileKind.NOIVA,
        "file": AttachedFile(ARQUIVO, "contrato-exemplo.pdf", "application/pdf", 2048),
        "title": None,
        "comment": "Versão final",
    }
    return Attachment.new_file(**{**padrao, **campos})


def test_o_link_vai_e_volta_com_todos_os_campos_e_o_historico_basico(banco, clock):
    anexo = _link()
    with banco(NOIVO) as uow:
        uow.schedule.add_attachment(anexo)
        uow.commit()
    with banco(NOIVA) as uow:
        lido = uow.schedule.get_attachment(anexo.id)
        assert lido is not None
        assert (lido.owner_kind, lido.owner_id, lido.kind) == (
            OwnerKind.MILESTONE,
            marco_id("C06"),
            AttachmentKind.LINK,
        )
        assert (lido.profile, lido.url, lido.title, lido.comment) == (
            ProfileKind.NOIVO,
            "https://exemplo.com/mesa",
            "Mesa",
            None,
        )
        assert (lido.file, lido.domain, lido.version) == (None, "exemplo.com", 1)
        assert lido.created_at == clock.now()
        assert lido.created_by == NOIVO.user_id
        assert lido.deleted_at is None


def test_o_arquivo_guarda_a_copia_de_nome_tipo_e_tamanho(banco):
    anexo = _arquivo(tipo=OwnerKind.TASK, dono=uuid4())
    with banco() as uow:
        uow.schedule.add_attachment(anexo)
        uow.commit()
    with banco() as uow:
        lido = uow.schedule.get_attachment(anexo.id)
        assert lido is not None
        assert lido.owner_kind is OwnerKind.TASK
        assert lido.file == AttachedFile(ARQUIVO, "contrato-exemplo.pdf", "application/pdf", 2048)
        assert (lido.url, lido.domain, lido.comment) == (None, None, "Versão final")


def test_o_tipo_do_dono_vai_para_a_coluna_owner_type(banco):
    anexo = _link(tipo=OwnerKind.TASK, dono=uuid4())
    with banco() as uow:
        uow.schedule.add_attachment(anexo)
        uow.commit()
    with banco.engine.connect() as conn:  # type: ignore[attr-defined]
        assert conn.execute(select(attachments.c.owner_type)).scalars().all() == ["tasks"]


def test_o_arquivo_que_nao_existe_no_files_e_recusado_pela_chave_estrangeira(banco):
    anexo = _arquivo(file=AttachedFile(uuid4(), "x.pdf", "application/pdf", 1))
    with banco() as uow:
        uow.schedule.add_attachment(anexo)
        with pytest.raises(IntegrityError):
            uow.commit()


def test_remover_grava_quem_e_quando_sobe_a_version_e_some_das_leituras(banco, clock):
    anexo = _link()
    with banco(NOIVO) as uow:
        uow.schedule.add_attachment(anexo)
        uow.commit()
    clock.advance(minutes=3)
    with banco(NOIVO) as uow:
        lido = uow.schedule.get_attachment(anexo.id)
        assert lido is not None
        lido.remove(NOIVO.profile, NOIVO.user_id, clock.now())
        uow.commit()
    with banco() as uow:
        assert uow.schedule.get_attachment(anexo.id) is None
        assert uow.schedule.list_attachments() == []
        linha = uow.session.execute(select(attachments)).one()
    assert linha.deleted_at == clock.now()
    assert linha.deleted_by == NOIVO.user_id
    assert linha.version == 2


def test_a_lista_traz_so_os_vivos_na_ordem_em_que_foram_anexados(banco, clock):
    primeiro, segundo, removido = _link(url="https://a.exemplo.com"), _arquivo(), _link()
    for anexo in (primeiro, segundo, removido):
        with banco() as uow:
            uow.schedule.add_attachment(anexo)
            uow.commit()
        clock.advance(seconds=1)
    with banco() as uow:
        uow.schedule.get_attachment(removido.id).remove(  # type: ignore[union-attr]
            NOIVO.profile, NOIVO.user_id, clock.now()
        )
        uow.commit()
    with banco() as uow:
        assert [a.id for a in uow.schedule.list_attachments()] == [primeiro.id, segundo.id]


def test_anexar_nao_regrava_o_dono(banco):
    with banco() as uow:
        antes = uow.session.execute(
            select(milestones.c.updated_at, milestones.c.version).where(
                milestones.c.id == marco_id("C06")
            )
        ).one()
    with banco(NOIVA) as uow:
        uow.schedule.add_attachment(_link(profile=ProfileKind.NOIVA))
        uow.commit()
    with banco() as uow:
        depois = uow.session.execute(
            select(milestones.c.updated_at, milestones.c.version).where(
                milestones.c.id == marco_id("C06")
            )
        ).one()
    assert depois == antes


def test_o_anexo_nao_exige_que_o_dono_exista_no_banco_mas_o_leitor_so_mostra_donos_vivos(banco):
    """Sem chave estrangeira no dono: a integridade é do caso de uso e do leitor."""
    with banco() as uow:
        uow.schedule.add_attachment(_link(dono=uuid4()))
        uow.commit()
        assert len(uow.schedule.list_attachments()) == 1


class _Mapa:
    def categories(self, actor):
        return {}


class _SemData:
    def wedding_date(self, actor):
        return WeddingDate(defined=False, exact=None)


def _leitor(clock) -> ScheduleReader:
    return ScheduleReader(_Mapa(), _SemData(), clock)  # type: ignore[arg-type]


def _marco(cronograma, codigo: str):
    return next(m for f in cronograma.phases for m in f.milestones if m.id == marco_id(codigo))


def test_a_leitura_so_mostra_anexos_de_donos_vivos_e_o_dono_restaurado_os_traz_de_volta(
    banco, clock
):
    leitor = _leitor(clock)
    anexo = _link()
    with banco() as uow:
        uow.schedule.add_attachment(anexo)
        uow.commit()
    with banco() as uow:
        assert [a.id for a in _marco(leitor.read(uow.schedule, NOIVO), "C06").attachments] == [
            anexo.id
        ]
    with banco() as uow:
        dono = uow.schedule.get_milestone(marco_id("C06"))
        assert isinstance(dono, Milestone)
        dono.delete(clock.now(), NOIVO.user_id)
        uow.commit()
    with banco() as uow:
        cronograma = leitor.read(uow.schedule, NOIVO)
        assert all(m.id != marco_id("C06") for f in cronograma.phases for m in f.milestones)
        assert uow.schedule.get_attachment(anexo.id) is not None  # a linha segue viva e guardada
    with banco() as uow:
        uow.schedule.get_milestone(marco_id("C06"), include_deleted=True).restore(0)  # type: ignore[union-attr]
        uow.commit()
    with banco() as uow:
        assert [a.id for a in _marco(leitor.read(uow.schedule, NOIVO), "C06").attachments] == [
            anexo.id
        ]


def test_o_anexo_de_avulsa_aparece_na_avulsa_e_nao_nos_marcos(banco, clock):
    tarefa = Task(id=uuid4(), title="Pesquisar Alianças", responsible=ProfileKind.NOIVA)
    with banco() as uow:
        uow.schedule.add_task(tarefa)
        uow.commit()
    with banco() as uow:
        uow.schedule.add_attachment(_link(tarefa.id, OwnerKind.TASK))
        uow.commit()
    with banco() as uow:
        cronograma = _leitor(clock).read(uow.schedule, NOIVO)
    assert len(cronograma.tasks[0].attachments) == 1
    assert all(not m.attachments for f in cronograma.phases for m in f.milestones)


def test_can_remove_vem_do_perfil_de_quem_le(banco, clock):
    with banco() as uow:
        uow.schedule.add_attachment(_link(profile=ProfileKind.NOIVA))
        uow.commit()
    with banco() as uow:
        leitor = _leitor(clock)
        assert _marco(leitor.read(uow.schedule, NOIVA), "C06").attachments[0].can_remove is True
        assert _marco(leitor.read(uow.schedule, NOIVO), "C06").attachments[0].can_remove is False


def test_a_leitura_carrega_os_anexos_de_todos_os_donos_em_uma_consulta(banco, clock):
    """Nada de N+1: seis donos com anexo, uma consulta à tabela."""
    tarefas = [
        Task(id=uuid4(), title=f"Avulsa {n}", responsible=ProfileKind.NOIVA) for n in range(3)
    ]
    with banco() as uow:
        for tarefa in tarefas:
            uow.schedule.add_task(tarefa)
        uow.commit()
    with banco() as uow:
        for tarefa in tarefas:
            uow.schedule.add_attachment(_link(tarefa.id, OwnerKind.TASK))
        for codigo in ("C01", "C02", "C03"):
            uow.schedule.add_attachment(_arquivo(marco_id(codigo)))
        uow.commit()
    contagem = SimpleNamespace(n=0)

    @event.listens_for(banco.engine, "before_cursor_execute")  # type: ignore[attr-defined]
    def conta(conn, cursor, statement, parameters, context, executemany):
        if statement.lstrip().upper().startswith("SELECT") and "FROM attachments" in statement:
            contagem.n += 1

    with banco() as uow:
        _leitor(clock).read(uow.schedule, NOIVO)
    event.remove(banco.engine, "before_cursor_execute", conta)  # type: ignore[attr-defined]
    assert contagem.n == 1


def test_o_instante_do_anexo_vem_do_historico_basico(banco, clock):
    with banco() as uow:
        uow.schedule.add_attachment(_link())
        uow.commit()
    clock.advance(hours=2)
    with banco() as uow:
        anexo = _marco(_leitor(clock).read(uow.schedule, NOIVO), "C06").attachments[0]
    assert anexo.added_at == clock.now() - timedelta(hours=2)
    assert isinstance(anexo.id, UUID)


def test_a_linha_antiga_com_url_que_o_parse_atual_recusa_le_sem_derrubar_o_cronograma(banco, clock):
    """Uma regra mais apertada no futuro não pode quebrar o `GET /schedule` por causa de uma linha
    já gravada: o domínio mostra o que der."""
    with banco.engine.begin() as conn:  # type: ignore[attr-defined]
        conn.execute(
            text(
                "INSERT INTO attachments (id, created_at, updated_at, version, owner_type,"
                " owner_id, kind, profile, url) VALUES (:id, '2026-11-04', '2026-11-04', 1,"
                " 'milestones', :dono, 'link', 'Noiva', :url)"
            ),
            {
                "id": uuid4().hex,
                "dono": marco_id("C06").hex,
                "url": "https://banco-exemplo.com\\.gov.br/x",
            },
        )
    with banco() as uow:
        (anexo,) = _marco(_leitor(clock).read(uow.schedule, NOIVO), "C06").attachments
    assert anexo.url == "https://banco-exemplo.com\\.gov.br/x"
    assert anexo.domain == "banco-exemplo.com"


def test_duas_remocoes_simultaneas_disputam_a_version_e_a_segunda_da_409(banco, clock):
    """O `DELETE /attachments/{id}` não recebe `version`, mas o mapeamento a confere: quem perde a
    corrida vira `VersionConflict` (409)."""
    anexo = _link()
    with banco(NOIVO) as uow:
        uow.schedule.add_attachment(anexo)
        uow.commit()
    primeiro, segundo = banco(NOIVO), banco(NOIVO)
    with primeiro as uow_a, segundo as uow_b:
        a = uow_a.schedule.get_attachment(anexo.id)
        b = uow_b.schedule.get_attachment(anexo.id)
        assert a is not None
        assert b is not None
        a.remove(NOIVO.profile, NOIVO.user_id, clock.now())
        b.remove(NOIVO.profile, NOIVO.user_id, clock.now())
        uow_a.commit()
        with pytest.raises(VersionConflict):
            uow_b.commit()
