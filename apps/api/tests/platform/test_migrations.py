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
from wedding.platform.db.engine import create_db_engine
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


CRONOGRAMA = {
    "schedule_phases",
    "milestones",
    "milestone_dependencies",
    "milestone_changes",
    "schedule_tasks",
    "checklist_items",
}


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


def test_a_migracao_de_edicao_acrescenta_a_revisao_das_dependencias_e_desce(tmp_path):  # F-CRN-01
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    config = _config(url)
    command.upgrade(config, "head")
    colunas = {c["name"] for c in inspect(create_engine(url)).get_columns("milestones")}
    assert "dependencies_revision" in colunas
    assert _ler(url, "SELECT DISTINCT dependencies_revision FROM milestones") == [(0,)]
    command.downgrade(config, "0010")
    colunas = {c["name"] for c in inspect(create_engine(url)).get_columns("milestones")}
    assert "dependencies_revision" not in colunas
    # A semente continua intacta depois de descer.
    assert _ler(url, "SELECT COUNT(*) FROM milestones") == [(29,)]
    assert _ler(url, "SELECT COUNT(*) FROM milestone_dependencies") == [(31,)]
    assert _ler(url, "SELECT COUNT(*) FROM schedule_phases") == [(5,)]
    command.upgrade(config, "head")
    assert _ler(url, "SELECT COUNT(*) FROM milestones") == [(29,)]
    assert _ler(url, "SELECT DISTINCT dependencies_revision FROM milestones") == [(0,)]


def test_a_semente_sobrevive_a_migracao_de_edicao_com_os_mesmos_ids(tmp_path):
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    config = _config(url)
    command.upgrade(config, "0010")
    antes = _ler(url, "SELECT id, title, position FROM milestones ORDER BY id")
    command.upgrade(config, "head")
    assert _ler(url, "SELECT id, title, position FROM milestones ORDER BY id") == antes


def test_o_banco_recusa_titulo_em_branco_em_marco_e_fase(tmp_path):
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    command.upgrade(_config(url), "head")
    engine = create_engine(url)
    with engine.begin() as conn, pytest.raises(IntegrityError):
        conn.execute(
            text("UPDATE milestones SET title = '   ' WHERE id = :id"), {"id": _id("marco:C01")}
        )
    with engine.begin() as conn, pytest.raises(IntegrityError):
        conn.execute(
            text("UPDATE schedule_phases SET title = '' WHERE id = :id"), {"id": _id("fase:1")}
        )
    with engine.begin() as conn, pytest.raises(IntegrityError):
        conn.execute(
            text("UPDATE milestones SET dependencies_revision = -1 WHERE id = :id"),
            {"id": _id("marco:C01")},
        )
    engine.dispose()


def test_a_migracao_de_edicao_nao_deixa_chave_estrangeira_quebrada(tmp_path):
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    command.upgrade(_config(url), "head")
    assert _ler(url, "PRAGMA foreign_key_check") == []
    engine = create_engine(url)
    alvos = {
        (tabela, fk["referred_table"])
        for tabela in ("milestone_dependencies", "milestone_changes", "milestones")
        for fk in inspect(engine).get_foreign_keys(tabela)
    }
    engine.dispose()
    assert ("milestone_dependencies", "milestones") in alvos
    assert ("milestone_changes", "milestones") in alvos
    assert ("milestones", "scope_categories") in alvos
    assert ("milestones", "schedule_phases") in alvos


def _linha_de_historico(url: str) -> None:
    engine = create_engine(url)
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO milestone_changes (id, created_at, updated_at, version, milestone_id,"
                " state_before, state_after, ignored_block, profile)"
                " VALUES (:id, '2026-10-27', '2026-10-27', 1, :m, NULL, 'Concluído', 1, 'Noiva')"
            ),
            {"id": uuid.uuid4().hex, "m": _id("marco:C03")},
        )
    engine.dispose()


def test_a_0011_sobe_da_0010_com_dados_sem_perder_nem_alterar_nada(tmp_path):  # caminho de produção
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    config = _config(url)
    command.upgrade(config, "0010")
    _linha_de_historico(url)
    sql_dependencias = (
        "SELECT id, milestone_id, depends_on_id FROM milestone_dependencies ORDER BY id"
    )
    sql_historico = "SELECT * FROM milestone_changes"
    sql_marcos = "SELECT id, phase_id, title, position, version FROM milestones ORDER BY id"
    antes = (_ler(url, sql_dependencias), _ler(url, sql_historico), _ler(url, sql_marcos))
    assert len(antes[0]) == 31
    assert len(antes[1]) == 1

    command.upgrade(config, "head")

    depois = (_ler(url, sql_dependencias), _ler(url, sql_historico), _ler(url, sql_marcos))
    assert depois == antes
    assert _ler(url, "PRAGMA foreign_key_check") == []
    assert _ler(url, "SELECT DISTINCT dependencies_revision FROM milestones") == [(0,)]


