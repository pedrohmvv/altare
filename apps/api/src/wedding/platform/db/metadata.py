from sqlalchemy import MetaData
from sqlalchemy.orm import registry

# Necessária para o Alembic gerar ALTER reproduzível em batch mode (stack.md §4, regra 6).
NAMING_CONVENTION: dict[str, str] = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)

# Mapeamento imperativo: as tabelas (infraestrutura) ligam-se às dataclasses do domínio.
mapper_registry = registry(metadata=metadata)
