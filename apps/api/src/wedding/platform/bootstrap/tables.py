from importlib import import_module

# Cada módulo com tabelas entra aqui ao nascer.
_TABLE_MODULES = (
    "wedding.modules.identity.infrastructure.tables",
    "wedding.modules.files.infrastructure.tables",
    "wedding.modules.wedding.infrastructure.tables",
    "wedding.modules.wedding.infrastructure.scope_tables",
    "wedding.modules.wedding.infrastructure.reference_tables",
    "wedding.modules.guests.infrastructure.tables",
)


def load_tables() -> None:
    """Importa as tabelas dos módulos para o `metadata` conhecê-las (Alembic e testes)."""
    for module in _TABLE_MODULES:
        import_module(module)