def test_o_caminho_completo_da_base_ao_head_deixa_as_chaves_estrangeiras_integras(tmp_path):
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    command.upgrade(_config(url), "head")
    assert _ler(url, "PRAGMA foreign_key_check") == []
    assert _ler(url, "SELECT COUNT(*) FROM milestone_dependencies") == [(31,)]


@pytest.mark.parametrize("caminho", ["0010_para_0011", "base_para_head"])
def test_sem_o_pragma_a_0011_quebra_com_as_chaves_ligadas_nos_dois_caminhos(
    tmp_path, monkeypatch, caminho
):
    """O `env.py` abre a conexão com `foreign_keys=ON`, e o SQLite não tem DDL transacional: o
    Alembic não envolve a migration numa transação, então o `PRAGMA foreign_keys=OFF` da 0011 vale
    de fato, na subida da base e na da 0010. Sem ele, apagar `milestones` no lote falha."""
    from alembic import op

    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    config = _config(url)
    if caminho == "0010_para_0011":
        command.upgrade(config, "0010")
    executar = op.execute

    def sem_pragma(statement, *args, **kwargs):
        if "PRAGMA foreign_keys" in str(statement):
            return None
        return executar(statement, *args, **kwargs)

    monkeypatch.setattr(op, "execute", sem_pragma)
    with pytest.raises(IntegrityError, match="FOREIGN KEY"):
        command.upgrade(config, "head")


# --- 0012: a marca de janela editada (F-CRN-02 e F-CRN-05) --------------------------------------

CHECKS_DA_JANELA = {
    "ck_milestones_window_unit_known",
    "ck_milestones_window_all_or_none",
    "ck_milestones_window_starts_before_it_ends",
}
SQL_SEMENTE = {
    "marcos": "SELECT id, phase_id, title, position, version, window_start_before,"
    " window_end_before, window_unit FROM milestones ORDER BY id",
    "dependencias": "SELECT id, milestone_id, depends_on_id FROM milestone_dependencies"
    " ORDER BY id",
    "fases": "SELECT id, title, position FROM schedule_phases ORDER BY id",
}


def _nomes_dos_checks(url: str, tabela: str) -> set[str]:
    engine = create_engine(url)
    nomes = {str(c["name"]) for c in inspect(engine).get_check_constraints(tabela)}
    engine.dispose()
    return nomes


def _tentar_update(url: str, sql: str) -> None:
    engine = create_engine(url)
    with engine.begin() as conn:
        conn.execute(text(sql), {"id": _id("marco:C06")})
    engine.dispose()


def test_a_0012_acrescenta_a_marca_de_janela_editada_falsa_e_desce_e_sobe(tmp_path):
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    config = _config(url)
    command.upgrade(config, "head")
    colunas = {c["name"] for c in inspect(create_engine(url)).get_columns("milestones")}
    assert "window_edited" in colunas
    assert _ler(url, "SELECT DISTINCT window_edited FROM milestones") == [(0,)]
    antes = {chave: _ler(url, sql) for chave, sql in SQL_SEMENTE.items()}

    command.downgrade(config, "0011")
    colunas = {c["name"] for c in inspect(create_engine(url)).get_columns("milestones")}
    assert "window_edited" not in colunas
    assert {chave: _ler(url, sql) for chave, sql in SQL_SEMENTE.items()} == antes
    assert [len(antes[c]) for c in ("marcos", "dependencias", "fases")] == [29, 31, 5]

    command.upgrade(config, "head")
    assert {chave: _ler(url, sql) for chave, sql in SQL_SEMENTE.items()} == antes
    assert _ler(url, "SELECT DISTINCT window_edited FROM milestones") == [(0,)]


def test_a_0012_nao_marca_nenhuma_janela_da_semente_como_editada(tmp_path):  # F-CRN-02
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    command.upgrade(_config(url), "0011")
    command.upgrade(_config(url), "head")
    assert _ler(url, "SELECT COUNT(*) FROM milestones WHERE window_edited") == [(0,)]


