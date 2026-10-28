from wedding.platform.config import Settings


def test_banco_padrao_e_um_sqlite_local(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert Settings().database_url == "sqlite:///data/altare.db"


def test_banco_vem_da_variavel_de_ambiente(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///outro.db")
    assert Settings().database_url == "sqlite:///outro.db"


def test_cookie_da_sessao_e_seguro_por_padrao(monkeypatch):
    monkeypatch.delenv("SESSION_COOKIE_SECURE", raising=False)
    assert Settings().session_cookie_secure is True


def test_cookie_seguro_pode_ser_desligado_so_para_o_desenvolvimento_local(monkeypatch):
    monkeypatch.setenv("SESSION_COOKIE_SECURE", "false")
    assert Settings().session_cookie_secure is False


def test_arquivos_vao_para_uma_pasta_local_por_padrao(monkeypatch):
    monkeypatch.delenv("FILES_DIR", raising=False)
    assert Settings().files_dir == "data/files"


def test_a_pasta_dos_arquivos_vem_da_variavel_de_ambiente(monkeypatch):
    monkeypatch.setenv("FILES_DIR", "/dados/arquivos")
    assert Settings().files_dir == "/dados/arquivos"
