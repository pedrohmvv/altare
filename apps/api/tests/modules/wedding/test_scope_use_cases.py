from uuid import uuid4

import pytest
from tests.modules.wedding.conftest import NOIVA, NOIVO

from wedding.modules.wedding.application.commands.change_scope_status import (
    ChangeScopeStatusCommand,
)
from wedding.modules.wedding.application.commands.create_scope_category import (
    CreateScopeCategoryCommand,
)
from wedding.modules.wedding.application.commands.create_scope_group import CreateScopeGroupCommand
from wedding.modules.wedding.application.commands.delete_scope_category import (
    DeleteScopeCategoryCommand,
)
from wedding.modules.wedding.application.commands.delete_scope_group import DeleteScopeGroupCommand
from wedding.modules.wedding.application.commands.rename_scope_group import RenameScopeGroupCommand
from wedding.modules.wedding.application.commands.set_my_evaluation import SetMyEvaluationCommand
from wedding.modules.wedding.application.commands.set_scope_category_visibility import (
    SetScopeCategoryVisibilityCommand,
)
from wedding.modules.wedding.application.commands.set_scope_group_visibility import (
    SetScopeGroupVisibilityCommand,
)
from wedding.modules.wedding.application.commands.update_scope_category import (
    UpdateScopeCategoryCommand,
)
from wedding.modules.wedding.application.scope_dto import CategoryDto, GroupDto, ScopeMapDto
from wedding.modules.wedding.domain.errors import (
    CatalogItemNotDeletable,
    DiscardReasonRequired,
    DuplicateScopeName,
    GroupNotEmpty,
    InvalidScopeValue,
)
from wedding.modules.wedding.domain.scope_rules import AlignmentState
from wedding.modules.wedding.domain.scope_values import Priority, ScopeStatus
from wedding.shared_kernel.errors import NotFound, VersionConflict
from wedding.shared_kernel.profile import ProfileKind


def group_of(mapa: ScopeMapDto, nome: str) -> GroupDto:
    return next(g for g in mapa.groups if g.name == nome)


def category_of(mapa: ScopeMapDto, nome: str) -> CategoryDto:
    return next(c for g in mapa.groups for c in g.categories if c.name == nome)


def novo_grupo(world, nome="Grupo Exemplo", ator=NOIVO) -> GroupDto:
    mapa = world.scope_use_cases().create_scope_group.execute(CreateScopeGroupCommand(nome), ator)
    return group_of(mapa, nome)


def nova_categoria(world, grupo: GroupDto, nome="Frente Exemplo", estimativa=None, ator=NOIVO):
    mapa = world.scope_use_cases().create_scope_category.execute(
        CreateScopeCategoryCommand(grupo.id, nome, estimativa), ator
    )
    return category_of(mapa, nome)


def mudar_status(world, cat, status, motivo=None, ator=NOIVO, versao=None):
    return world.scope_use_cases().change_scope_status.execute(
        ChangeScopeStatusCommand(cat.id, status, motivo, cat.version if versao is None else versao),
        ator,
    )


