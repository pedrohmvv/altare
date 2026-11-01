from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import insert, select, text
from sqlalchemy.exc import IntegrityError

from wedding.modules.wedding.application.commands.update_baseline_field import (
    UpdateBaselineField,
    UpdateBaselineFieldCommand,
)
from wedding.modules.wedding.application.queries.get_baseline import GetBaseline
from wedding.modules.wedding.application.queries.list_baseline_changes import ListBaselineChanges
from wedding.modules.wedding.domain.value_objects import (
    BaselineKey,
    CeilingValue,
    CeremonyKind,
    CeremonyValue,
    DateKind,
    DateValue,
    DefinitionStatus,
    MonthYear,
    TextValue,
)
from wedding.modules.wedding.infrastructure.mapping import start_mappers
from wedding.modules.wedding.infrastructure.tables import baseline_changes, baseline_fields
from wedding.modules.wedding.infrastructure.uow import SqlWeddingUnitOfWork
from wedding.platform.bootstrap.tables import load_tables
from wedding.platform.db.engine import create_db_engine, create_session_factory
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.errors import VersionConflict
from wedding.shared_kernel.ids import UuidGenerator
from wedding.shared_kernel.profile import ProfileKind

API_DIR = Path(__file__).parents[3]
NOIVO = Actor(user_id=uuid4(), profile=ProfileKind.NOIVO)
NOIVA = Actor(user_id=uuid4(), profile=ProfileKind.NOIVA)


class _SemLista:
    """Estas provas são do banco das Definições Base, não da lista: a contagem aqui é zero."""

    def total_nominal(self, actor: Actor) -> int:
        return 0


