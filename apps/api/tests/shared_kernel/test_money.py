import pytest
from hypothesis import given
from hypothesis import strategies as st

from wedding.shared_kernel.money import Money

centavos = st.integers(min_value=0, max_value=10**11)


def test_soma_de_dois_valores_em_centavos():
    assert Money(1_000_00) + Money(250_50) == Money(1_250_50)


def test_subtracao_pode_ficar_negativa():
    assert Money(100) - Money(250) == Money(-150)


def test_multiplicacao_por_inteiro():
    assert Money(1_99) * 3 == Money(5_97)
    assert 3 * Money(1_99) == Money(5_97)


def test_negacao():
    assert -Money(500) == Money(-500)


def test_ordenacao_compara_centavos():
    assert Money(99) < Money(100)
    assert max(Money(5), Money(7)) == Money(7)


@pytest.mark.parametrize("invalido", [1.5, "10", None, True])
def test_rejeita_centavos_que_nao_sejam_inteiros(invalido):
    with pytest.raises(TypeError):
        Money(invalido)  # type: ignore[arg-type]


def test_nao_soma_com_inteiro_solto():
    with pytest.raises(TypeError):
        Money(100) + 100  # type: ignore[operator]


def test_nao_multiplica_por_float():
    with pytest.raises(TypeError):
        Money(100) * 1.5  # type: ignore[operator]


def test_divide_em_parcelas_iguais_com_o_resto_na_ultima():  # contratos-e-parcelas.md, F-CTR
    assert Money(100_00).split(3) == (Money(33_33), Money(33_33), Money(33_34))


def test_divide_sem_resto_quando_exato():
    assert Money(90_00).split(3) == (Money(30_00), Money(30_00), Money(30_00))


def test_divide_em_uma_parcela_devolve_o_total():
    assert Money(777).split(1) == (Money(777),)


@pytest.mark.parametrize("partes", [0, -1])
def test_divisao_exige_ao_menos_uma_parcela(partes):
    with pytest.raises(ValueError, match="ao menos uma parcela"):
        Money(100).split(partes)


def test_divisao_nao_aceita_valor_negativo():
    with pytest.raises(ValueError, match="valor negativo"):
        Money(-1).split(2)


@given(total=centavos, partes=st.integers(min_value=1, max_value=360))
def test_parcelas_somam_exatamente_o_total(total, partes):
    parcelas = Money(total).split(partes)
    assert len(parcelas) == partes
    assert sum(p.cents for p in parcelas) == total


@given(total=centavos, partes=st.integers(min_value=1, max_value=360))
def test_so_a_ultima_parcela_absorve_o_resto(total, partes):
    *iniciais, ultima = Money(total).split(partes)
    assert all(p.cents == total // partes for p in iniciais)
    assert ultima.cents == total // partes + total % partes


@given(a=centavos, b=centavos)
def test_soma_e_subtracao_sao_inversas(a, b):
    assert (Money(a) + Money(b)) - Money(b) == Money(a)