def test_o_downgrade_da_0012_preserva_os_tres_checks_da_janela(tmp_path):
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    config = _config(url)
    command.upgrade(config, "head")
    todos = _nomes_dos_checks(url, "milestones")
    assert todos >= CHECKS_DA_JANELA

    command.downgrade(config, "0011")

    assert _nomes_dos_checks(url, "milestones") == todos
    for sql in (
        "UPDATE milestones SET window_unit = NULL WHERE id = :id",
        "UPDATE milestones SET window_unit = 'dias' WHERE id = :id",
        "UPDATE milestones SET window_start_before = 1, window_end_before = 4 WHERE id = :id",
    ):
        with pytest.raises(IntegrityError):
            _tentar_update(url, sql)


def test_o_downgrade_da_0012_nao_deixa_chave_estrangeira_quebrada_e_guarda_os_dados_do_casal(
    tmp_path,
):
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    config = _config(url)
    command.upgrade(config, "head")
    _linha_de_historico(url)
    historico = _ler(url, "SELECT * FROM milestone_changes")
    assert len(historico) == 1

    command.downgrade(config, "0011")
    assert _ler(url, "PRAGMA foreign_key_check") == []
    assert _ler(url, "SELECT * FROM milestone_changes") == historico

    command.upgrade(config, "head")
    assert _ler(url, "PRAGMA foreign_key_check") == []
    assert _ler(url, "SELECT * FROM milestone_changes") == historico


def test_a_0012_sobe_da_0011_com_dados_sem_perder_nem_alterar_nada(tmp_path):  # caminho de produção
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    config = _config(url)
    command.upgrade(config, "0011")
    _linha_de_historico(url)
    antes = {chave: _ler(url, sql) for chave, sql in SQL_SEMENTE.items()}
    historico = _ler(url, "SELECT * FROM milestone_changes")

    command.upgrade(config, "head")

    assert {chave: _ler(url, sql) for chave, sql in SQL_SEMENTE.items()} == antes
    assert _ler(url, "SELECT * FROM milestone_changes") == historico
    assert _ler(url, "PRAGMA foreign_key_check") == []


def test_sem_o_pragma_a_descida_da_0012_quebra_com_as_chaves_ligadas(tmp_path, monkeypatch):
    """Como a 0011: o `drop_column` em lote recria `milestones`, e apagá-la com as dependências
    apontando para ela falha se as chaves estrangeiras estiverem ligadas. O `PRAGMA` da 0012 é o
    que impede."""
    from alembic import op

    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    config = _config(url)
    command.upgrade(config, "head")
    executar = op.execute

    def sem_pragma(statement, *args, **kwargs):
        if "PRAGMA foreign_keys" in str(statement):
            return None
        return executar(statement, *args, **kwargs)

    monkeypatch.setattr(op, "execute", sem_pragma)
    with pytest.raises(IntegrityError, match="FOREIGN KEY"):
        command.downgrade(config, "0011")


def test_a_marca_de_janela_editada_tem_default_falso_que_o_postgresql_entende(tmp_path):
    from sqlalchemy.dialects import postgresql
    from sqlalchemy.schema import CreateTable

    from wedding.modules.schedule.infrastructure.tables import milestones

    ddl = str(CreateTable(milestones).compile(dialect=postgresql.dialect()))
    assert "window_edited BOOLEAN DEFAULT false NOT NULL" in ddl
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    command.upgrade(_config(url), "head")
    engine = create_engine(url)
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO milestones (id, created_at, updated_at, version, phase_id, position,"
                " title, responsible, dependencies_revision)"
                " VALUES (:id, '2026-10-27', '2026-10-27', 1, :fase, 99, 'Marco Exemplo',"
                " 'Ambos', 0)"
            ),
            {"id": uuid.uuid4().hex, "fase": _id("fase:1")},
        )
    engine.dispose()
    assert _ler(url, "SELECT window_edited FROM milestones WHERE title = 'Marco Exemplo'") == [(0,)]


# --- 0013: tarefas avulsas e checklist (F-CRN-06 e F-CRN-07) ------------------------------------

NOVAS = {"schedule_tasks", "checklist_items"}
CHECKS_DAS_NOVAS = {
    "schedule_tasks": {
        "ck_schedule_tasks_title_not_blank",
        "ck_schedule_tasks_task_responsible",
        "ck_schedule_tasks_task_state",
    },
    "checklist_items": {
        "ck_checklist_items_text_not_blank",
        "ck_checklist_items_position_not_negative",
        "ck_checklist_items_one_owner",
    },
}


def _tarefa_sql(url: str, tarefa: str = "t1") -> None:
    engine = create_engine(url)
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO schedule_tasks (id, created_at, updated_at, version, title,"
                " responsible, state) VALUES (:id, '2026-11-04', '2026-11-04', 1,"
                " 'Tarefa Exemplo', 'Noiva', 'A fazer')"
            ),
            {"id": _id(f"tarefa:{tarefa}")},
        )
    engine.dispose()