class TestGrupos:
    def test_cria_grupo_no_fim_e_o_mapa_o_mostra(self, world):
        a = novo_grupo(world, "Primeiro Exemplo")
        b = novo_grupo(world, "Segundo Exemplo")
        assert (a.position, b.position) == (0, 1)
        assert (b.origin.value, b.hidden, b.version, b.can_delete) == ("casal", False, 1, True)

    def test_nome_repetido_sem_diferenciar_caixa_e_recusado(self, world):  # F-PLN-02
        novo_grupo(world, "Pós-festa")
        with pytest.raises(DuplicateScopeName):
            novo_grupo(world, "  PÓS-FESTA ")

    def test_nome_invalido_e_recusado(self, world):
        with pytest.raises(InvalidScopeValue):
            novo_grupo(world, "   ")

    def test_renomear_exige_a_versao_vista_e_respeita_o_nome_unico(self, world):
        a, b = novo_grupo(world, "A Exemplo"), novo_grupo(world, "B Exemplo")
        uc = world.scope_use_cases()
        mapa = uc.rename_scope_group.execute(
            RenameScopeGroupCommand(a.id, "Novo Exemplo", 1), NOIVA
        )
        assert group_of(mapa, "Novo Exemplo").version == 2
        with pytest.raises(VersionConflict):
            uc.rename_scope_group.execute(RenameScopeGroupCommand(a.id, "Outro Exemplo", 1), NOIVO)
        with pytest.raises(DuplicateScopeName):
            uc.rename_scope_group.execute(RenameScopeGroupCommand(b.id, "novo exemplo", 1), NOIVO)

    def test_renomear_para_o_mesmo_nome_nao_sobe_a_versao(self, world):
        a = novo_grupo(world, "A Exemplo")
        mapa = world.scope_use_cases().rename_scope_group.execute(
            RenameScopeGroupCommand(a.id, " A  Exemplo ", 1), NOIVO
        )
        assert group_of(mapa, "A Exemplo").version == 1

    def test_ocultar_grupo_esconde_as_frentes_dele_sem_mudar_nenhuma(self, world):
        grupo = novo_grupo(world)
        cat = nova_categoria(world, grupo)
        mapa = world.scope_use_cases().set_scope_group_visibility.execute(
            SetScopeGroupVisibilityCommand(grupo.id, True, grupo.version), NOIVO
        )
        assert group_of(mapa, "Grupo Exemplo").hidden is True
        filha = category_of(mapa, "Frente Exemplo")
        assert (filha.hidden, filha.visible, filha.version) == (False, False, cat.version)
        assert mapa.progress.total == 0

    def test_excluir_grupo_do_catalogo_e_proibido(self, world):
        grupo_id, _ = world.seed_catalog()
        with pytest.raises(CatalogItemNotDeletable):
            world.scope_use_cases().delete_scope_group.execute(
                DeleteScopeGroupCommand(grupo_id, 1), NOIVO
            )

    def test_excluir_grupo_com_categorias_e_recusado_e_vazio_sai(self, world):
        grupo = novo_grupo(world)
        cat = nova_categoria(world, grupo)
        uc = world.scope_use_cases()
        with pytest.raises(GroupNotEmpty):
            uc.delete_scope_group.execute(DeleteScopeGroupCommand(grupo.id, grupo.version), NOIVO)
        assert group_of(uc.get_scope_map.execute(NOIVO), "Grupo Exemplo").can_delete is False
        uc.delete_scope_category.execute(DeleteScopeCategoryCommand(cat.id, cat.version), NOIVO)
        mapa = uc.delete_scope_group.execute(DeleteScopeGroupCommand(grupo.id, 1), NOIVO)
        assert [g.name for g in mapa.groups] == []

    def test_excluir_grupo_com_versao_velha_da_conflito(self, world):
        grupo = novo_grupo(world)
        with pytest.raises(VersionConflict):
            world.scope_use_cases().delete_scope_group.execute(
                DeleteScopeGroupCommand(grupo.id, 7), NOIVO
            )

    def test_grupo_inexistente_e_nao_encontrado(self, world):
        with pytest.raises(NotFound):
            world.scope_use_cases().rename_scope_group.execute(
                RenameScopeGroupCommand(uuid4(), "X Exemplo", 1), NOIVO
            )


