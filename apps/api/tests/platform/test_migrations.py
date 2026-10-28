from pathlib import Path

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect, text

from wedding.platform.bootstrap.tables import load_tables
from wedding.platform.db.metadata import metadata

API_DIR = Path(__file__).parents[2]


def _config(url: str | None = None) -> Config:
    config = Config(str(API_DIR / "alembic.ini"))
    if url:
        config.set_main_option("sqlalchemy.url", url)
    return config


def _estado(url: str) -> tuple[set[str], list[str]]:
    engine = create_engine(url)
    with engine.connect() as conn:
        tabelas = set(inspect(conn).get_table_names())
        versoes = (
            [r[0] for r in conn.execute(text("SELECT version_num FROM alembic_version"))]
            if "alembic_version" in tabelas
            else []
        )
    engine.dispose()
    return tabelas, versoes


def test_historico_tem_uma_unica_cabeca():
    assert len(ScriptDirectory.from_config(_config()).get_heads()) == 1


def test_migracoes_sobem_descem_e_sobem(tmp_path):
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    config = _config(url)
    cabeca = ScriptDirectory.from_config(config).get_current_head()

    command.upgrade(config, "head")
    subiu, versoes = _estado(url)
    assert versoes == [cabeca]

    command.downgrade(config, "base")
    desceu, versoes = _estado(url)
    assert versoes == []
    assert desceu - {"alembic_version"} == set()

    command.upgrade(config, "head")
    subiu_de_novo, versoes = _estado(url)
    assert versoes == [cabeca]
    assert subiu_de_novo == subiu


def test_a_migracao_de_identidade_cria_e_remove_as_tabelas(tmp_path):
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    config = _config(url)
    command.upgrade(config, "head")
    assert {"users", "user_sessions"} <= _estado(url)[0]
    command.downgrade(config, "0001")
    assert {"users", "user_sessions"}.isdisjoint(_estado(url)[0])


def test_banco_migrado_nao_difere_do_modelo(tmp_path):
    load_tables()
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    command.upgrade(_config(url), "head")
    engine = create_engine(url)
    with engine.connect() as conn:
        diferencas = compare_metadata(MigrationContext.configure(conn), metadata)
    engine.dispose()
    assert diferencas == []


def test_url_vem_do_ambiente_quando_o_ini_nao_a_define(tmp_path, monkeypatch):
    arquivo = tmp_path / "pasta-nova" / "ambiente.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{arquivo}")
    command.upgrade(_config(), "head")
    assert arquivo.exists()
    assert _estado(f"sqlite:///{arquivo}")[1] != []


def test_nao_ha_migracao_que_pule_o_downgrade():
    pasta = API_DIR / "migrations" / "versions"
    for arquivo in pasta.glob("*.py"):
        assert "def downgrade" in arquivo.read_text(encoding="utf-8"), arquivo.name


@pytest.mark.parametrize("nome", ["alembic.ini", "migrations/env.py"])
def test_arquivos_de_configuracao_existem(nome):
    assert (API_DIR / nome).exists()
