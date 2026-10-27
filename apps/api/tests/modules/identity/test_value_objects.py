import pytest
from hypothesis import given
from hypothesis import strategies as st

from wedding.modules.identity.domain.errors import InvalidUsername, WeakPassword
from wedding.modules.identity.domain.value_objects import (
    hash_token,
    normalize_username,
    validate_password,
    validate_username,
)


def test_usuario_e_guardado_sem_espacos_e_em_minusculas():
    assert normalize_username("  Exemplo.Noivo ") == "exemplo.noivo"


@pytest.mark.parametrize("usuario", ["exemplo.noivo", "a_b-c.9", "abc", "x" * 32])
def test_usuario_valido(usuario):
    validate_username(usuario)


@pytest.mark.parametrize(
    "usuario", ["", "ab", "x" * 33, "com espaço", "acentuação", "Maiuscula", "x/y", "a@b"]
)
def test_usuario_invalido_e_recusado(usuario):
    with pytest.raises(InvalidUsername) as erro:
        validate_username(usuario)
    assert erro.value.code == "invalid_username"


@pytest.mark.parametrize("senha", ["a" * 12, "a" * 128, "uma frase longa com espaços"])
def test_senha_dentro_dos_limites_nao_exige_composicao(senha):
    validate_password(senha)


@pytest.mark.parametrize("senha", ["", "a" * 11, "a" * 129])
def test_senha_fora_dos_limites_e_fraca(senha):
    with pytest.raises(WeakPassword) as erro:
        validate_password(senha)
    assert erro.value.code == "weak_password"


@given(senha=st.text(min_size=12, max_size=128))
def test_qualquer_senha_de_12_a_128_caracteres_e_aceita(senha):
    validate_password(senha)


@given(senha=st.one_of(st.text(max_size=11), st.text(min_size=129, max_size=300)))
def test_qualquer_senha_fora_de_12_a_128_caracteres_e_recusada(senha):
    with pytest.raises(WeakPassword):
        validate_password(senha)


def test_hash_do_token_e_sha256_em_hexadecimal():
    assert hash_token("abc") == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


@given(a=st.text(min_size=1), b=st.text(min_size=1))
def test_tokens_diferentes_dao_hashes_diferentes(a, b):
    assert (hash_token(a) == hash_token(b)) == (a == b)