class TestCategorias:
    def test_nasce_em_discussao_sem_estimativa_e_com_o_par_de_avaliacoes(self, world):
        cat = nova_categoria(world, novo_grupo(world))
        assert cat.status is ScopeStatus.IN_DISCUSSION
        assert cat.estimate_cents is None
        assert (cat.noivo.priority, cat.noiva.priority) == (None, None)
        assert (cat.noivo.version, cat.noiva.version, cat.version) == (1, 1, 1)
        assert cat.alignment.state is AlignmentState.MISSING
        assert cat.alignment.missing == (ProfileKind.NOIVO, ProfileKind.NOIVA)

    def test_estimativa_na_criacao_e_guardada(self, world):
        cat = nova_categoria(world, novo_grupo(world), estimativa=2_800_000)
        assert cat.estimate_cents == 2_800_000

    def test_grupo_inexistente_e_nome_repetido_em_qualquer_grupo(self, world):
        a, b = novo_grupo(world, "A Exemplo"), novo_grupo(world, "B Exemplo")
        nova_categoria(world, a, "Fotografia")
        uc = world.scope_use_cases()
        with pytest.raises(NotFound):
            uc.create_scope_category.execute(CreateScopeCategoryCommand(uuid4(), "X", None), NOIVO)
        with pytest.raises(DuplicateScopeName):
            uc.create_scope_category.execute(
                CreateScopeCategoryCommand(b.id, "fotografia", None), NOIVO
            )

    def test_nome_de_categoria_oculta_continua_ocupado(self, world):  # F-PLN-02, regra 3
        grupo = novo_grupo(world)
        cat = nova_categoria(world, grupo, "Fotografia")
        uc = world.scope_use_cases()
        uc.set_scope_category_visibility.execute(
            SetScopeCategoryVisibilityCommand(cat.id, True, cat.version), NOIVO
        )
        with pytest.raises(DuplicateScopeName):
            nova_categoria(world, grupo, "FOTOGRAFIA")

    def test_atualiza_nome_grupo_e_estimativa_de_uma_vez(self, world):
        a, b = novo_grupo(world, "A Exemplo"), novo_grupo(world, "B Exemplo")
        cat = nova_categoria(world, a, "Vídeo")
        mapa = world.scope_use_cases().update_scope_category.execute(
            UpdateScopeCategoryCommand(cat.id, "Vídeo e drone", b.id, 150_000, cat.version), NOIVA
        )
        nova = category_of(mapa, "Vídeo e drone")
        assert (nova.group_id, nova.estimate_cents, nova.version) == (b.id, 150_000, 2)

    def test_atualizar_sem_mudar_nada_nao_sobe_a_versao_e_o_proprio_nome_nao_colide(self, world):
        grupo = novo_grupo(world)
        cat = nova_categoria(world, grupo, "Vídeo")
        mapa = world.scope_use_cases().update_scope_category.execute(
            UpdateScopeCategoryCommand(cat.id, " Vídeo ", grupo.id, None, cat.version), NOIVO
        )
        assert category_of(mapa, "Vídeo").version == 1

    def test_atualizar_para_nome_de_outra_estimativa_invalida_ou_grupo_ausente(self, world):
        grupo = novo_grupo(world)
        a, b = nova_categoria(world, grupo, "A Exemplo"), nova_categoria(world, grupo, "B Exemplo")
        uc = world.scope_use_cases()
        with pytest.raises(DuplicateScopeName):
            uc.update_scope_category.execute(
                UpdateScopeCategoryCommand(a.id, "b exemplo", grupo.id, None, 1), NOIVO
            )
        with pytest.raises(InvalidScopeValue):
            uc.update_scope_category.execute(
                UpdateScopeCategoryCommand(a.id, "A Exemplo", grupo.id, 0, 1), NOIVO
            )
        with pytest.raises(NotFound):
            uc.update_scope_category.execute(
                UpdateScopeCategoryCommand(b.id, "B Exemplo", uuid4(), None, 1), NOIVO
            )
        with pytest.raises(VersionConflict):
            uc.update_scope_category.execute(
                UpdateScopeCategoryCommand(b.id, "B Exemplo", grupo.id, None, 9), NOIVO
            )

    def test_ocultar_e_mostrar_de_novo_mantem_tudo_e_vale_para_o_catalogo(self, world):
        _, cat_id = world.seed_catalog()
        uc = world.scope_use_cases()
        mapa = uc.set_scope_category_visibility.execute(
            SetScopeCategoryVisibilityCommand(cat_id, True, 1), NOIVO
        )
        cat = category_of(mapa, "Cerimônia civil")
        assert (cat.hidden, cat.visible) == (True, False)
        mapa = uc.set_scope_category_visibility.execute(
            SetScopeCategoryVisibilityCommand(cat_id, False, cat.version), NOIVA
        )
        assert category_of(mapa, "Cerimônia civil").visible is True

    def test_categoria_do_catalogo_nao_e_excluida_e_a_do_casal_sai_liberando_o_nome(self, world):
        _, catalogo_id = world.seed_catalog()
        uc = world.scope_use_cases()
        with pytest.raises(CatalogItemNotDeletable):
            uc.delete_scope_category.execute(DeleteScopeCategoryCommand(catalogo_id, 1), NOIVO)
        grupo = novo_grupo(world)
        cat = nova_categoria(world, grupo, "Fotografia")
        mapa = uc.delete_scope_category.execute(
            DeleteScopeCategoryCommand(cat.id, cat.version), NOIVO
        )
        assert [c.name for g in mapa.groups for c in g.categories if g.name == grupo.name] == []
        nova_categoria(world, grupo, "Fotografia")


