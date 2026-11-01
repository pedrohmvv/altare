"""Os contadores da lista (F-CNV-06): função pura sobre os fatos, sem banco.

Os exemplos nomeados vêm da spec e das propriedades do plano (D-071). A recontagem de referência usa
`fractions.Fraction`, de propósito: a conferência não reaproveita a aritmética da produção.
"""

import math
from fractions import Fraction

import pytest
from hypothesis import given
from hypothesis import strategies as st

from wedding.modules.guests.domain.errors import InvalidWeights
from wedding.modules.guests.domain.headcount import (
    BandCounts,
    GuestFacts,
    Weights,
    compute_headcount,
)
from wedding.modules.guests.domain.values import AgeBand, GuestStatus, Probability

ADULT, PAYING, EXEMPT = AgeBand.ADULT, AgeBand.PAYING_CHILD, AgeBand.EXEMPT_CHILD
CERTAIN, PROBABLE, PHASE_2 = Probability.CERTAIN, Probability.PROBABLE, Probability.PHASE_2
DRAFT, INVITED, CONFIRMED, DECLINED = (
    GuestStatus.DRAFT,
    GuestStatus.INVITED,
    GuestStatus.CONFIRMED,
    GuestStatus.DECLINED,
)
SPEC_WEIGHTS = Weights(100, 70, 30)  # os do exemplo da spec: nunca valores do casal


def person(band=ADULT, probability=PROBABLE, status=DRAFT) -> GuestFacts:
    return GuestFacts(band, probability, status)


facts_strategy = st.builds(
    GuestFacts,
    st.sampled_from(list(AgeBand)),
    st.sampled_from(list(Probability)),
    st.sampled_from(list(GuestStatus)),
)
weights_strategy = st.builds(Weights, st.integers(0, 100), st.integers(0, 100), st.integers(0, 100))


def reference_weighted(facts, weights) -> Fraction:
    """A recontagem de referência, em frações exatas de pessoa."""
    total = Fraction(0)
    for f in facts:
        if f.status is DECLINED or f.band is EXEMPT:
            continue
        pct = 100 if f.status is CONFIRMED else weights.of(f.probability)
        total += Fraction(pct, 100)
    return total