def _item_sql(url: str, marco: str | None, tarefa: str | None, texto="Item Exemplo", posicao=0):
    engine = create_engine(url)
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO checklist_items (id, created_at, updated_at, version, milestone_id,"
                " task_id, text, position) VALUES (:id, '2026-11-04', '2026-11-04', 1, :m, :t,"
                " :texto, :posicao)"
            ),
            {
                "id": uuid.uuid4().hex,
                "m": _id(f"marco:{marco}") if marco else None,
                "t": _id(f"tarefa:{tarefa}") if tarefa else None,
                "texto": texto,
                "posicao": posicao,
            },
        )
    engine.dispose()


def test_a_0013_e_a_cabeca_e_sucede_a_0012():
    script = ScriptDirectory.from_config(_config())
    assert script.get_current_head() == "0013"
    assert script.get_revision("0013").down_revision == "0012"


def test_a_0013_cria_as_duas_tabelas_e_a_semente_continua_29_31_5(tmp_path):
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    command.upgrade(_config(url), "head")
    assert _estado(url)[0] >= NOVAS
    assert _ler(url, "SELECT COUNT(*) FROM schedule_tasks") == [(0,)]
    assert _ler(url, "SELECT COUNT(*) FROM checklist_items") == [(0,)]
    assert _ler(url, "SELECT COUNT(*) FROM milestones") == [(29,)]
    assert _ler(url, "SELECT COUNT(*) FROM milestone_dependencies") == [(31,)]
    assert _ler(url, "SELECT COUNT(*) FROM schedule_phases") == [(5,)]


def test_a_0013_desce_e_sobe_sem_perder_os_dados_dos_marcos(tmp_path):
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    config = _config(url)
    command.upgrade(config, "0012")
    engine = create_engine(url)
    with engine.begin() as conn:
        conn.execute(
            text(
                "UPDATE milestones SET note = 'nota do casal', manual_state = 'Concluído'"
                " WHERE id = :id"
            ),
            {"id": _id("marco:C06")},
        )
    engine.dispose()
    antes = {chave: _ler(url, sql) for chave, sql in SQL_SEMENTE.items()}
    marco = _ler(url, "SELECT note, manual_state FROM milestones WHERE note IS NOT NULL")

    command.upgrade(config, "head")
    assert _estado(url)[0] >= NOVAS
    assert {chave: _ler(url, sql) for chave, sql in SQL_SEMENTE.items()} == antes
    assert _ler(url, "SELECT note, manual_state FROM milestones WHERE note IS NOT NULL") == marco

    command.downgrade(config, "0012")
    assert NOVAS.isdisjoint(_estado(url)[0])
    assert {chave: _ler(url, sql) for chave, sql in SQL_SEMENTE.items()} == antes
    assert _ler(url, "SELECT note, manual_state FROM milestones WHERE note IS NOT NULL") == marco
    assert [len(antes[c]) for c in ("marcos", "dependencias", "fases")] == [29, 31, 5]
    assert _ler(url, "PRAGMA foreign_key_check") == []

    command.upgrade(config, "head")
    assert _estado(url)[0] >= NOVAS
    assert _ler(url, "PRAGMA foreign_key_check") == []


def test_a_0013_desce_mesmo_com_avulsas_e_itens_gravados(tmp_path):
    """A descida apaga os itens antes das avulsas (a chave estrangeira do item aponta para elas)."""
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    config = _config(url)
    command.upgrade(config, "head")
    _tarefa_sql(url)
    _item_sql(url, "C06", None)
    _item_sql(url, None, "t1")
    command.downgrade(config, "0012")
    assert NOVAS.isdisjoint(_estado(url)[0])
    assert _ler(url, "PRAGMA foreign_key_check") == []


@pytest.mark.parametrize(
    ("marco", "tarefa"),
    [("C06", "t1"), (None, None)],
    ids=["os dois donos", "nenhum dono"],
)
def test_o_check_de_dono_recusa_os_dois_e_nenhum(tmp_path, marco, tarefa):  # F-CRN-07
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    command.upgrade(_config(url), "head")
    _tarefa_sql(url)
    with pytest.raises(IntegrityError, match="ck_checklist_items_one_owner"):
        _item_sql(url, marco, tarefa)
    _item_sql(url, "C06", None)  # só o marco vale
    _item_sql(url, None, "t1")  # só a avulsa vale
    assert _ler(url, "SELECT COUNT(*) FROM checklist_items") == [(2,)]