class TestStatus:
    def test_entra_e_talvez_mudam_sem_motivo(self, world):
        cat = nova_categoria(world, novo_grupo(world))
        mapa = mudar_status(world, cat, ScopeStatus.ESSENTIAL, ator=NOIVA)
        assert category_of(mapa, "Frente Exemplo").status is ScopeStatus.ESSENTIAL

    def test_fica_de_fora_sem_motivo_e_bloqueado_sem_historico_nem_versao(self, world):
        cat = nova_categoria(world, novo_grupo(world))
        with pytest.raises(DiscardReasonRequired):
            mudar_status(world, cat, ScopeStatus.OUT, "  ")
        uc = world.scope_use_cases()
        assert uc.list_scope_category_history.execute(cat.id, NOIVO) == []
        assert category_of(uc.get_scope_map.execute(NOIVO), "Frente Exemplo").version == 1

    def test_historico_lista_quem_mudou_o_que_do_mais_novo_ao_mais_antigo(self, world, clock):
        cat = nova_categoria(world, novo_grupo(world))
        mudar_status(world, cat, ScopeStatus.ESSENTIAL, ator=NOIVO)
        clock.advance(hours=1)
        mapa = mudar_status(
            world,
            category_of(world.scope_use_cases().get_scope_map.execute(NOIVO), "Frente Exemplo"),
            ScopeStatus.OUT,
            " não cabe ",
            ator=NOIVA,
        )
        recente, antiga = world.scope_use_cases().list_scope_category_history.execute(cat.id, NOIVO)
        assert (recente.from_status, recente.to_status, recente.reason) == (
            ScopeStatus.ESSENTIAL,
            ScopeStatus.OUT,
            "não cabe",
        )
        assert recente.profile is ProfileKind.NOIVA
        assert (antiga.from_status, antiga.to_status, antiga.profile) == (
            ScopeStatus.IN_DISCUSSION,
            ScopeStatus.ESSENTIAL,
            ProfileKind.NOIVO,
        )
        assert recente.changed_at > antiga.changed_at
        assert category_of(mapa, "Frente Exemplo").discard_reason == "não cabe"

    def test_o_motivo_so_vale_para_fica_de_fora(self, world):
        cat = nova_categoria(world, novo_grupo(world))
        mudar_status(world, cat, ScopeStatus.MAYBE, "lixo que ninguém pediu")
        (mudanca,) = world.scope_use_cases().list_scope_category_history.execute(cat.id, NOIVO)
        assert mudanca.reason is None

    def test_reabrir_mostra_o_motivo_do_descarte_anterior_e_o_historico_o_guarda(
        self, world
    ):  # F-PLN-03
        cat = nova_categoria(world, novo_grupo(world))
        mudar_status(world, cat, ScopeStatus.OUT, "fora do teto")
        atual = category_of(world.scope_use_cases().get_scope_map.execute(NOIVO), "Frente Exemplo")
        mapa = mudar_status(world, atual, ScopeStatus.IN_DISCUSSION)
        reaberta = category_of(mapa, "Frente Exemplo")
        assert reaberta.status is ScopeStatus.IN_DISCUSSION
        assert reaberta.discard_reason == "fora do teto"
        assert len(world.scope_use_cases().list_scope_category_history.execute(cat.id, NOIVO)) == 2

    def test_repetir_o_status_nao_grava_historico_nem_sobe_a_versao(self, world):
        cat = nova_categoria(world, novo_grupo(world))
        mapa = mudar_status(world, cat, ScopeStatus.IN_DISCUSSION)
        assert category_of(mapa, "Frente Exemplo").version == 1
        assert world.scope_use_cases().list_scope_category_history.execute(cat.id, NOIVO) == []

    def test_versao_velha_da_conflito_e_nao_muda_nada(self, world):
        cat = nova_categoria(world, novo_grupo(world))
        mudar_status(world, cat, ScopeStatus.ESSENTIAL)
        with pytest.raises(VersionConflict):
            mudar_status(world, cat, ScopeStatus.MAYBE, ator=NOIVA)  # `cat` ainda é a versão 1
        atual = category_of(world.scope_use_cases().get_scope_map.execute(NOIVO), "Frente Exemplo")
        assert atual.status is ScopeStatus.ESSENTIAL

    def test_historico_de_categoria_inexistente_e_nao_encontrado(self, world):
        with pytest.raises(NotFound):
            world.scope_use_cases().list_scope_category_history.execute(uuid4(), NOIVO)