class TestExemplosDaSpec:
    def test_cinco_adultos_nenhum_confirmado_dao_3_7_exibido_como_4(self):  # F-CNV-06
        facts = [
            person(probability=CERTAIN),
            person(probability=CERTAIN),
            person(probability=PROBABLE),
            person(probability=PROBABLE),
            person(probability=PHASE_2),
        ]

        result = compute_headcount(facts, SPEC_WEIGHTS)

        assert result.weighted_adults_hundredths == 370
        assert result.weighted_paying_children_hundredths == 0
        assert result.weighted_rounded_up == 4

    def test_com_uma_crianca_pagante_a_base_do_cenario_e_4_7_arredondada_para_5(self):  # F-ORC-03
        facts = [
            person(probability=CERTAIN),
            person(probability=CERTAIN),
            person(probability=PROBABLE),
            person(probability=PROBABLE),
            person(probability=PHASE_2),
            person(PAYING, CERTAIN),
        ]

        result = compute_headcount(facts, SPEC_WEIGHTS)

        assert (
            result.weighted_adults_hundredths,
            result.weighted_paying_children_hundredths,
        ) == (370, 100)
        assert result.weighted_rounded_up == 5

    def test_crianca_isenta_aumenta_o_total_nominal_e_nao_o_ponderado(self):  # F-CNV-06
        base = [person(probability=CERTAIN)]
        com_isenta = [*base, person(EXEMPT, CERTAIN)]

        before = compute_headcount(base, SPEC_WEIGHTS)
        after = compute_headcount(com_isenta, SPEC_WEIGHTS)

        assert after.total_nominal.total == before.total_nominal.total + 1
        assert after.weighted_rounded_up == before.weighted_rounded_up

    def test_sem_pesos_o_ponderado_e_nulo_mas_os_outros_contadores_existem(self):  # F-CNV-06
        result = compute_headcount([person(status=CONFIRMED), person()], None)

        assert result.weighted_adults_hundredths is None
        assert result.weighted_paying_children_hundredths is None
        assert result.weighted_rounded_up is None
        assert (result.total_nominal.adults, result.confirmed.adults) == (2, 1)

    def test_marcar_confirmado_conta_100_por_cento_na_hora(self):  # F-CNV-06
        before = compute_headcount([person(probability=PHASE_2)], SPEC_WEIGHTS)
        after = compute_headcount([person(probability=PHASE_2, status=CONFIRMED)], SPEC_WEIGHTS)

        assert (before.weighted_adults_hundredths, after.weighted_adults_hundredths) == (30, 100)

    def test_nao_ira_sai_dos_tres_contadores_e_aparece_a_parte(self):  # F-CNV-04
        result = compute_headcount(
            [person(status=DECLINED), person(PAYING, CERTAIN, DECLINED), person()], SPEC_WEIGHTS
        )

        assert result.total_nominal == BandCounts(adults=1)
        assert result.confirmed == BandCounts()
        assert result.weighted_adults_hundredths == 70
        assert result.not_attending == BandCounts(adults=1, paying_children=1)

    def test_detalha_cada_contador_por_faixa(self):  # F-CNV-06
        facts = [
            person(ADULT, status=CONFIRMED),
            person(PAYING, status=CONFIRMED),
            person(EXEMPT, status=CONFIRMED),
            person(EXEMPT),
        ]

        result = compute_headcount(facts, SPEC_WEIGHTS)

        assert result.total_nominal == BandCounts(1, 1, 2)
        assert result.confirmed == BandCounts(1, 1, 1)

    def test_base_so_certeza_e_confirmados(self):  # F-ORC-03
        facts = [
            person(probability=CERTAIN),
            person(probability=PROBABLE, status=CONFIRMED),
            person(probability=PROBABLE),
            person(probability=CERTAIN, status=DECLINED),
        ]

        result = compute_headcount(facts, SPEC_WEIGHTS)

        assert result.certain_or_confirmed == BandCounts(adults=2)

    def test_lista_vazia_zera_tudo(self):
        result = compute_headcount([], SPEC_WEIGHTS)

        assert result.total_nominal == BandCounts()
        assert result.weighted_rounded_up == 0


class TestPesos:
    def test_pesos_de_0_a_100_valem(self):
        assert Weights(0, 50, 100).of(PROBABLE) == 50

    @pytest.mark.parametrize("pesos", [(-1, 50, 50), (50, 101, 50), (50, 50, True), (50, 50, 5.5)])
    def test_peso_fora_de_0_a_100_ou_nao_inteiro_e_recusado(self, pesos):
        with pytest.raises(InvalidWeights):
            Weights(*pesos)  # type: ignore[arg-type]


