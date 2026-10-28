import pytest
from hypothesis import given
from hypothesis import strategies as st

from wedding.modules.guests.domain.age import AgeLimits, suggest_band
from wedding.modules.guests.domain.errors import InvalidAgeLimits
from wedding.modules.guests.domain.values import AgeBand


def test_sem_limites_nenhuma_sugestao_aparece():  # F-CNV-03
    assert suggest_band(4, AgeLimits()) is None


def test_isenta_ate_5_e_crianca_de_4_anos_sugere_isenta():  # F-CNV-03
    assert suggest_band(4, AgeLimits(exempt_until=5)) is AgeBand.EXEMPT_CHILD


def test_sem_idade_nao_ha_o_que_sugerir():
    assert suggest_band(None, AgeLimits(exempt_until=5, paying_until=12)) is None


@pytest.mark.parametrize(
    ("idade", "esperada"),
    [
        (0, AgeBand.EXEMPT_CHILD),
        (5, AgeBand.EXEMPT_CHILD),
        (6, AgeBand.PAYING_CHILD),
        (12, AgeBand.PAYING_CHILD),
        (13, AgeBand.ADULT),
    ],
)
def test_com_os_dois_limites_cada_idade_tem_a_sua_faixa(idade, esperada):
    assert suggest_band(idade, AgeLimits(exempt_until=5, paying_until=12)) is esperada


def test_so_sugere_quando_a_regra_decide():  # decisão 2 do plano
    only_exempt = AgeLimits(exempt_until=5)
    only_paying = AgeLimits(paying_until=12)

    assert suggest_band(8, only_exempt) is None  # acima de N, pagante ou adulta: não se sabe
    assert suggest_band(8, only_paying) is None  # até M, isenta ou pagante: não se sabe
    assert suggest_band(13, only_paying) is AgeBand.ADULT


def test_limites_validos_e_o_isenta_nao_passa_do_pagante():
    assert AgeLimits(exempt_until=5, paying_until=5).exempt_until == 5
    assert AgeLimits(exempt_until=0).paying_until is None


@pytest.mark.parametrize(
    "limites",
    [
        {"exempt_until": 8, "paying_until": 5},
        {"exempt_until": -1},
        {"paying_until": 18},
        {"exempt_until": True},
        {"paying_until": 4.5},
    ],
)
def test_limites_incoerentes_sao_recusados(limites):
    with pytest.raises(InvalidAgeLimits):
        AgeLimits(**limites)


@given(
    st.integers(0, 17),
    st.one_of(st.none(), st.integers(0, 17)),
    st.one_of(st.none(), st.integers(0, 17)),
)
def test_a_sugestao_so_vem_de_limites_coerentes_e_nunca_muda_a_idade(age, exempt, paying):
    if exempt is not None and paying is not None and exempt > paying:
        with pytest.raises(InvalidAgeLimits):
            AgeLimits(exempt, paying)
        return
    limits = AgeLimits(exempt, paying)

    suggestion = suggest_band(age, limits)

    if exempt is None and paying is None:
        assert suggestion is None
    assert suggestion in (None, *AgeBand)