class TestAvaliacao:
    def avaliar(self, world, cat, prioridade, nota=None, ator=NOIVO, versao=None):
        evaluation = cat.noivo if ator.profile is ProfileKind.NOIVO else cat.noiva
        return world.scope_use_cases().set_my_evaluation.execute(
            SetMyEvaluationCommand(
                cat.id, prioridade, nota, evaluation.version if versao is None else versao
            ),
            ator,
        )

    def test_cada_perfil_edita_so_a_propria_avaliacao(self, world):  # F-PLN-04
        cat = nova_categoria(world, novo_grupo(world))
        mapa = self.avaliar(world, cat, Priority.WANT_A_LOT, "quero muito", ator=NOIVA)
        feita = category_of(mapa, "Frente Exemplo")
        assert (feita.noiva.priority, feita.noiva.note, feita.noiva.version) == (
            Priority.WANT_A_LOT,
            "quero muito",
            2,
        )
        assert (feita.noivo.priority, feita.noivo.note, feita.noivo.version) == (None, None, 1)

    def test_falta_diz_quem_falta_diverge_e_alinha(self, world):
        cat = nova_categoria(world, novo_grupo(world))
        mapa = self.avaliar(world, cat, Priority.IF_FITS, ator=NOIVO)
        parcial = category_of(mapa, "Frente Exemplo")
        assert parcial.alignment.state is AlignmentState.MISSING
        assert parcial.alignment.missing == (ProfileKind.NOIVA,)
        mapa = self.avaliar(world, parcial, Priority.DISPENSE, ator=NOIVA)
        assert category_of(mapa, "Frente Exemplo").alignment.state is AlignmentState.DIVERGENT
        cat2 = category_of(mapa, "Frente Exemplo")
        mapa = self.avaliar(world, cat2, Priority.IF_FITS, ator=NOIVA)
        assert category_of(mapa, "Frente Exemplo").alignment.state is AlignmentState.ALIGNED

    def test_a_avaliacao_nao_muda_o_status_conjunto(self, world):  # F-PLN-04, regra 2
        cat = nova_categoria(world, novo_grupo(world))
        mapa = self.avaliar(world, cat, Priority.DISPENSE)
        assert category_of(mapa, "Frente Exemplo").status is ScopeStatus.IN_DISCUSSION

    def test_versao_velha_da_conflito_e_nota_longa_e_recusada_e_categoria_ausente(self, world):
        cat = nova_categoria(world, novo_grupo(world))
        self.avaliar(world, cat, Priority.IF_FITS)
        with pytest.raises(VersionConflict):
            self.avaliar(world, cat, Priority.DISPENSE, versao=1)
        atual = category_of(world.scope_use_cases().get_scope_map.execute(NOIVO), "Frente Exemplo")
        with pytest.raises(InvalidScopeValue):
            self.avaliar(world, atual, None, "x" * 501)
        with pytest.raises(NotFound):
            world.scope_use_cases().set_my_evaluation.execute(
                SetMyEvaluationCommand(uuid4(), None, None, 1), NOIVO
            )

    def test_repetir_a_mesma_avaliacao_nao_sobe_a_versao(self, world):
        cat = nova_categoria(world, novo_grupo(world))
        self.avaliar(world, cat, Priority.IF_FITS, "ok")
        atual = category_of(world.scope_use_cases().get_scope_map.execute(NOIVO), "Frente Exemplo")
        mapa = self.avaliar(world, atual, Priority.IF_FITS, "ok")
        assert category_of(mapa, "Frente Exemplo").noivo.version == 2


class TestMapa:
    def test_progresso_e_totais_acompanham_status_estimativa_e_visibilidade(
        self, world
    ):  # F-PLN-05
        grupo = novo_grupo(world)
        a = nova_categoria(world, grupo, "A Exemplo", 100)
        b = nova_categoria(world, grupo, "B Exemplo")
        c = nova_categoria(world, grupo, "C Exemplo", 50)
        nova_categoria(world, grupo, "D Exemplo", 999)
        mudar_status(world, a, ScopeStatus.ESSENTIAL)
        mudar_status(world, b, ScopeStatus.ESSENTIAL)
        mapa = mudar_status(world, c, ScopeStatus.MAYBE)
        assert (mapa.progress.classified, mapa.progress.total) == (3, 4)
        assert (mapa.totals.essential_cents, mapa.totals.essential_without_estimate) == (100, 1)
        assert (mapa.totals.maybe_cents, mapa.totals.maybe_without_estimate) == (50, 0)
        mapa = world.scope_use_cases().set_scope_category_visibility.execute(
            SetScopeCategoryVisibilityCommand(a.id, True, category_of(mapa, "A Exemplo").version),
            NOIVO,
        )
        assert (mapa.progress.classified, mapa.progress.total) == (2, 3)
        assert mapa.totals.essential_cents == 0

    def test_grupos_e_categorias_saem_na_ordem_de_posicao(self, world):
        a, b = novo_grupo(world, "Z Exemplo"), novo_grupo(world, "A Exemplo")
        nova_categoria(world, a, "Y Exemplo")
        nova_categoria(world, a, "B Exemplo")
        mapa = world.scope_use_cases().get_scope_map.execute(NOIVO)
        assert [g.name for g in mapa.groups] == ["Z Exemplo", "A Exemplo"]
        assert [c.name for c in mapa.groups[0].categories] == ["Y Exemplo", "B Exemplo"]
        assert b.position == 1

    def test_o_ator_da_sessao_vai_para_a_transacao(self, world):
        novo_grupo(world, ator=NOIVA)
        assert world.actors[-1] == NOIVA
