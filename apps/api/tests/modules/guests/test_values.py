import pytest
from hypothesis import given
from hypothesis import strategies as st

from wedding.modules.guests.domain.errors import GuestNameRequired, InvalidGuestValue
from wedding.modules.guests.domain.values import (
    AgeBand,
    clean_age,
    clean_guest_name,
    clean_household_name,
    clean_state,
    clean_text,
    name_key,
)


def test_nome_do_nucleo_igual_sem_diferenciar_caixa_nem_espacos():  # F-CNV-01
    assert name_key("Família Exemplo") == name_key("  FAMÍLIA   exemplo ")


def test_acento_continua_diferente_na_chave_do_nome():
    assert name_key("Familia Exemplo") != name_key("Família Exemplo")


@given(st.text())
def test_a_chave_do_nome_e_idempotente(texto):
    assert name_key(name_key(texto)) == name_key(texto)


def test_nome_do_nucleo_colapsa_espacos():
    assert clean_household_name("  Família   Exemplo ") == "Família Exemplo"


@pytest.mark.parametrize("nome", ["", "   ", "x" * 81])
def test_nome_do_nucleo_vazio_ou_longo_e_recusado(nome):
    with pytest.raises(InvalidGuestValue):
        clean_household_name(nome)


def test_nome_do_convidado_e_obrigatorio_fora_do_acompanhante():
    with pytest.raises(GuestNameRequired):
        clean_guest_name("  ", required=True)
    assert clean_guest_name("  ", required=False) is None
    assert clean_guest_name(None, required=False) is None


def test_nome_do_convidado_longo_e_recusado_mesmo_no_acompanhante():
    with pytest.raises(InvalidGuestValue):
        clean_guest_name("x" * 81, required=False)


def test_texto_livre_perde_espacos_e_vazio_vira_nulo():
    assert clean_text("  sem glúten ", 120) == "sem glúten"
    assert clean_text("   ", 120) is None
    assert clean_text(None, 120) is None


def test_texto_livre_acima_do_limite_e_recusado():
    with pytest.raises(InvalidGuestValue):
        clean_text("x" * 121, 120)


def test_uf_normaliza_e_so_aceita_estado_brasileiro():
    assert clean_state(" sp ") == "SP"
    assert clean_state("") is None
    with pytest.raises(InvalidGuestValue):
        clean_state("XX")


@pytest.mark.parametrize("faixa", [AgeBand.PAYING_CHILD, AgeBand.EXEMPT_CHILD])
def test_idade_vale_para_crianca_de_0_a_17(faixa):  # F-CNV-03, regra 1
    assert clean_age(0, faixa) == 0
    assert clean_age(17, faixa) == 17
    assert clean_age(None, faixa) is None
    for idade in (-1, 18, True, 4.5):
        with pytest.raises(InvalidGuestValue):
            clean_age(idade, faixa)  # type: ignore[arg-type]


def test_idade_de_adulto_e_recusada():
    assert clean_age(None, AgeBand.ADULT) is None
    with pytest.raises(InvalidGuestValue):
        clean_age(30, AgeBand.ADULT)
