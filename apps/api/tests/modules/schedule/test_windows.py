"""O cálculo das janelas dos marcos (F-CRN-05, Modo Com Data): aritmética de meses e semanas sobre
a data do casamento, sem biblioteca externa, e os limites que o casal pode editar."""

import calendar
from datetime import date, timedelta

import pytest
from hypothesis import given
from hypothesis import strategies as st

from wedding.modules.schedule.domain.errors import InvalidMilestoneWindow
from wedding.modules.schedule.domain.windows import (
    WindowUnit,
    subtract_months,
    subtract_weeks,
    validate_window,
    window_dates,
)

MESES = WindowUnit.MONTHS
SEMANAS = WindowUnit.WEEKS


@pytest.mark.parametrize(
    ("data", "meses", "esperado"),
    [
        (date(2027, 5, 31), 3, date(2027, 2, 28)),  # F-CRN-05: 31/05 menos 3 meses
        (date(2028, 5, 31), 3, date(2028, 2, 29)),  # ano bissexto
        (date(2028, 2, 29), 12, date(2027, 2, 28)),
        (date(2028, 3, 31), 1, date(2028, 2, 29)),
        (date(2027, 6, 12), 14, date(2026, 4, 12)),  # F-CRN-05: início de "Fechar o Espaço"
        (date(2027, 6, 12), 10, date(2026, 8, 12)),
        (date(2027, 3, 1), 3, date(2026, 12, 1)),  # atravessa o ano
        (date(2027, 1, 31), 1, date(2026, 12, 31)),
        (date(2027, 6, 12), 0, date(2027, 6, 12)),
    ],
)
def test_subtrai_meses_respeitando_o_fim_do_mes(data, meses, esperado):
    assert subtract_months(data, meses) == esperado


def test_subtrai_semanas_como_sete_dias():
    assert subtract_weeks(date(2027, 6, 12), 4) == date(2027, 5, 15)
    assert subtract_weeks(date(2027, 6, 12), 0) == date(2027, 6, 12)


def test_janela_em_meses_do_fechar_o_espaco_com_a_data_de_aceite():  # F-CRN-05
    assert window_dates(date(2027, 6, 12), 14, 10, MESES) == (date(2026, 4, 12), date(2026, 8, 12))


def test_janela_em_semanas():
    assert window_dates(date(2027, 6, 12), 4, 2, SEMANAS) == (
        date(2027, 5, 15),
        date(2027, 5, 29),
    )


def test_janela_zero_a_zero_e_o_proprio_dia_do_casamento():
    assert window_dates(date(2027, 6, 12), 0, 0, MESES) == (
        date(2027, 6, 12),
        date(2027, 6, 12),
    )


def test_fim_tres_meses_antes_de_31_05_cai_em_28_02_ou_29_02():  # F-CRN-05
    assert window_dates(date(2027, 5, 31), 6, 3, MESES) == (date(2026, 11, 30), date(2027, 2, 28))
    assert window_dates(date(2028, 5, 31), 6, 3, MESES) == (date(2027, 11, 30), date(2028, 2, 29))


@pytest.mark.parametrize(
    ("exact", "inicio", "fim", "unidade"),
    [
        (date(1, 1, 1), 1, 1, MESES),  # antes do ano 1
        (date(1, 1, 5), 1, 0, SEMANAS),  # semanas passam do ano 1
    ],
)
def test_data_antes_do_ano_1_nao_levanta_excecao_e_nao_calcula(exact, inicio, fim, unidade):
    assert window_dates(exact, inicio, fim, unidade) is None


def test_o_ultimo_dia_representavel_ainda_calcula_a_janela_zero():
    ultimo = date(9999, 12, 31)
    assert window_dates(ultimo, 0, 0, MESES) == (ultimo, ultimo)


@given(
    dia=st.dates(min_value=date(1, 1, 1), max_value=date(9999, 12, 31)),
    inicio=st.integers(0, 120),
    fim=st.integers(0, 120),
    unidade=st.sampled_from(list(WindowUnit)),
)
def test_window_dates_e_total_ate_nos_extremos_de_ano(dia, inicio, fim, unidade):
    resultado = window_dates(dia, max(inicio, fim), min(inicio, fim), unidade)
    if resultado is not None:
        assert resultado[0] <= resultado[1] <= dia


@given(
    dia=st.dates(min_value=date(2000, 1, 1), max_value=date(2100, 12, 31)),
    meses=st.integers(0, 120),
)
def test_meses_o_dia_nunca_passa_do_original_e_o_indice_do_mes_difere_em_exatamente_n(dia, meses):
    resultado = subtract_months(dia, meses)
    assert resultado.day <= dia.day
    assert (dia.year * 12 + dia.month) - (resultado.year * 12 + resultado.month) == meses
    # O dia só encolhe quando o mês de destino é menor, e vira o último dia dele.
    if resultado.day != dia.day:
        assert resultado.day == calendar.monthrange(resultado.year, resultado.month)[1]


@given(
    dia=st.dates(min_value=date(2000, 1, 1), max_value=date(2100, 12, 31)),
    semanas=st.integers(0, 520),
)
def test_semanas_sao_exatamente_sete_vezes_n_dias(dia, semanas):
    assert dia - subtract_weeks(dia, semanas) == timedelta(days=7 * semanas)


@given(
    dia=st.dates(min_value=date(2000, 1, 1), max_value=date(2100, 12, 31)),
    a=st.integers(0, 120),
    b=st.integers(0, 120),
    unidade=st.sampled_from(list(WindowUnit)),
)
def test_inicio_nunca_vem_depois_do_fim_quando_a_e_maior_ou_igual_a_b(dia, a, b, unidade):
    maior, menor = max(a, b), min(a, b)
    resultado = window_dates(dia, maior, menor, unidade)
    assert resultado is not None
    assert resultado[0] <= resultado[1]


@pytest.mark.parametrize(
    ("inicio", "fim", "unidade"),
    [(14, 10, MESES), (0, 0, MESES), (120, 0, MESES), (520, 1, SEMANAS), (4, 4, SEMANAS)],
)
def test_janelas_dentro_dos_limites_sao_aceitas(inicio, fim, unidade):
    validate_window(inicio, fim, unidade)


@pytest.mark.parametrize(
    ("inicio", "fim", "unidade"),
    [
        (3, 4, MESES),  # início menor que o fim
        (3, -1, MESES),  # fim negativo
        (-1, -2, SEMANAS),  # negativos
        (121, 1, MESES),  # acima de 120 meses
        (521, 1, SEMANAS),  # acima de 520 semanas
    ],
)
def test_janelas_fora_dos_limites_sao_recusadas(inicio, fim, unidade):
    with pytest.raises(InvalidMilestoneWindow) as erro:
        validate_window(inicio, fim, unidade)
    assert erro.value.code == "invalid_window"


def test_o_limite_de_meses_nao_vale_para_semanas_e_vice_versa():
    validate_window(300, 0, SEMANAS)
    with pytest.raises(InvalidMilestoneWindow):
        validate_window(300, 0, MESES)
