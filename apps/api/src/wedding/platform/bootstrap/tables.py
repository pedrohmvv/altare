from importlib import import_module

# Cada módulo com tabelas entra aqui ao nascer.
_TABLE_MODULES = ("wedding.modules.identity.infrastructure.tables",)


def load_tables() -> None:
    """Importa as tabelas dos módulos para o `metadata` conhecê-las (Alembic e testes)."""
    for module in _TABLE_MODULES:
        import_module(module)
