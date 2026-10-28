from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import insert, select, text
from sqlalchemy.exc import IntegrityError

from wedding.modules.wedding.application.commands.change_scope_status import (
    ChangeScopeStatus,
    ChangeScopeStatusCommand,
)
from wedding.modules.wedding.application.commands.create_scope_category import (
    CreateScopeCategory,
    CreateScopeCategoryCommand,
)
from wedding.modules.wedding.application.commands.create_scope_group import (
    CreateScopeGroup,
    CreateScopeGroupCommand,
)
from wedding.modules.wedding.application.commands.set_my_evaluation import (
    SetMyEvaluation,
    SetMyEvaluationCommand,
)
from wedding.modules.wedding.application.commands.update_scope_category import (
    UpdateScopeCategory,
    UpdateScopeCategoryCommand,
)
from wedding.modules.wedding.application.queries.get_scope_map import GetScopeMap
from wedding.modules.wedding.application.queries.list_scope_category_history import (
    ListScopeCategoryHistory,
)
from wedding.modules.wedding.application.scope_map import build_scope_map
from wedding.modules.wedding.domain.errors import DuplicateScopeName
from wedding.modules.wedding.domain.scope_entities import ScopeCategory
from wedding.modules.wedding.domain.scope_rules import AlignmentState
from wedding.modules.wedding.domain.scope_values import Origin, Priority, ScopeStatus
from wedding.modules.wedding.infrastructure.mapping import start_mappers
from wedding.modules.wedding.infrastructure.scope_tables import (
    scope_categories,
    scope_evaluations,
    scope_groups,
    scope_status_changes,
)
from wedding.modules.wedding.infrastructure.uow import SqlWeddingUnitOfWork
from wedding.platform.bootstrap.tables import load_tables
from wedding.platform.db.engine import create_db_engine, create_session_factory
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.errors import VersionConflict
from wedding.shared_kernel.ids import UuidGenerator
from wedding.shared_kernel.profile import ProfileKind

API_DIR = Path(__file__).parents[3]
NOIVO = Actor(user_id=uuid4(), profile=ProfileKind.NOIVO)
NOIVA = Actor(user_id=uuid4(), profile=ProfileKind.NOIVA)
CATALOG = {
    "Cerimônia": ["Cerimônia civil", "Cerimônia religiosa ou simbólica"],
    "Espaço e alimentação": ["Espaço", "Buffet", "Bebidas e bar", "Bolo e doces"],
    "Registro": ["Fotografia", "Vídeo"],
    "Som e ambiente": ["Música (DJ, banda)", "Decoração e flores", "Iluminação e som"],
    "Estética": ["Trajes", "Beleza (noivos)"],
    "Papelaria e lembranças": ["Convites e papelaria", "Lembrancinhas"],
    "Condução": ["Cerimonial do dia"],
    "Pós-festa": ["Noite de núpcias", "Lua de mel"],
}


