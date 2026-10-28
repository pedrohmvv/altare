from wedding.platform.bootstrap.tables import load_tables
from wedding.platform.db.metadata import metadata


def test_carregar_as_tabelas_registra_as_de_cada_modulo_no_metadata():
    load_tables()
    assert {
        "users",
        "user_sessions",
        "file_assets",
        "baseline_fields",
        "baseline_changes",
        "scope_groups",
        "scope_categories",
        "scope_evaluations",
        "scope_status_changes",
    } <= set(metadata.tables)


def test_carregar_duas_vezes_e_inofensivo():
    load_tables()
    load_tables()
    assert "users" in metadata.tables
