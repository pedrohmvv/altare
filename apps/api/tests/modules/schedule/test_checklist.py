"""O checklist (F-CRN-07) no domínio: o item, os limites e o progresso."""

from datetime import UTC, datetime
from uuid import UUID

import pytest

from wedding.modules.schedule.domain.checklist import ChecklistProgress, checklist_progress
from wedding.modules.schedule.domain.entities import ChecklistItem
from wedding.modules.schedule.domain.errors import (
    ChecklistFull,
    ChecklistOpenItems,
    ChecklistTextRequired,
    InvalidChecklistOrder,
    InvalidScheduleValue,
)
from wedding.modules.schedule.domain.values import (
    MAX_CHECKLIST_ITEMS,
    MAX_CHECKLIST_TEXT,
    OwnerKind,
)
from wedding.shared_kernel.errors import DomainRuleViolated

MARCO = UUID(int=100)
TAREFA = UUID(int=200)


def item(texto="Pedir orçamento", posicao=0, **campos) -> ChecklistItem:
    return ChecklistItem(UUID(int=1), texto, posicao, **{"milestone_id": MARCO, **campos})


def test_os_limites_do_checklist():  # F-CRN-07
    assert (MAX_CHECKLIST_TEXT, MAX_CHECKLIST_ITEMS) == (200, 50)


def test_item_nasce_nao_feito():
    assert item().done is False


def test_item_de_marco_e_de_avulsa_sabem_quem_e_o_dono():
    de_marco = item()
    assert (de_marco.owner_kind, de_marco.owner_id) == (OwnerKind.MILESTONE, MARCO)
    de_avulsa = ChecklistItem(UUID(int=2), "Ligar", 0, task_id=TAREFA)
    assert (de_avulsa.owner_kind, de_avulsa.owner_id) == (OwnerKind.TASK, TAREFA)


def test_a_fabrica_liga_o_item_ao_dono_do_tipo_certo():
    de_marco = ChecklistItem.of_owner(UUID(int=3), OwnerKind.MILESTONE, MARCO, "A", 2)
    assert (de_marco.milestone_id, de_marco.task_id, de_marco.position) == (MARCO, None, 2)
    de_avulsa = ChecklistItem.of_owner(UUID(int=4), OwnerKind.TASK, TAREFA, "B", 0)
    assert (de_avulsa.milestone_id, de_avulsa.task_id) == (None, TAREFA)


def test_item_exige_exatamente_um_dono():
    with pytest.raises(ValueError, match="dono"):
        ChecklistItem(UUID(int=1), "Sem dono", 0)
    with pytest.raises(ValueError, match="dono"):
        ChecklistItem(UUID(int=1), "Dois donos", 0, milestone_id=MARCO, task_id=TAREFA)


def test_posicao_negativa_e_recusada():
    with pytest.raises(ValueError, match="posição"):
        item(posicao=-1)


@pytest.mark.parametrize("texto", ["", "   ", "\t\n"])
def test_item_sem_texto_e_recusado(texto):
    with pytest.raises(ChecklistTextRequired):
        item(texto)


def test_texto_e_aparado_e_tem_o_limite_da_coluna():
    assert item("  Pedir orçamento ").text == "Pedir orçamento"
    assert item("x" * MAX_CHECKLIST_TEXT).text == "x" * MAX_CHECKLIST_TEXT
    with pytest.raises(InvalidScheduleValue):
        item("x" * (MAX_CHECKLIST_TEXT + 1))


def test_editar_troca_texto_e_feito_e_diz_se_mudou():
    entrada = item()
    assert entrada.edit(" Pedir dois orçamentos ", True) is True
    assert (entrada.text, entrada.done) == ("Pedir dois orçamentos", True)
    assert entrada.edit("Pedir dois orçamentos", True) is False
    assert entrada.edit("Pedir dois orçamentos", False) is True
    assert entrada.done is False


def test_editar_com_texto_invalido_nao_muda_nada():
    entrada = item()
    with pytest.raises(ChecklistTextRequired):
        entrada.edit("  ", True)
    assert (entrada.text, entrada.done) == ("Pedir orçamento", False)


def test_excluir_carimba_o_item():
    entrada = item()
    agora = datetime(2026, 11, 4, 12, tzinfo=UTC)
    entrada.delete(agora, UUID(int=9))
    assert (entrada.deleted_at, entrada.deleted_by) == (agora, UUID(int=9))


def test_progresso_conta_feitos_e_total():  # F-CRN-07, regra 3
    itens = [item(done=feito) for feito in (True, False, True, False, False)]
    assert checklist_progress(itens) == ChecklistProgress(done=2, total=5)
    assert checklist_progress([]) == ChecklistProgress(done=0, total=0)


def test_os_erros_do_checklist_tem_codigo_estavel():
    esperados = {
        ChecklistTextRequired: "checklist_text_required",
        InvalidChecklistOrder: "invalid_checklist_order",
        ChecklistFull: "checklist_full",
        ChecklistOpenItems: "checklist_open_items",
    }
    for erro, codigo in esperados.items():
        assert issubclass(erro, DomainRuleViolated)
        assert erro().code == codigo