class TestPropriedades:
    @given(st.lists(facts_strategy), weights_strategy)
    def test_total_nominal_e_a_soma_das_faixas_e_nada_e_negativo(self, facts, weights):
        result = compute_headcount(facts, weights)

        for counts in (
            result.total_nominal,
            result.confirmed,
            result.not_attending,
            result.certain_or_confirmed,
        ):
            assert counts.total == counts.adults + counts.paying_children + counts.exempt_children
            assert min(counts.adults, counts.paying_children, counts.exempt_children) >= 0
        assert result.confirmed.total <= result.total_nominal.total
        assert result.total_nominal.total + result.not_attending.total == len(facts)

    @given(st.lists(facts_strategy), weights_strategy)
    def test_nao_ira_nao_entra_em_nenhum_dos_tres_contadores(self, facts, weights):
        declined = [f for f in facts if f.status is DECLINED]
        living = [f for f in facts if f.status is not DECLINED]

        with_declined = compute_headcount(facts, weights)
        without = compute_headcount(living, weights)

        assert with_declined.total_nominal == without.total_nominal
        assert with_declined.confirmed == without.confirmed
        assert with_declined.weighted_adults_hundredths == without.weighted_adults_hundredths
        assert with_declined.not_attending.total == len(declined)

    @given(st.lists(facts_strategy), weights_strategy)
    def test_crianca_isenta_nunca_altera_o_ponderado(self, facts, weights):
        extra = person(EXEMPT, PROBABLE, CONFIRMED)

        assert (
            compute_headcount([*facts, extra], weights).weighted_rounded_up
            == compute_headcount(facts, weights).weighted_rounded_up
        )

    @given(
        st.lists(facts_strategy, min_size=1), weights_strategy, st.sampled_from(list(Probability))
    )
    def test_confirmado_conta_100_qualquer_que_seja_a_probabilidade(
        self, facts, weights, probability
    ):
        confirmed = person(ADULT, probability, CONFIRMED)
        other = person(ADULT, Probability.PHASE_2, CONFIRMED)

        a = compute_headcount([*facts, confirmed], weights)
        b = compute_headcount([*facts, other], weights)

        assert a.weighted_adults_hundredths == b.weighted_adults_hundredths

    @given(
        st.lists(facts_strategy),
        weights_strategy,
        st.sampled_from(list(Probability)),
        st.integers(1, 100),
    )
    def test_subir_um_peso_nunca_diminui_o_ponderado(self, facts, weights, which, bump):
        raised = Weights(
            min(100, weights.certain_pct + (bump if which is CERTAIN else 0)),
            min(100, weights.probable_pct + (bump if which is PROBABLE else 0)),
            min(100, weights.phase_2_pct + (bump if which is PHASE_2 else 0)),
        )

        before = compute_headcount(facts, weights)
        after = compute_headcount(facts, raised)

        assert after.weighted_adults_hundredths is not None
        assert before.weighted_adults_hundredths is not None
        assert after.weighted_adults_hundredths >= before.weighted_adults_hundredths
        assert (after.weighted_paying_children_hundredths or 0) >= (
            before.weighted_paying_children_hundredths or 0
        )

    @given(st.lists(facts_strategy, min_size=1), weights_strategy, st.data())
    def test_com_pesos_ate_100_marcar_confirmado_nunca_diminui_o_ponderado(
        self, facts, weights, data
    ):
        index = data.draw(st.integers(0, len(facts) - 1))
        confirmed = [
            GuestFacts(f.band, f.probability, CONFIRMED) if i == index else f
            for i, f in enumerate(facts)
        ]

        before = compute_headcount(facts, weights)
        after = compute_headcount(confirmed, weights)

        old = facts[index].status
        if old is DECLINED:
            return  # voltar de Não irá conta uma pessoa a mais, e isso é outra propriedade
        assert after.weighted_rounded_up is not None
        assert before.weighted_rounded_up is not None
        assert after.weighted_rounded_up >= before.weighted_rounded_up

    @given(st.lists(facts_strategy), weights_strategy)
    def test_o_ponderado_fica_entre_zero_e_o_total_sem_isentos(self, facts, weights):
        result = compute_headcount(facts, weights)

        non_exempt = result.total_nominal.adults + result.total_nominal.paying_children
        total = (result.weighted_adults_hundredths or 0) + (
            result.weighted_paying_children_hundredths or 0
        )
        assert 0 <= total <= 100 * non_exempt

    @given(st.lists(facts_strategy), weights_strategy, st.randoms(use_true_random=False))
    def test_a_ordem_das_pessoas_nao_importa(self, facts, weights, random):
        shuffled = list(facts)
        random.shuffle(shuffled)

        assert compute_headcount(shuffled, weights) == compute_headcount(facts, weights)

    @given(st.lists(facts_strategy), weights_strategy)
    def test_o_arredondado_para_cima_e_o_menor_inteiro_que_nao_subestima(self, facts, weights):
        result = compute_headcount(facts, weights)

        exact = reference_weighted(facts, weights)
        assert result.weighted_rounded_up == math.ceil(exact)
        assert Fraction(result.weighted_rounded_up or 0) >= exact
        assert Fraction(result.weighted_rounded_up or 0) < exact + 1

    @given(st.lists(facts_strategy), weights_strategy)
    def test_o_ponderado_confere_com_a_recontagem_em_fracoes_exatas(self, facts, weights):
        result = compute_headcount(facts, weights)

        adults = [f for f in facts if f.band is ADULT]
        kids = [f for f in facts if f.band is PAYING]
        assert Fraction(result.weighted_adults_hundredths or 0, 100) == reference_weighted(
            adults, weights
        )
        assert Fraction(result.weighted_paying_children_hundredths or 0, 100) == reference_weighted(
            kids, weights
        )
