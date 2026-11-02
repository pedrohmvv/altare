import uuid
from pathlib import Path
from typing import Any

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import IntegrityError
from tests.modules.schedule.catalog import FASES, MARCOS, SEED_NS

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


def test_a_migracao_de_arquivos_cria_e_remove_a_tabela(tmp_path):
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    config = _config(url)
    command.upgrade(config, "head")
    assert "file_assets" in _estado(url)[0]
    command.downgrade(config, "0002")
    assert "file_assets" not in _estado(url)[0]
    assert {"users", "user_sessions"} <= _estado(url)[0]


def test_a_migracao_das_definicoes_base_semeia_e_remove_as_tabelas(tmp_path):
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    config = _config(url)
    command.upgrade(config, "head")
    assert {"baseline_fields", "baseline_changes"} <= _estado(url)[0]
    engine = create_engine(url)
    with engine.connect() as conn:
        linhas = conn.execute(
            text("SELECT field_key, status, value FROM baseline_fields ORDER BY field_key")
        ).all()
    engine.dispose()
    assert [(chave, status, valor) for chave, status, valor in linhas] == [
        (chave, "Em definição", None)
        for chave in ["ceiling", "ceremony", "city", "date", "format", "size"]
    ]
    command.downgrade(config, "0003")
    assert {"baseline_fields", "baseline_changes"}.isdisjoint(_estado(url)[0])
    assert "file_assets" in _estado(url)[0]


def test_a_migracao_do_mapa_de_escopo_semeia_o_catalogo_e_remove_as_tabelas(tmp_path):
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    config = _config(url)
    tabelas = {"scope_groups", "scope_categories", "scope_evaluations", "scope_status_changes"}
    command.upgrade(config, "head")
    assert tabelas <= _estado(url)[0]
    engine = create_engine(url)
    with engine.connect() as conn:
        contagens = [
            conn.execute(text(f"SELECT COUNT(*) FROM {tabela}")).scalar()
            for tabela in sorted(tabelas)
        ]
    engine.dispose()
    # evaluations, categories, groups, status_changes (ordem alfabética das tabelas)
    assert contagens == [18, 36, 8, 0]
    command.downgrade(config, "0004")
    assert tabelas.isdisjoint(_estado(url)[0])
    assert {"baseline_fields", "baseline_changes"} <= _estado(url)[0]


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


def test_a_migracao_das_referencias_cria_e_remove_a_tabela(tmp_path):
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    config = _config(url)
    command.upgrade(config, "head")
    assert "scope_references" in _estado(url)[0]
    command.downgrade(config, "0005")
    assert "scope_references" not in _estado(url)[0]
    assert {"scope_categories", "file_assets"} <= _estado(url)[0]


def test_a_migracao_dos_convidados_cria_e_remove_as_tabelas(tmp_path):
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    config = _config(url)
    tabelas = {"guest_households", "guests", "guest_status_changes"}
    command.upgrade(config, "head")
    assert tabelas <= _estado(url)[0]
    engine = create_engine(url)
    with engine.connect() as conn:
        # Diferente do escopo, a lista nasce vazia: nenhum convidado é semeado (AGENTS.md §2).
        contagens = [conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar() for t in tabelas]
    engine.dispose()
    assert contagens == [0, 0, 0]
    command.downgrade(config, "0006")
    assert tabelas.isdisjoint(_estado(url)[0])
    assert {"scope_references", "scope_categories"} <= _estado(url)[0]


def test_a_migracao_das_configuracoes_semeia_uma_linha_vazia_e_a_remove(tmp_path):
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    config = _config(url)
    command.upgrade(config, "head")
    engine = create_engine(url)
    with engine.connect() as conn:
        linhas = conn.execute(
            text(
                "SELECT version, weight_certain_pct, weight_probable_pct, weight_phase_2_pct, "
                "exempt_until_age, paying_until_age FROM guest_settings"
            )
        ).all()
    engine.dispose()
    # Pesos e limites são decisões do casal: a semente é uma linha só, toda vazia (D-030).
    assert [tuple(linha) for linha in linhas] == [(1, None, None, None, None, None)]
    command.downgrade(config, "0007")
    assert "guest_settings" not in _estado(url)[0]
    assert {"guests", "guest_households"} <= _estado(url)[0]


