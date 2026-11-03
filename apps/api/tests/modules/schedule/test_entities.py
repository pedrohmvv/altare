from datetime import date
from uuid import UUID

import pytest

from wedding.modules.schedule.domain.entities import Milestone
from wedding.modules.schedule.domain.errors import InvalidScheduleValue
from wedding.modules.schedule.domain.values import MAX_NOTE, ManualState
from wedding.shared_kernel.errors import DomainRuleViolated
from wedding.shared_kernel.profile import ProfileKind


def novo():
    return Milestone(id=UUID(int=1), phase_id=UUID(int=2), title="Marco Exemplo", position=0)


def test_marco_nasce_com_responsavel_ambos_sem_prazo_e_sem_estado_manual():  # F-CRN-02, regra 3
    marco = novo()
    assert marco.responsible is ProfileKind.AMBOS
    assert (marco.target_date, marco.note, marco.manual_state) == (None, None, None)


def test_editar_troca_responsavel_nota_e_prazo():  # F-CRN-01
    marco = novo()
    assert marco.edit(ProfileKind.NOIVA, "  Ligar na segunda  ", date(2027, 1, 10)) is True
    assert (marco.responsible, marco.note, marco.target_date) == (
        ProfileKind.NOIVA,
        "Ligar na segunda",
        date(2027, 1, 10),
    )


def test_editar_igual_nao_e_mudanca():
    marco = novo()
    marco.edit(ProfileKind.NOIVO, "nota", date(2027, 1, 10))
    assert marco.edit(ProfileKind.NOIVO, " nota ", date(2027, 1, 10)) is False


def test_nota_em_branco_vira_ausencia_e_prazo_pode_ser_limpo():
    marco = novo()
    marco.edit(ProfileKind.AMBOS, "nota", date(2027, 1, 10))
    assert marco.edit(ProfileKind.AMBOS, "   ", None) is True
    assert (marco.note, marco.target_date) == (None, None)


def test_nota_acima_do_limite_e_recusada_sem_cortar():
    with pytest.raises(InvalidScheduleValue):
        novo().edit(ProfileKind.AMBOS, "x" * (MAX_NOTE + 1), None)
    assert novo().edit(ProfileKind.AMBOS, "x" * MAX_NOTE, None) is True


@pytest.mark.parametrize("ano", [1999, 2101])
def test_prazo_fora_do_intervalo_e_recusado(ano):
    with pytest.raises(InvalidScheduleValue):
        novo().edit(ProfileKind.AMBOS, None, date(ano, 1, 1))


def test_o_erro_de_valor_e_de_dominio_com_codigo_proprio():
    assert issubclass(InvalidScheduleValue, DomainRuleViolated)
    assert InvalidScheduleValue().code == "invalid_schedule_value"


def test_marcar_e_reabrir_mudam_o_estado_manual_e_repetir_nao():  # F-CRN-03
    marco = novo()
    assert marco.set_manual_state(ManualState.DONE) is True
    assert marco.manual_state is ManualState.DONE
    assert marco.set_manual_state(ManualState.DONE) is False
    assert marco.set_manual_state(None) is True
    assert marco.manual_state is None
    assert marco.set_manual_state(None) is False
