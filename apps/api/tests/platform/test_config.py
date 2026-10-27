from wedding.platform.config import Settings


def test_banco_padrao_e_um_sqlite_local(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert Settings().database_url == "sqlite:///data/altare.db"


def test_banco_vem_da_variavel_de_ambiente(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///outro.db")
    assert Settings().database_url == "sqlite:///outro.db"