def test_a_0013_nomeia_os_checks_pela_convencao(tmp_path):
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    command.upgrade(_config(url), "head")
    for tabela, esperados in CHECKS_DAS_NOVAS.items():
        assert _nomes_dos_checks(url, tabela) >= esperados, tabela


def test_os_checks_da_0013_recusam_valor_invalido(tmp_path):
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    command.upgrade(_config(url), "head")
    _tarefa_sql(url)
    for texto, posicao, erro in (
        ("   ", 0, "text_not_blank"),
        ("Item Exemplo", -1, "position_not_negative"),
    ):
        with pytest.raises(IntegrityError, match=erro):
            _item_sql(url, "C06", None, texto, posicao)
    engine = create_engine(url)
    for titulo, responsavel, estado, erro in (
        ("  ", "Noiva", "A fazer", "title_not_blank"),
        ("Tarefa Exemplo", "Ninguém", "A fazer", "task_responsible"),
        ("Tarefa Exemplo", "Noiva", "Concluído", "task_state"),
    ):
        with pytest.raises(IntegrityError, match=erro), engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO schedule_tasks (id, created_at, updated_at, version, title,"
                    " responsible, state) VALUES (:id, '2026-11-04', '2026-11-04', 1, :t, :r, :s)"
                ),
                {"id": uuid.uuid4().hex, "t": titulo, "r": responsavel, "s": estado},
            )
    engine.dispose()


def test_as_chaves_dos_itens_apontam_para_marco_e_avulsa_e_nao_apagam(tmp_path):
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    command.upgrade(_config(url), "head")
    engine = create_engine(url)
    chaves = {
        fk["referred_table"]: fk for fk in inspect(engine).get_foreign_keys("checklist_items")
    }
    engine.dispose()
    assert set(chaves) == {"milestones", "schedule_tasks"}
    assert chaves["milestones"]["constrained_columns"] == ["milestone_id"]
    assert chaves["schedule_tasks"]["constrained_columns"] == ["task_id"]
    for fk in chaves.values():
        assert fk.get("options", {}).get("ondelete") == "RESTRICT"
    _tarefa_sql(url)
    _item_sql(url, "C06", None)
    _item_sql(url, None, "t1")
    # O `create_engine` puro não liga as chaves estrangeiras do SQLite; a do app, sim.
    engine = create_db_engine(url)
    for tabela, chave in (("milestones", _id("marco:C06")), ("schedule_tasks", _id("tarefa:t1"))):
        with pytest.raises(IntegrityError, match="FOREIGN KEY"), engine.begin() as conn:
            conn.execute(text(f"DELETE FROM {tabela} WHERE id = :id"), {"id": chave})
    engine.dispose()


def test_os_indices_do_checklist_sao_parciais_por_dono_vivo_e_nenhum_e_unico(tmp_path):
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    command.upgrade(_config(url), "head")
    engine = create_engine(url)
    indices = inspect(engine).get_indexes("checklist_items")
    engine.dispose()
    assert {tuple(i["column_names"]) for i in indices} == {
        ("milestone_id", "position"),
        ("task_id", "position"),
    }
    assert not any(i["unique"] for i in indices)
    sql = " ".join(
        linha[0]
        for linha in _ler(
            url,
            "SELECT sql FROM sqlite_master WHERE type = 'index' AND tbl_name = 'checklist_items'",
        )
        if linha[0]
    )
    assert sql.count("WHERE deleted_at IS NULL") == 2
    # Sem índice único em (dono, posição): reordenar troca posições em passos intermediários.
    _tarefa_sql(url)
    _item_sql(url, "C06", None, "A", 0)
    _item_sql(url, "C06", None, "B", 0)


def test_toda_coluna_e_as_duas_tabelas_novas_tem_comentario(tmp_path):
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    command.upgrade(_config(url), "head")
    from wedding.modules.schedule.infrastructure.tables import checklist_items, schedule_tasks

    for tabela in (schedule_tasks, checklist_items):
        assert tabela.comment, tabela.name
        assert [c.name for c in tabela.columns if not c.comment] == [], tabela.name


def test_o_feito_do_item_tem_default_falso_que_o_postgresql_entende(tmp_path):
    from sqlalchemy.dialects import postgresql
    from sqlalchemy.schema import CreateTable

    from wedding.modules.schedule.infrastructure.tables import checklist_items

    ddl = str(CreateTable(checklist_items).compile(dialect=postgresql.dialect()))
    assert "done BOOLEAN DEFAULT false NOT NULL" in ddl
    url = f"sqlite:///{tmp_path / 'migracao.db'}"
    command.upgrade(_config(url), "head")
    _item_sql(url, "C06", None)
    assert _ler(url, "SELECT done FROM checklist_items") == [(0,)]