def test_a_migracao_do_convite_acrescenta_as_colunas_sem_perder_nada_e_desce(tmp_path):
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    config = _config(url)
    command.upgrade(config, "0008")
    engine = create_engine(url)
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO guest_households (id, created_at, updated_at, version, name, "
                "name_key, side, members_revision) VALUES ('00000000000000000000000000000001', "
                "'2026-10-28', '2026-10-28', 1, 'Família Exemplo', 'família exemplo', 'Comum', 0)"
            )
        )

    command.upgrade(config, "0009")

    with engine.connect() as conn:
        linha = conn.execute(
            text("SELECT name, invite_sent_on, invite_channel FROM guest_households")
        ).one()
        indices = {i["name"] for i in inspect(conn).get_indexes("guest_households")}
    assert tuple(linha) == ("Família Exemplo", None, None)
    # O lote recria a tabela: o índice parcial do nome não pode se perder.
    assert "uq_guest_households_name_key_live" in indices
    command.downgrade(config, "0008")
    with engine.connect() as conn:
        colunas = {c["name"] for c in inspect(conn).get_columns("guest_households")}
        nome = conn.execute(text("SELECT name FROM guest_households")).scalar()
    engine.dispose()
    assert {"invite_sent_on", "invite_channel"}.isdisjoint(colunas)
    assert nome == "Família Exemplo"


CRONOGRAMA = {"schedule_phases", "milestones", "milestone_dependencies", "milestone_changes"}


def _ler(url: str, sql: str) -> list[Any]:
    engine = create_engine(url)
    with engine.connect() as conn:
        linhas = list(conn.execute(text(sql)).all())
    engine.dispose()
    return linhas


def _id(valor: str) -> str:
    """Como o SQLite guarda o `Uuid` do SQLAlchemy: 32 caracteres hexadecimais, sem hífen."""
    return uuid.uuid5(SEED_NS, valor).hex


def test_a_migracao_do_cronograma_cria_as_tabelas_e_semeia_29_marcos_em_5_fases(
    tmp_path,
):  # F-CRN-02
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    command.upgrade(_config(url), "head")
    assert _estado(url)[0] >= CRONOGRAMA
    assert _ler(url, "SELECT COUNT(*) FROM schedule_phases") == [(5,)]
    assert _ler(url, "SELECT COUNT(*) FROM milestones") == [(29,)]
    assert _ler(url, "SELECT COUNT(*) FROM milestone_changes") == [(0,)]


def test_a_semente_traz_as_5_fases_na_ordem_do_catalogo(tmp_path):  # F-CRN-02
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    command.upgrade(_config(url), "head")
    fases = _ler(url, "SELECT id, title, position FROM schedule_phases ORDER BY position")
    assert [(f[1], f[2]) for f in fases] == list(zip(FASES, range(5), strict=True))
    assert [f[0] for f in fases] == [_id(f"fase:{n}") for n in range(1, 6)]


def test_cada_marco_da_semente_bate_com_a_tabela_de_cronograma_md(tmp_path):  # F-CRN-02
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    command.upgrade(_config(url), "head")
    linhas = _ler(
        url,
        "SELECT id, phase_id, title, position, responsible, category_id, note, target_date,"
        " manual_state, window_start_before, window_end_before, window_unit, version, deleted_at"
        " FROM milestones",
    )
    por_id = {linha[0]: linha for linha in linhas}
    posicao_na_fase: dict[int, int] = {}
    for codigo, fase, titulo, categoria, _deps, janela in MARCOS:
        posicao = posicao_na_fase.get(fase, 0)
        posicao_na_fase[fase] = posicao + 1
        esperado_categoria = _id(f"categoria:{categoria}") if categoria else None
        (
            _,
            fase_id,
            nome,
            pos,
            responsavel,
            cat,
            nota,
            prazo,
            manual,
            ini,
            fim,
            unid,
            ver,
            apagado,
        ) = por_id[_id(f"marco:{codigo}")]
        assert fase_id == _id(f"fase:{fase + 1}"), codigo
        assert (nome, pos) == (titulo, posicao), codigo
        assert cat == esperado_categoria, codigo
        assert (ini, fim, unid) == (janela or (None, None, None)), codigo
        # Responsável inicial Ambos, nenhum prazo, nota nem estado marcado (F-CRN-02, regra 3).
        assert (responsavel, nota, prazo, manual, ver, apagado) == (
            "Ambos",
            None,
            None,
            None,
            1,
            None,
        ), codigo