@pytest.fixture
def banco(tmp_path, clock):
    """O banco como a migration o deixa, semente incluída: é o que o app encontra em produção."""
    load_tables()
    start_mappers()
    url = f"sqlite:///{tmp_path / 'wedding.db'}"
    config = Config(str(API_DIR / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", url)
    command.upgrade(config, "head")
    engine = create_db_engine(url)
    factory = create_session_factory(engine)

    def uow(ator: Actor = NOIVO) -> SqlWeddingUnitOfWork:
        return SqlWeddingUnitOfWork(factory, clock, ator)

    yield SimpleNamespace(
        engine=engine,
        clock=clock,
        uow=uow,
        get=GetBaseline(uow, _SemLista()),
        update=UpdateBaselineField(uow, UuidGenerator(), _SemLista()),
        changes=ListBaselineChanges(uow),
    )
    engine.dispose()


def _cmd(key, value, status=DefinitionStatus.DEFINED, version=1, note=None):
    return UpdateBaselineFieldCommand(key, value, status, note, version)


def test_a_migration_semeia_os_seis_campos_vazios_e_em_definicao(banco):
    quadro = banco.get.execute(NOIVO)
    for campo in (
        quadro.date,
        quadro.city,
        quadro.format,
        quadro.size,
        quadro.ceiling,
        quadro.ceremony,
    ):
        assert campo.value is None
        assert campo.status is DefinitionStatus.IN_DEFINITION
        assert campo.version == 1
    with banco.engine.connect() as conn:
        assert conn.execute(select(baseline_fields.c.field_key)).scalars().all().__len__() == 6


def test_valor_gravado_volta_tipado_e_a_versao_sobe(banco):
    banco.update.execute(_cmd(BaselineKey.CEILING, CeilingValue(2_800_000), note="teto"), NOIVA)
    quadro = banco.get.execute(NOIVO)
    assert quadro.ceiling.value == CeilingValue(2_800_000)
    assert quadro.ceiling.note == "teto"
    assert quadro.ceiling.version == 2
    assert quadro.city.version == 1


@pytest.mark.parametrize(
    ("chave", "valor"),
    [
        (BaselineKey.CITY, TextValue("Cidade Exemplo")),
        (
            BaselineKey.DATE,
            DateValue(
                kind=DateKind.WINDOW,
                window_start=MonthYear(2027, 3),
                window_end=MonthYear(2027, 5),
                label="outono",
            ),
        ),
        (BaselineKey.DATE, DateValue(kind=DateKind.EXACT, exact=date(2027, 5, 1))),
        (
            BaselineKey.CEREMONY,
            CeremonyValue(frozenset({CeremonyKind.CIVIL, CeremonyKind.SYMBOLIC}), "detalhe"),
        ),
    ],
)
def test_cada_tipo_de_valor_sobrevive_ao_json_do_banco(banco, chave, valor):
    banco.update.execute(_cmd(chave, valor), NOIVO)
    campo = getattr(banco.get.execute(NOIVO), chave.value)
    assert campo.value == valor


def test_autoria_e_instante_vem_do_historico_basico(banco, clock):
    clock.advance(minutes=5)
    banco.update.execute(_cmd(BaselineKey.CITY, TextValue("Cidade Exemplo")), NOIVA)
    with banco.engine.connect() as conn:
        linha = conn.execute(
            select(baseline_fields.c.updated_by, baseline_fields.c.updated_at).where(
                baseline_fields.c.field_key == BaselineKey.CITY
            )
        ).one()
    assert linha.updated_by == NOIVA.user_id
    assert linha.updated_at == datetime(2026, 10, 27, 12, 5, tzinfo=UTC)


def test_dois_editando_o_mesmo_campo_o_segundo_recebe_conflito(banco):
    banco.update.execute(_cmd(BaselineKey.CITY, TextValue("Cidade Exemplo")), NOIVO)
    with pytest.raises(VersionConflict):
        banco.update.execute(_cmd(BaselineKey.CITY, TextValue("Outra Exemplo"), version=1), NOIVA)
    assert banco.get.execute(NOIVO).city.value == TextValue("Cidade Exemplo")


def test_conflito_de_transacoes_concorrentes_vira_conflito_de_versao(banco):
    """Dois pedidos passam pela checagem de versão ao mesmo tempo: o bloqueio otimista do banco
    pega o segundo no commit."""
    with banco.uow(NOIVO) as primeiro, banco.uow(NOIVA) as segundo:
        campo_a = primeiro.baseline.get(BaselineKey.CITY)
        campo_b = segundo.baseline.get(BaselineKey.CITY)
        assert campo_a is not None
        assert campo_b is not None
        campo_a.update(TextValue("A Exemplo"), DefinitionStatus.DEFINED, None)
        campo_b.update(TextValue("B Exemplo"), DefinitionStatus.DEFINED, None)
        primeiro.commit()
        with pytest.raises(VersionConflict):
            segundo.commit()


def test_historico_guarda_antes_depois_perfil_e_instante(banco, clock):
    banco.update.execute(_cmd(BaselineKey.CITY, TextValue("A Exemplo")), NOIVO)
    clock.advance(hours=1)
    banco.update.execute(_cmd(BaselineKey.CITY, TextValue("B Exemplo"), version=2), NOIVA)

    recente, antiga = banco.changes.execute(NOIVO)
    assert recente.before.value == TextValue("A Exemplo")
    assert recente.after.value == TextValue("B Exemplo")
    assert recente.profile is ProfileKind.NOIVA
    assert antiga.before.value is None
    assert antiga.profile is ProfileKind.NOIVO
    assert recente.changed_at - antiga.changed_at == timedelta(hours=1)


def test_historico_respeita_o_limite(banco):
    for versao, cidade in enumerate(["A Exemplo", "B Exemplo", "C Exemplo"], start=1):
        banco.update.execute(_cmd(BaselineKey.CITY, TextValue(cidade), version=versao), NOIVO)
    assert len(banco.changes.execute(NOIVO, limit=2)) == 2


def test_sem_alteracao_nada_e_gravado_nem_a_versao_sobe(banco):
    banco.update.execute(_cmd(BaselineKey.CITY, TextValue("A Exemplo")), NOIVO)
    banco.update.execute(_cmd(BaselineKey.CITY, TextValue("A Exemplo"), version=2), NOIVO)
    assert banco.get.execute(NOIVO).city.version == 2
    with banco.engine.connect() as conn:
        assert conn.execute(select(baseline_changes.c.id)).all().__len__() == 1


def test_campo_vazio_fica_nulo_no_banco_e_nao_como_json_null(banco):
    with banco.engine.connect() as conn:
        assert (
            conn.execute(text("SELECT COUNT(*) FROM baseline_fields WHERE value IS NULL")).scalar()
            == 6
        )


def test_cada_chave_existe_uma_so_vez(banco):
    with banco.engine.begin() as conn, pytest.raises(IntegrityError):
        conn.execute(
            insert(baseline_fields).values(
                id=uuid4(),
                created_at=banco.clock.now(),
                updated_at=banco.clock.now(),
                version=1,
                field_key=BaselineKey.CITY,
                status=DefinitionStatus.IN_DEFINITION,
            )
        )


def test_o_banco_recusa_status_fora_da_lista(banco):
    with banco.engine.begin() as conn, pytest.raises(IntegrityError):
        conn.execute(text("UPDATE baseline_fields SET status = 'Quase' WHERE field_key = 'city'"))


def test_o_banco_recusa_definido_sem_valor(banco):
    with banco.engine.begin() as conn, pytest.raises(IntegrityError):
        conn.execute(
            text("UPDATE baseline_fields SET status = 'Definido' WHERE field_key = 'city'")
        )
