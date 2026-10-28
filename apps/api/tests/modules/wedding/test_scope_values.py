import pytest
from hypothesis import given
from hypothesis import strategies as st

from wedding.modules.wedding.domain.errors import InvalidScopeValue
from wedding.modules.wedding.domain.scope_values import (
    clean_estimate,
    clean_name,
    clean_note,
    clean_reason,
    name_key,
)


def test_nome_igual_sem_diferenciar_maiusculas_nem_espacos():  # F-PLN-02, regra 3
    assert name_key("Fotografia") == name_key("  fotografia ") == name_key("FOTOGRAFIA")
    assert name_key("Bolo  e   doces") == name_key("bolo e doces")


def test_acentos_continuam_diferentes():
    assert name_key("Condução") != name_key("Conducao")


@given(st.text())
def test_a_chave_do_nome_e_idempotente(texto):
    assert name_key(name_key(texto)) == name_key(texto)


def test_nome_perde_espacos_e_colapsa_os_do_meio():
    assert clean_name("  Bolo   e doces ") == "Bolo e doces"


@pytest.mark.parametrize("nome", ["", "   ", "x" * 61])
def test_nome_vazio_ou_longo_e_recusado(nome):
    with pytest.raises(InvalidScopeValue):
        clean_name(nome)


def test_nome_de_60_caracteres_vale():
    assert clean_name("x" * 60) == "x" * 60


def test_estimativa_vazia_e_nula_nunca_zero():  # F-PLN-05
    assert clean_estimate(None) is None


@pytest.mark.parametrize("centavos", [0, -1, 10**12 + 1, True, 10.5])
def test_estimativa_zero_negativa_enorme_ou_nao_inteira_e_recusada(centavos):
    with pytest.raises(InvalidScopeValue):
        clean_estimate(centavos)  # type: ignore[arg-type]


def test_estimativa_valida():
    assert clean_estimate(1) == 1
    assert clean_estimate(2_800_000) == 2_800_000
    assert clean_estimate(10**12) == 10**12


def test_motivo_e_nota_perdem_espacos_e_em_branco_vira_nada():
    assert clean_reason("  não cabe  ") == "não cabe"
    assert clean_reason("   ") is None
    assert clean_reason(None) is None
    assert clean_note("  oi ") == "oi"
    assert clean_note("") is None


def test_motivo_passa_de_300_e_nota_passa_de_500_sao_recusados():
    with pytest.raises(InvalidScopeValue):
        clean_reason("x" * 301)
    with pytest.raises(InvalidScopeValue):
        clean_note("x" * 501)
