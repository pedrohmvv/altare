from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from wedding.modules.wedding.domain.errors import (
    CatalogItemNotDeletable,
    DiscardReasonRequired,
    InvalidScopeValue,
)
from wedding.modules.wedding.domain.scope_entities import (
    ScopeCategory,
    ScopeEvaluation,
    ScopeGroup,
)
from wedding.modules.wedding.domain.scope_values import Origin, Priority, ScopeStatus
from wedding.shared_kernel.profile import ProfileKind

AGORA = datetime(2026, 10, 28, 12, 0, tzinfo=UTC)
GRUPO = UUID(int=1)


def _categoria(origin=Origin.COUPLE, name="Fotografia") -> ScopeCategory:
    return ScopeCategory(id=uuid4(), group_id=GRUPO, name=name, position=1, origin=origin)


def test_categoria_nasce_em_discussao_sem_estimativa_e_com_a_chave_do_nome():
    categoria = _categoria(name="  Bolo   e doces ")
    assert categoria.status is ScopeStatus.IN_DISCUSSION
    assert categoria.estimate_cents is None
    assert categoria.name == "Bolo e doces"
    assert categoria.name_key == "bolo e doces"


def test_categoria_com_nome_invalido_nao_existe():
    with pytest.raises(InvalidScopeValue):
        _categoria(name="   ")


@pytest.mark.parametrize("alvo", [ScopeStatus.ESSENTIAL, ScopeStatus.MAYBE])
def test_entra_e_talvez_nao_pedem_motivo(alvo):
    categoria = _categoria()
    assert categoria.change_status(alvo, None) is True
    assert categoria.status is alvo


def test_fica_de_fora_sem_motivo_e_bloqueado_e_o_status_nao_muda():  # F-PLN-03, regra 1
    categoria = _categoria()
    categoria.change_status(ScopeStatus.ESSENTIAL, None)
    for motivo in (None, "", "   "):
        with pytest.raises(DiscardReasonRequired):
            categoria.change_status(ScopeStatus.OUT, motivo)
    assert categoria.status is ScopeStatus.ESSENTIAL


def test_fica_de_fora_com_motivo_e_reabrir_e_permitido():  # F-PLN-03, regra 3
    categoria = _categoria()
    assert categoria.change_status(ScopeStatus.OUT, " não cabe no teto ") is True
    assert categoria.status is ScopeStatus.OUT
    assert categoria.change_status(ScopeStatus.IN_DISCUSSION, None) is True


def test_repetir_o_status_nao_conta_como_mudanca_nem_pede_motivo():
    categoria = _categoria()
    assert categoria.change_status(ScopeStatus.IN_DISCUSSION, None) is False
    categoria.change_status(ScopeStatus.OUT, "motivo")
    assert categoria.change_status(ScopeStatus.OUT, None) is False


def test_atualizar_nome_grupo_e_estimativa_diz_se_mudou():
    categoria = _categoria()
    outro_grupo = UUID(int=2)
    assert categoria.update("Vídeo", outro_grupo, 150_000) is True
    assert (categoria.name, categoria.name_key, categoria.group_id) == (
        "Vídeo",
        "vídeo",
        outro_grupo,
    )
    assert categoria.estimate_cents == 150_000
    assert categoria.update("  Vídeo ", outro_grupo, 150_000) is False
    assert (
        categoria.update("vídeo", outro_grupo, 150_000) is True
    )  # só a caixa mudou, mas é um renomear


def test_estimativa_pode_voltar_a_vazia():
    categoria = _categoria()
    categoria.update("Fotografia", GRUPO, 100)
    assert categoria.update("Fotografia", GRUPO, None) is True
    assert categoria.estimate_cents is None


def test_ocultar_e_mostrar_e_idempotente():
    categoria = _categoria()
    assert categoria.set_hidden(True, AGORA) is True
    assert categoria.hidden_at == AGORA
    assert categoria.set_hidden(True, AGORA) is False
    assert categoria.set_hidden(False, AGORA) is True
    assert categoria.hidden_at is None


def test_categoria_do_catalogo_nunca_e_excluida_e_a_do_casal_sim():  # F-PLN-02, regra 1
    with pytest.raises(CatalogItemNotDeletable):
        _categoria(Origin.CATALOG).delete(AGORA, uuid4())
    categoria = _categoria()
    autor = uuid4()
    categoria.delete(AGORA, autor)
    assert (categoria.deleted_at, categoria.deleted_by) == (AGORA, autor)


def test_grupo_segue_as_mesmas_regras_de_nome_ocultar_e_excluir():
    grupo = ScopeGroup(id=uuid4(), name=" Pós-festa ", position=1, origin=Origin.COUPLE)
    assert (grupo.name, grupo.name_key) == ("Pós-festa", "pós-festa")
    assert grupo.rename("Depois da festa") is True
    assert grupo.rename("  Depois da festa ") is False
    assert grupo.set_hidden(True, AGORA) is True
    with pytest.raises(CatalogItemNotDeletable):
        ScopeGroup(id=uuid4(), name="Cerimônia", position=0, origin=Origin.CATALOG).delete(
            AGORA, None
        )
    grupo.delete(AGORA, None)
    assert grupo.deleted_at == AGORA


def test_avaliacao_guarda_prioridade_e_nota_e_diz_se_mudou():
    avaliacao = ScopeEvaluation(id=uuid4(), category_id=GRUPO, profile=ProfileKind.NOIVA)
    assert avaliacao.priority is None
    assert avaliacao.update(Priority.WANT_A_LOT, "  quero muito  ") is True
    assert (avaliacao.priority, avaliacao.note) == (Priority.WANT_A_LOT, "quero muito")
    assert avaliacao.update(Priority.WANT_A_LOT, "quero muito") is False
    assert avaliacao.update(None, "") is True
    assert (avaliacao.priority, avaliacao.note) == (None, None)


def test_nota_longa_demais_e_recusada():
    avaliacao = ScopeEvaluation(id=uuid4(), category_id=GRUPO, profile=ProfileKind.NOIVO)
    with pytest.raises(InvalidScopeValue):
        avaliacao.update(None, "x" * 501)
