from dataclasses import dataclass
from types import SimpleNamespace
from uuid import UUID

import pytest
from sqlalchemy import Column, MetaData, String, Table
from sqlalchemy.orm import registry

from wedding.platform.db.audit import audit_columns
from wedding.platform.db.engine import create_db_engine, create_session_factory
from wedding.platform.db.metadata import NAMING_CONVENTION


@pytest.fixture
def banco(tmp_path):
    """Tabela e entidade descartáveis, com o histórico básico, num SQLite temporário."""

    @dataclass
    class Coisa:
        id: UUID
        nome: str

    meta = MetaData(naming_convention=NAMING_CONVENTION)
    tabela = Table("coisas", meta, *audit_columns(), Column("nome", String, nullable=False))
    mapeamentos = registry(metadata=meta)
    mapeamentos.map_imperatively(Coisa, tabela, version_id_col=tabela.c.version)
    engine = create_db_engine(f"sqlite:///{tmp_path / 'teste.db'}")
    meta.create_all(engine)
    yield SimpleNamespace(
        engine=engine, factory=create_session_factory(engine), tabela=tabela, Coisa=Coisa
    )
    mapeamentos.dispose()
    engine.dispose()
