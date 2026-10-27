from datetime import UTC, datetime, timedelta, timezone

import pytest
from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    Table,
    text,
)
from sqlalchemy.exc import IntegrityError, StatementError

from wedding.platform.db.engine import create_db_engine
from wedding.platform.db.metadata import NAMING_CONVENTION, metadata
from wedding.platform.db.types import UtcDateTime

SAO_PAULO = timezone(timedelta(hours=-3))


def test_metadata_compartilhado_usa_a_convencao_de_nomes():
    assert metadata.naming_convention == NAMING_CONVENTION


def test_constraints_recebem_nomes_previsiveis():
    meta = MetaData(naming_convention=NAMING_CONVENTION)
    pais = Table("pais", meta, Column("id", Integer, primary_key=True))
    filhos = Table(
        "filhos",
        meta,
        Column("id", Integer, primary_key=True),
        Column("pai_id", ForeignKey("pais.id")),
        Column("codigo", Integer, unique=True),
        Column("valor", Integer),
        CheckConstraint("valor >= 0", name="valor_nao_negativo"),
    )
    Index(None, filhos.c.valor)
    nomes = {c.name for t in (pais, filhos) for c in t.constraints} | {
        i.name for i in filhos.indexes
    }
    assert nomes == {
        "pk_pais",
        "pk_filhos",
        "fk_filhos_pai_id_pais",
        "uq_filhos_codigo",
        "ck_filhos_valor_nao_negativo",
        "ix_filhos_valor",
    }


def test_engine_liga_chaves_estrangeiras_wal_e_busy_timeout(tmp_path):
    engine = create_db_engine(f"sqlite:///{tmp_path / 'teste.db'}")
    with engine.connect() as conn:
        assert conn.execute(text("PRAGMA foreign_keys")).scalar() == 1
        assert conn.execute(text("PRAGMA journal_mode")).scalar() == "wal"
        assert conn.execute(text("PRAGMA busy_timeout")).scalar() == 5000


def test_engine_barra_chave_estrangeira_orfa(tmp_path):
    engine = create_db_engine(f"sqlite:///{tmp_path / 'teste.db'}")
    meta = MetaData(naming_convention=NAMING_CONVENTION)
    Table("pais", meta, Column("id", Integer, primary_key=True))
    Table(
        "filhos",
        meta,
        Column("id", Integer, primary_key=True),
        Column("pai_id", ForeignKey("pais.id")),
    )
    meta.create_all(engine)
    with pytest.raises(IntegrityError), engine.begin() as conn:
        conn.execute(text("INSERT INTO filhos (id, pai_id) VALUES (1, 999)"))


def test_engine_cria_a_pasta_do_arquivo_sqlite(tmp_path):
    arquivo = tmp_path / "data" / "fundo" / "altare.db"
    create_db_engine(f"sqlite:///{arquivo}").connect().close()
    assert arquivo.exists()


def _tabela_com_instante(engine):
    meta = MetaData()
    tabela = Table(
        "eventos", meta, Column("id", Integer, primary_key=True), Column("quando", UtcDateTime)
    )
    meta.create_all(engine)
    return tabela


def test_instante_com_fuso_e_gravado_em_utc_e_lido_com_fuso(tmp_path):
    engine = create_db_engine(f"sqlite:///{tmp_path / 'teste.db'}")
    eventos = _tabela_com_instante(engine)
    local = datetime(2026, 10, 27, 12, 0, tzinfo=SAO_PAULO)
    with engine.begin() as conn:
        conn.execute(eventos.insert().values(id=1, quando=local))
        bruto = conn.execute(text("SELECT quando FROM eventos")).scalar()
        lido = conn.execute(eventos.select()).one().quando
    assert bruto is not None
    assert bruto.startswith("2026-10-27 15:00:00")
    assert lido == local
    assert lido.tzinfo is UTC


def test_instante_nulo_continua_nulo(tmp_path):
    engine = create_db_engine(f"sqlite:///{tmp_path / 'teste.db'}")
    eventos = _tabela_com_instante(engine)
    with engine.begin() as conn:
        conn.execute(eventos.insert().values(id=1, quando=None))
        assert conn.execute(eventos.select()).one().quando is None


def test_instante_sem_fuso_e_recusado(tmp_path):
    engine = create_db_engine(f"sqlite:///{tmp_path / 'teste.db'}")
    eventos = _tabela_com_instante(engine)
    with pytest.raises(StatementError, match="fuso"), engine.begin() as conn:
        conn.execute(eventos.insert().values(id=1, quando=datetime(2026, 10, 27, 12, 0)))
