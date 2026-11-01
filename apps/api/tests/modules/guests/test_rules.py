from uuid import UUID

from hypothesis import given
from hypothesis import strategies as st

from wedding.modules.guests.domain.entities import Guest
from wedding.modules.guests.domain.rules import HouseholdSummary, display_order, household_summary
from wedding.modules.guests.domain.values import GuestStatus

NUCLEO = UUID(int=100)


def pessoa(numero, **campos) -> Guest:
    base = {
        "id": UUID(int=numero),
        "household_id": NUCLEO,
        "position": numero,
        "name": f"P{numero}",
    }
    return Guest(**(base | campos))


def test_resumo_do_nucleo_conta_cada_status():  # F-CNV-04, regra 1
    resumo = household_summary(
        [
            GuestStatus.CONFIRMED,
            GuestStatus.CONFIRMED,
            GuestStatus.CONFIRMED,
            GuestStatus.INVITED,
            GuestStatus.DECLINED,
            GuestStatus.DRAFT,
        ]
    )

    assert resumo == HouseholdSummary(total=6, confirmed=3, invited=1, draft=1, declined=1)


@given(st.lists(st.sampled_from(list(GuestStatus))))
def test_resumo_soma_todas_as_pessoas(statuses):
    resumo = household_summary(statuses)

    assert resumo.total == len(statuses)
    assert resumo.confirmed + resumo.invited + resumo.draft + resumo.declined == resumo.total


def test_acompanhante_aparece_logo_depois_do_titular():  # decisão 13 do plano
    titular = pessoa(1)
    outra = pessoa(2)
    acompanhante = pessoa(3, name=None, companion_of_id=titular.id)

    ordem = display_order([acompanhante, outra, titular])

    assert [g.id for g in ordem] == [titular.id, acompanhante.id, outra.id]


def test_acompanhante_sem_titular_na_lista_fica_na_sua_posicao():
    orfa = pessoa(2, name=None, companion_of_id=UUID(int=999))

    assert [g.id for g in display_order([pessoa(3), orfa, pessoa(1)])] == [
        UUID(int=1),
        UUID(int=2),
        UUID(int=3),
    ]


@given(st.permutations(range(1, 7)))
def test_ordem_de_exibicao_e_uma_permutacao_que_nao_depende_da_entrada(numeros):
    titular = pessoa(1)
    todas = [
        titular,
        pessoa(2),
        pessoa(3, name=None, companion_of_id=titular.id),
        pessoa(4),
        pessoa(5, name=None, companion_of_id=UUID(int=4)),
        pessoa(6),
    ]
    entrada = [todas[n - 1] for n in numeros]

    ordem = display_order(entrada)

    assert sorted(g.id.int for g in ordem) == [1, 2, 3, 4, 5, 6]
    assert [g.id.int for g in ordem] == [1, 3, 2, 4, 5, 6]