@pytest.fixture
def banco(tmp_path, clock):
    """O banco como a migration o deixa, com o catálogo semeado: é o que o app encontra."""
    load_tables()
    start_mappers()
    url = f"sqlite:///{tmp_path / 'escopo.db'}"
    config = Config(str(API_DIR / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", url)
    command.upgrade(config, "head")
    engine = create_db_engine(url)
    factory = create_session_factory(engine)

    def uow(ator: Actor = NOIVO) -> SqlWeddingUnitOfWork:
        return SqlWeddingUnitOfWork(factory, clock, ator)

    ids = UuidGenerator()
    yield SimpleNamespace(
        engine=engine,
        clock=clock,
        uow=uow,
        mapa=GetScopeMap(uow),
        criar_grupo=CreateScopeGroup(uow, ids),
        criar_categoria=CreateScopeCategory(uow, ids),
        atualizar=UpdateScopeCategory(uow),
        status=ChangeScopeStatus(uow, ids),
        avaliar=SetMyEvaluation(uow),
        historico=ListScopeCategoryHistory(uow),
    )
    engine.dispose()


def _categoria(mapa, nome):
    return next(c for g in mapa.groups for c in g.categories if c.name == nome)


class TestSemente:
    def test_traz_os_8_grupos_e_as_18_categorias_da_spec_na_ordem(self, banco):  # F-PLN-02
        mapa = banco.mapa.execute(NOIVO)
        assert [g.name for g in mapa.groups] == list(CATALOG)
        for grupo in mapa.groups:
            assert [c.name for c in grupo.categories] == CATALOG[grupo.name]
        assert sum(len(g.categories) for g in mapa.groups) == 18

    def test_tudo_nasce_em_discussao_sem_estimativa_do_catalogo_e_visivel(self, banco):
        mapa = banco.mapa.execute(NOIVO)
        for grupo in mapa.groups:
            assert (grupo.origin, grupo.hidden, grupo.can_delete) == (Origin.CATALOG, False, False)
            for cat in grupo.categories:
                assert cat.status is ScopeStatus.IN_DISCUSSION
                assert cat.estimate_cents is None
                assert (cat.origin, cat.hidden, cat.visible, cat.can_delete) == (
                    Origin.CATALOG,
                    False,
                    True,
                    False,
                )
                assert cat.alignment.state is AlignmentState.MISSING
        assert (mapa.progress.classified, mapa.progress.total) == (0, 18)
        assert mapa.totals.essential_cents == mapa.totals.maybe_cents == 0

    def test_toda_categoria_tem_exatamente_um_par_de_avaliacoes_vazias(self, banco):
        with banco.engine.connect() as conn:
            linhas = conn.execute(
                select(
                    scope_evaluations.c.category_id,
                    scope_evaluations.c.profile,
                    scope_evaluations.c.priority,
                    scope_evaluations.c.version,
                )
            ).all()
            categorias = conn.execute(select(scope_categories.c.id)).scalars().all()
        assert len(linhas) == 36
        for categoria in categorias:
            perfis = sorted(p.value for c, p, _, _ in linhas if c == categoria)
            assert perfis == ["Noiva", "Noivo"]
        assert all(prioridade is None and versao == 1 for _, _, prioridade, versao in linhas)

    def test_nenhum_historico_de_status_na_semente(self, banco):
        with banco.engine.connect() as conn:
            assert conn.execute(select(scope_status_changes.c.id)).all() == []


class TestFluxoNoBanco:
    def test_criar_grupo_e_categoria_cria_o_par_e_o_mapa_devolve_tudo(self, banco):
        banco.criar_grupo.execute(CreateScopeGroupCommand("Grupo Exemplo"), NOIVO)
        mapa = banco.mapa.execute(NOIVO)
        grupo = next(g for g in mapa.groups if g.name == "Grupo Exemplo")
        banco.criar_categoria.execute(
            CreateScopeCategoryCommand(grupo.id, "Frente Exemplo", 2_800_000), NOIVA
        )
        cat = _categoria(banco.mapa.execute(NOIVO), "Frente Exemplo")
        assert (cat.estimate_cents, cat.origin, cat.can_delete, cat.version) == (
            2_800_000,
            Origin.COUPLE,
            True,
            1,
        )
        assert (cat.noivo.version, cat.noiva.version) == (1, 1)

    def test_status_avaliacao_historico_e_motivo_do_descarte_anterior(self, banco, clock):
        cat = _categoria(banco.mapa.execute(NOIVO), "Fotografia")
        banco.status.execute(
            ChangeScopeStatusCommand(cat.id, ScopeStatus.OUT, "fora do teto", cat.version), NOIVA
        )
        clock.advance(hours=1)
        cat = _categoria(banco.mapa.execute(NOIVO), "Fotografia")
        banco.status.execute(
            ChangeScopeStatusCommand(cat.id, ScopeStatus.IN_DISCUSSION, None, cat.version), NOIVO
        )
        banco.avaliar.execute(
            SetMyEvaluationCommand(cat.id, Priority.WANT_A_LOT, "adoramos", cat.noiva.version),
            NOIVA,
        )
        cat = _categoria(banco.mapa.execute(NOIVO), "Fotografia")
        assert cat.status is ScopeStatus.IN_DISCUSSION
        assert cat.discard_reason == "fora do teto"  # F-PLN-03: a reaberta mostra o motivo anterior
        assert (cat.noiva.priority, cat.noiva.note, cat.noiva.version) == (
            Priority.WANT_A_LOT,
            "adoramos",
            2,
        )
        assert cat.alignment.missing == (ProfileKind.NOIVO,)
        recente, antiga = banco.historico.execute(cat.id, NOIVO)
        assert (recente.from_status, recente.to_status, recente.profile) == (
            ScopeStatus.OUT,
            ScopeStatus.IN_DISCUSSION,
            ProfileKind.NOIVO,
        )
        assert (antiga.reason, antiga.profile) == ("fora do teto", ProfileKind.NOIVA)
        assert recente.changed_at > antiga.changed_at

    def test_dois_mudando_o_status_ao_mesmo_tempo_o_segundo_recebe_conflito(self, banco):
        cat = _categoria(banco.mapa.execute(NOIVO), "Espaço")
        with banco.uow(NOIVO) as a, banco.uow(NOIVA) as b:
            ca, cb = a.scope.get_category(cat.id), b.scope.get_category(cat.id)
            assert ca is not None
            assert cb is not None
            ca.change_status(ScopeStatus.ESSENTIAL, None)
            cb.change_status(ScopeStatus.MAYBE, None)
            a.commit()
            with pytest.raises(VersionConflict):
                b.commit()
        assert _categoria(banco.mapa.execute(NOIVO), "Espaço").status is ScopeStatus.ESSENTIAL

    def test_renomear_para_nome_ocupado_e_nome_duplicado_e_nao_erro_de_banco(self, banco):
        cat = _categoria(banco.mapa.execute(NOIVO), "Buffet")
        grupo = next(g for g in banco.mapa.execute(NOIVO).groups if cat in g.categories)
        with pytest.raises(DuplicateScopeName):
            banco.atualizar.execute(
                UpdateScopeCategoryCommand(cat.id, "  FOTOGRAFIA", grupo.id, None, cat.version),
                NOIVO,
            )
        assert _categoria(banco.mapa.execute(NOIVO), "Buffet").version == 1

    def test_duas_criacoes_com_o_mesmo_nome_ao_mesmo_tempo_a_segunda_vira_duplicado(self, banco):
        with banco.uow(NOIVO) as a, banco.uow(NOIVA) as b:
            grupo_id = a.scope.list_groups()[0].id
            for uow in (a, b):
                uow.scope.add_category(
                    ScopeCategory(uuid4(), grupo_id, "Nome Disputado", 99, Origin.COUPLE)
                )
            a.commit()
            with pytest.raises(DuplicateScopeName):
                b.commit()

    def test_depois_do_erro_o_banco_continua_consistente(self, banco):
        with banco.uow() as uow:
            mapa = build_scope_map(uow.scope)
        assert sum(len(g.categories) for g in mapa.groups) == 18


class TestRestricoesDoBanco:
    def _insere_categoria(self, conn, **valores):
        base = {
            "id": uuid4(),
            "created_at": datetime(2026, 10, 28, tzinfo=UTC),
            "updated_at": datetime(2026, 10, 28, tzinfo=UTC),
            "version": 1,
            "name": "Outra Exemplo",
            "name_key": "outra exemplo",
            "position": 0,
            "origin": "casal",
            "status": "Em discussão",
        }
        grupo = conn.execute(select(scope_groups.c.id)).scalars().first()
        return conn.execute(insert(scope_categories).values({**base, "group_id": grupo, **valores}))

    def test_nome_vivo_repetido_e_barrado_mas_o_de_excluida_pode_voltar(self, banco):
        with banco.engine.begin() as conn:
            self._insere_categoria(conn, name_key="solta")
            with pytest.raises(IntegrityError), conn.begin_nested():
                self._insere_categoria(conn, name_key="solta")
            conn.execute(
                text(
                    "UPDATE scope_categories SET deleted_at = '2026-10-28 00:00:00' "
                    "WHERE name_key = 'solta'"
                )
            )
            self._insere_categoria(conn, name_key="solta")

    @pytest.mark.parametrize(
        "valores",
        [
            {"estimate_cents": 0},
            {"status": "Quase"},
            {"origin": "outro"},
            {"position": -1},
            {"origin": "catalogo", "deleted_at": datetime(2026, 10, 28, tzinfo=UTC)},
        ],
    )
    def test_categoria_com_valor_fora_das_regras_e_barrada(self, banco, valores):
        with banco.engine.begin() as conn, pytest.raises(IntegrityError):
            self._insere_categoria(conn, name_key="x" + str(len(valores)), **valores)

    def test_categoria_de_grupo_inexistente_e_barrada_pela_chave_estrangeira(self, banco):
        with banco.engine.begin() as conn, pytest.raises(IntegrityError):
            self._insere_categoria(conn, group_id=uuid4(), name_key="orfa")

    def test_nao_se_apaga_um_grupo_que_ainda_tem_categorias(self, banco):
        with banco.engine.begin() as conn, pytest.raises(IntegrityError):
            conn.execute(text("DELETE FROM scope_groups"))

    def test_avaliacao_repetida_para_o_mesmo_perfil_e_barrada(self, banco):
        with banco.engine.begin() as conn:
            categoria = conn.execute(select(scope_categories.c.id)).scalars().first()
            with pytest.raises(IntegrityError):
                conn.execute(
                    insert(scope_evaluations).values(
                        id=uuid4(),
                        created_at=datetime(2026, 10, 28, tzinfo=UTC),
                        updated_at=datetime(2026, 10, 28, tzinfo=UTC),
                        version=1,
                        category_id=categoria,
                        profile="Noivo",
                    )
                )

    @pytest.mark.parametrize(
        ("perfil", "prioridade"),
        [("Ambos", None), ("Noiva", "Talvez"), ("Qualquer", None)],
    )
    def test_avaliacao_com_perfil_ou_prioridade_invalidos_e_barrada(
        self, banco, perfil, prioridade
    ):
        # Numa categoria nova, para a falha vir do CHECK e não do par repetido.
        with banco.engine.begin() as conn:
            nova = uuid4()
            self._insere_categoria(conn, id=nova, name_key="avaliada")
            with pytest.raises(IntegrityError, match="CHECK"):
                conn.execute(
                    text(
                        "INSERT INTO scope_evaluations (id, created_at, updated_at, version, "
                        "category_id, profile, priority) VALUES (:id, '2026-10-28', '2026-10-28', "
                        "1, :cat, :perfil, :prioridade)"
                    ),
                    {
                        "id": uuid4().hex,
                        "cat": nova.hex,
                        "perfil": perfil,
                        "prioridade": prioridade,
                    },
                )

    @pytest.mark.parametrize(
        ("de", "para", "motivo"),
        [
            ("Em discussão", "Em discussão", None),
            ("Em discussão", "Fica de fora", None),
            ("Em discussão", "Fica de fora", "   "),
        ],
    )
    def test_mudanca_de_status_sem_mudar_ou_descartando_sem_motivo_e_barrada(
        self, banco, de, para, motivo
    ):
        with banco.engine.begin() as conn:
            categoria = conn.execute(select(scope_categories.c.id)).scalars().first()
            with pytest.raises(IntegrityError):
                conn.execute(
                    text(
                        "INSERT INTO scope_status_changes (id, created_at, updated_at, version, "
                        "category_id, from_status, to_status, reason, profile) VALUES (:id, "
                        "'2026-10-28', '2026-10-28', 1, :cat, :de, :para, :motivo, 'Noivo')"
                    ),
                    {
                        "id": uuid4().hex,
                        "cat": categoria.hex,
                        "de": de,
                        "para": para,
                        "motivo": motivo,
                    },
                )
