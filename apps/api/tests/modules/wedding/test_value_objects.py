from datetime import date

import pytest
from hypothesis import given
from hypothesis import strategies as st

from wedding.modules.wedding.domain.errors import InvalidBaselineValue
from wedding.modules.wedding.domain.value_objects import (
    CeilingValue,
    CeremonyKind,
    CeremonyValue,
    DateKind,
    DateValue,
    MonthYear,
    SizeValue,
    TextValue,
)

JAN_2027 = MonthYear(2027, 1)
JUN_2027 = MonthYear(2027, 6)


def test_mes_e_ano_aceitam_do_mes_1_ao_12():
    assert MonthYear(2027, 12).month == 12


@pytest.mark.parametrize("mes", [0, 13, -1])
def test_mes_fora_de_1_a_12_e_recusado(mes):
    with pytest.raises(InvalidBaselineValue):
        MonthYear(2027, mes)


@pytest.mark.parametrize("ano", [1999, 2101])
def test_ano_absurdo_e_recusado(ano):
    with pytest.raises(InvalidBaselineValue):
        MonthYear(ano, 5)


def test_janela_guarda_inicio_fim_e_rotulo():
    janela = DateValue(
        kind=DateKind.WINDOW, window_start=JAN_2027, window_end=JUN_2027, label="primeiro semestre"
    )
    assert (janela.window_start, janela.window_end, janela.label) == (
        JAN_2027,
        JUN_2027,
        "primeiro semestre",
    )


def test_janela_de_um_mes_so_vale():
    assert DateValue(kind=DateKind.WINDOW, window_start=JAN_2027, window_end=JAN_2027)


def test_janela_com_fim_antes_do_inicio_e_recusada():
    with pytest.raises(InvalidBaselineValue):
        DateValue(kind=DateKind.WINDOW, window_start=JUN_2027, window_end=JAN_2027)


def test_janela_exige_inicio_e_fim():
    with pytest.raises(InvalidBaselineValue):
        DateValue(kind=DateKind.WINDOW, window_start=JAN_2027)


def test_data_exata_exige_a_data():
    with pytest.raises(InvalidBaselineValue):
        DateValue(kind=DateKind.EXACT)


def test_data_exata_nao_aceita_janela():
    with pytest.raises(InvalidBaselineValue):
        DateValue(kind=DateKind.EXACT, exact=date(2027, 5, 1), window_start=JAN_2027)


def test_janela_nao_aceita_data_exata():
    with pytest.raises(InvalidBaselineValue):
        DateValue(
            kind=DateKind.WINDOW, window_start=JAN_2027, window_end=JUN_2027, exact=date(2027, 5, 1)
        )


def test_sem_data_nao_e_um_valor():
    with pytest.raises(InvalidBaselineValue):
        DateValue(kind=DateKind.NONE)


def test_rotulo_em_branco_vira_nada_e_rotulo_longo_e_recusado():
    janela = DateValue(
        kind=DateKind.WINDOW, window_start=JAN_2027, window_end=JUN_2027, label="   "
    )
    assert janela.label is None
    with pytest.raises(InvalidBaselineValue):
        DateValue(kind=DateKind.WINDOW, window_start=JAN_2027, window_end=JUN_2027, label="x" * 61)


def test_data_vai_e_volta_do_json():
    exata = DateValue(kind=DateKind.EXACT, exact=date(2027, 5, 1))
    janela = DateValue(kind=DateKind.WINDOW, window_start=JAN_2027, window_end=JUN_2027, label="x")
    assert DateValue.from_json(exata.to_json()) == exata
    assert DateValue.from_json(janela.to_json()) == janela


def test_texto_perde_espacos_das_pontas():
    assert TextValue("  Cidade Exemplo ").text == "Cidade Exemplo"


@pytest.mark.parametrize("texto", ["", "   ", "x" * 81])
def test_texto_vazio_ou_longo_e_recusado(texto):
    with pytest.raises(InvalidBaselineValue):
        TextValue(texto)


def test_porte_aceita_faixa_e_recusa_faixa_invertida_ou_fora_do_limite():
    assert SizeValue(80, 120).maximum == 120
    assert SizeValue(50, 50)
    for minimo, maximo in [(120, 80), (0, 10), (10, 10_001), (-1, 5)]:
        with pytest.raises(InvalidBaselineValue):
            SizeValue(minimo, maximo)


def test_porte_nao_aceita_booleano_nem_decimal():
    with pytest.raises(InvalidBaselineValue):
        SizeValue(True, 10)  # type: ignore[arg-type]
    with pytest.raises(InvalidBaselineValue):
        SizeValue(10, 20.5)  # type: ignore[arg-type]


def test_teto_aceita_centavos_positivos():
    assert CeilingValue(2_800_000).cents == 2_800_000  # F-PLN-01: R$ 28.000,00


@pytest.mark.parametrize("centavos", [0, -1, 10**12 + 1, True, 10.5])
def test_teto_zero_negativo_enorme_ou_nao_inteiro_e_recusado(centavos):
    with pytest.raises(InvalidBaselineValue):
        CeilingValue(centavos)  # type: ignore[arg-type]


def test_cerimonia_aceita_varios_tipos_e_detalhe():
    valor = CeremonyValue(
        kinds=frozenset({CeremonyKind.CIVIL, CeremonyKind.RELIGIOUS}), detail="  detalhe  "
    )
    assert valor.kinds == {CeremonyKind.CIVIL, CeremonyKind.RELIGIOUS}
    assert valor.detail == "detalhe"


def test_cerimonia_exige_ao_menos_um_tipo_e_detalhe_curto():
    with pytest.raises(InvalidBaselineValue):
        CeremonyValue(kinds=frozenset())
    with pytest.raises(InvalidBaselineValue):
        CeremonyValue(kinds=frozenset({CeremonyKind.CIVIL}), detail="x" * 201)


def test_cerimonia_com_detalhe_em_branco_fica_sem_detalhe():
    assert CeremonyValue(kinds=frozenset({CeremonyKind.SYMBOLIC}), detail="  ").detail is None


@given(st.text(min_size=1, max_size=80).filter(lambda t: t.strip() != "" and t == t.strip()))
def test_texto_vai_e_volta_do_json(texto):
    valor = TextValue(texto)
    assert TextValue.from_json(valor.to_json()) == valor


@given(st.integers(min_value=1, max_value=10_000), st.integers(min_value=1, max_value=10_000))
def test_porte_vai_e_volta_do_json_e_respeita_a_ordem(a, b):
    minimo, maximo = sorted((a, b))
    valor = SizeValue(minimo, maximo)
    assert SizeValue.from_json(valor.to_json()) == valor
    assert valor.minimum <= valor.maximum


@given(st.integers(min_value=1, max_value=10**12))
def test_teto_vai_e_volta_do_json(centavos):
    assert CeilingValue.from_json(CeilingValue(centavos).to_json()) == CeilingValue(centavos)


@given(st.sets(st.sampled_from(list(CeremonyKind)), min_size=1))
def test_cerimonia_vai_e_volta_do_json(tipos):
    valor = CeremonyValue(kinds=frozenset(tipos), detail="d")
    assert CeremonyValue.from_json(valor.to_json()) == valor