def test_a_semente_liga_cada_categoria_pelo_id_fixo_do_mapa_e_o_c11_usa_o_nome_do_catalogo(
    tmp_path,
):
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    command.upgrade(_config(url), "head")
    ligacoes = dict(
        _ler(
            url,
            "SELECT m.id, c.name FROM milestones m JOIN scope_categories c ON c.id = m.category_id",
        )
    )
    esperado = {_id(f"marco:{m[0]}"): m[3] for m in MARCOS if m[3]}
    assert ligacoes == esperado
    assert ligacoes[_id("marco:C11")] == "Música (DJ, banda)"
    sem_categoria = _ler(url, "SELECT COUNT(*) FROM milestones WHERE category_id IS NULL")
    assert sem_categoria == [(sum(1 for m in MARCOS if m[3] is None),)]


def test_a_semente_traz_as_dependencias_exatas_da_tabela(tmp_path):  # F-CRN-02
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    command.upgrade(_config(url), "head")
    pares = set(_ler(url, "SELECT milestone_id, depends_on_id FROM milestone_dependencies"))
    esperado = {
        (_id(f"marco:{codigo}"), _id(f"marco:{dependencia}"))
        for codigo, _f, _t, _c, dependencias, _j in MARCOS
        for dependencia in dependencias
    }
    assert pares == esperado
    assert len(esperado) == 31
    ativos = _ler(url, "SELECT COUNT(*) FROM milestone_dependencies WHERE deleted_at IS NULL")
    assert ativos == [(31,)]


def test_o_historico_de_marcos_recusa_perfil_ambos_e_estado_repetido(tmp_path):
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    command.upgrade(_config(url), "head")
    engine = create_engine(url)
    marco = _id("marco:C01")

    def inserir(perfil, antes, depois, ignorou=0):
        with engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO milestone_changes (id, created_at, updated_at, version,"
                    " milestone_id, state_before, state_after, ignored_block, profile)"
                    " VALUES (:id, '2026-10-27', '2026-10-27', 1, :m, :b, :a, :i, :p)"
                ),
                {
                    "id": uuid.uuid4().hex,
                    "m": marco,
                    "b": antes,
                    "a": depois,
                    "i": ignorou,
                    "p": perfil,
                },
            )

    inserir("Noivo", None, "Concluído")
    inserir("Noiva", "Concluído", None)
    with pytest.raises(IntegrityError):
        inserir("Ambos", None, "Concluído")
    with pytest.raises(IntegrityError):
        inserir("Noivo", "Concluído", "Concluído")
    with pytest.raises(IntegrityError):
        inserir("Noivo", None, None)
    with pytest.raises(IntegrityError):
        inserir("Noivo", "Em andamento", None, ignorou=1)
    with pytest.raises(IntegrityError):
        inserir("Noivo", None, "Qualquer")
    engine.dispose()


def test_as_dependencias_recusam_ligar_o_marco_a_ele_mesmo_e_repetir_o_par(tmp_path):
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    command.upgrade(_config(url), "head")
    engine = create_engine(url)

    def inserir(marco, depende):
        with engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO milestone_dependencies (id, created_at, updated_at, version,"
                    " milestone_id, depends_on_id) VALUES (:id, '2026-10-27', '2026-10-27', 1,"
                    " :m, :d)"
                ),
                {"id": uuid.uuid4().hex, "m": _id(f"marco:{marco}"), "d": _id(f"marco:{depende}")},
            )

    with pytest.raises(IntegrityError):
        inserir("C01", "C01")
    with pytest.raises(IntegrityError):
        inserir("C03", "C01")  # já existe na semente
    inserir("C01", "C02")
    engine.dispose()


def test_a_migracao_do_cronograma_desce_e_deixa_o_resto_intacto(tmp_path):
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    config = _config(url)
    command.upgrade(config, "head")
    command.downgrade(config, "0009")
    tabelas = _estado(url)[0]
    assert CRONOGRAMA.isdisjoint(tabelas)
    assert {"scope_categories", "guests"} <= tabelas
    assert _ler(url, "SELECT COUNT(*) FROM scope_categories") == [(18,)]
    command.upgrade(config, "head")
    assert _ler(url, "SELECT COUNT(*) FROM milestones") == [(29,)]
