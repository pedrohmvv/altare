import pytest
from hypothesis import given
from hypothesis import strategies as st

from wedding.modules.guests.domain.contact import (
    clean_email,
    clean_postal_code,
    format_phone,
    format_postal_code,
    normalize_phone,
    whatsapp_url,
)
from wedding.modules.guests.domain.errors import InvalidEmail, InvalidGuestValue, InvalidPhone


def test_telefone_da_spec_gera_o_link_do_whatsapp():  # F-CNV-01
    phone = normalize_phone("(11) 91234-5678")

    assert phone == "11912345678"
    assert whatsapp_url(phone) == "https://wa.me/5511912345678"


@pytest.mark.parametrize(
    "texto",
    ["11912345678", "+55 11 91234-5678", "55 (11) 91234 5678", "011 91234-5678", " 11.91234.5678 "],
)
def test_formatos_comuns_do_mesmo_celular_normalizam_igual(texto):
    assert normalize_phone(texto) == "11912345678"


def test_telefone_vazio_e_nulo_nunca_invalido():
    assert normalize_phone(None) is None
    assert normalize_phone("   ") is None
    assert whatsapp_url(None) is None


def test_telefone_fixo_vale_mas_nao_gera_link():  # decisão 1 do plano (D-071)
    phone = normalize_phone("(11) 3456-7890")

    assert phone == "1134567890"
    assert whatsapp_url(phone) is None


@pytest.mark.parametrize(
    "texto",
    [
        "1234",
        "(11) 81234-5678",  # celular sem o 9 inicial
        "(00) 91234-5678",  # DDD inexistente
        "(01) 91234-5678",
        "(11) 91234-56789",  # número a mais
        "ligar depois",
        "11 91234-5678 ramal 2",
        "+1 202 555 0100",
    ],
)
def test_telefone_invalido_e_recusado(texto):
    with pytest.raises(InvalidPhone):
        normalize_phone(texto)


def test_telefone_formatado_para_exibir():
    assert format_phone("11912345678") == "(11) 91234-5678"
    assert format_phone("1134567890") == "(11) 3456-7890"


@given(
    ddd=st.integers(11, 99).filter(lambda d: d % 10 != 0),
    resto=st.integers(0, 10**8 - 1),
)
def test_link_do_whatsapp_existe_exatamente_para_celular_valido(ddd, resto):
    celular = f"{ddd}9{resto:08d}"

    phone = normalize_phone(celular)

    assert whatsapp_url(phone) == f"https://wa.me/55{celular}"
    assert normalize_phone(format_phone(celular)) == celular


@given(st.text(max_size=30))
def test_normalizar_telefone_ou_devolve_digitos_validos_ou_recusa(texto):
    try:
        phone = normalize_phone(texto)
    except InvalidPhone:
        return
    if phone is not None:
        assert phone.isdigit()
        assert len(phone) in (10, 11)
        assert (whatsapp_url(phone) is not None) == (len(phone) == 11)


def test_email_so_confere_o_formato():
    assert clean_email("  convidado@exemplo.invalid ") == "convidado@exemplo.invalid"
    assert clean_email("") is None
    assert clean_email(None) is None


@pytest.mark.parametrize(
    "texto",
    ["convidado", "convidado@", "@exemplo.invalid", "a b@exemplo.invalid", "a@b", "a@@b.com"],
)
def test_email_fora_do_formato_e_recusado(texto):
    with pytest.raises(InvalidEmail):
        clean_email(texto)


def test_email_longo_demais_e_recusado():
    with pytest.raises(InvalidEmail):
        clean_email("a" * 250 + "@exemplo.invalid")


def test_cep_aceita_so_o_formato_de_8_digitos():
    assert clean_postal_code("00000-000") == "00000000"
    assert clean_postal_code("00000000") == "00000000"
    assert clean_postal_code("") is None
    assert format_postal_code("00000000") == "00000-000"


@pytest.mark.parametrize("texto", ["0000-000", "000000000", "abcde-fgh"])
def test_cep_fora_do_formato_e_recusado(texto):
    with pytest.raises(InvalidGuestValue):
        clean_postal_code(texto)
