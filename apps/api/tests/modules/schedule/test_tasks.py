"""As tarefas avulsas (F-CRN-06) no domínio: a entidade, o prazo e a ordem da lista. Avulsa não tem
fase, categoria nem dependências, então nada aqui passa pela derivação dos marcos."""

from datetime import UTC, date, datetime, timedelta
from uuid import UUID

import pytest
from hypothesis import given
from hypothesis import strategies as st

from wedding.modules.schedule.domain.entities import Task
from wedding.modules.schedule.domain.errors import InvalidScheduleValue, TaskTitleRequired
from wedding.modules.schedule.domain.tasks import task_deadline, task_order_key
from wedding.modules.schedule.domain.values import MAX_NOTE, MAX_TITLE, TaskState
from wedding.shared_kernel.errors import DomainRuleViolated
from wedding.shared_kernel.profile import ProfileKind

HOJE = date(2026, 11, 4)


def nova(**campos) -> Task:
    padrao = {"id": UUID(int=1), "title": "Pesquisar Alianças", "responsible": ProfileKind.NOIVA}
    return Task(**{**padrao, "id": UUID(int=1), **campos})


def test_tarefa_nasce_a_fazer_sem_prazo_nem_nota():  # F-CRN-06
    tarefa = nova()
    assert tarefa.state is TaskState.TODO
    assert (tarefa.note, tarefa.target_date) == (None, None)
    assert tarefa.responsible is ProfileKind.NOIVA


def test_os_tres_estados_da_avulsa_usam_o_feminino():  # F-CRN-06
    assert [s.value for s in TaskState] == ["A fazer", "Em andamento", "Concluída"]


@pytest.mark.parametrize("titulo", ["", "   ", "\t\n"])
def test_avulsa_sem_titulo_e_recusada(titulo):
    with pytest.raises(TaskTitleRequired):
        nova(title=titulo)


def test_o_erro_de_titulo_da_avulsa_tem_codigo_proprio():
    assert issubclass(TaskTitleRequired, DomainRuleViolated)
    assert TaskTitleRequired().code == "task_title_required"


def test_titulo_e_aparado_e_tem_o_limite_da_coluna():
    assert nova(title="  Pesquisar Alianças ").title == "Pesquisar Alianças"
    assert nova(title="x" * MAX_TITLE).title == "x" * MAX_TITLE
    with pytest.raises(InvalidScheduleValue):
        nova(title="x" * (MAX_TITLE + 1))


def test_nota_e_prazo_seguem_os_limites_do_marco():
    assert nova(note="  Ver preços  ").note == "Ver preços"
    assert nova(note="   ").note is None
    with pytest.raises(InvalidScheduleValue):
        nova(note="x" * (MAX_NOTE + 1))
    assert nova(target_date=date(2000, 1, 1)).target_date == date(2000, 1, 1)
    assert nova(target_date=date(2100, 12, 31)).target_date == date(2100, 12, 31)
    for ano in (1999, 2101):
        with pytest.raises(InvalidScheduleValue):
            nova(target_date=date(ano, 1, 1))


def test_editar_troca_os_quatro_campos_e_diz_se_mudou():
    tarefa = nova()
    assert tarefa.edit(" Cotar alianças ", ProfileKind.AMBOS, " nota ", date(2027, 1, 10)) is True
    assert (tarefa.title, tarefa.responsible, tarefa.note, tarefa.target_date) == (
        "Cotar alianças",
        ProfileKind.AMBOS,
        "nota",
        date(2027, 1, 10),
    )
    assert tarefa.edit("Cotar alianças", ProfileKind.AMBOS, "nota", date(2027, 1, 10)) is False


def test_editar_com_valor_invalido_nao_muda_nada():
    tarefa = nova()
    with pytest.raises(TaskTitleRequired):
        tarefa.edit("  ", ProfileKind.AMBOS, "nota", None)
    with pytest.raises(InvalidScheduleValue):
        tarefa.edit("Outro", ProfileKind.AMBOS, "x" * (MAX_NOTE + 1), None)
    assert (tarefa.title, tarefa.responsible, tarefa.note) == (
        "Pesquisar Alianças",
        ProfileKind.NOIVA,
        None,
    )


def test_o_estado_e_livre_e_repetir_nao_e_mudanca():  # F-CRN-06
    tarefa = nova()
    assert tarefa.set_state(TaskState.TODO) is False
    for estado in (TaskState.DONE, TaskState.IN_PROGRESS, TaskState.TODO, TaskState.DONE):
        assert tarefa.set_state(estado) is True
        assert tarefa.state is estado
        assert tarefa.set_state(estado) is False


def test_excluir_carimba_e_restaurar_limpa_sem_mexer_no_resto():
    tarefa = nova()
    tarefa.set_state(TaskState.DONE)
    agora = datetime(2026, 11, 4, 12, tzinfo=UTC)
    tarefa.delete(agora, UUID(int=9))
    assert (tarefa.deleted_at, tarefa.deleted_by) == (agora, UUID(int=9))
    tarefa.restore()
    assert (tarefa.deleted_at, tarefa.deleted_by) == (None, None)
    assert tarefa.state is TaskState.DONE


# --- o prazo: a mesma regra do marco, sem passar pela derivação -------------------------------


def test_avulsa_vencida_e_nao_concluida_esta_atrasada():  # F-CRN-06, regra 3
    assert task_deadline(HOJE - timedelta(days=1), False, HOJE) == (True, -1)


def test_avulsa_com_prazo_hoje_nao_esta_atrasada_e_faltam_zero_dias():
    assert task_deadline(HOJE, False, HOJE) == (False, 0)


def test_avulsa_com_prazo_futuro_conta_os_dias():
    assert task_deadline(HOJE + timedelta(days=10), False, HOJE) == (False, 10)


def test_avulsa_concluida_nunca_atrasa_e_nao_tem_contagem():
    assert task_deadline(HOJE - timedelta(days=30), True, HOJE) == (False, None)
    assert task_deadline(HOJE + timedelta(days=30), True, HOJE) == (False, None)


def test_avulsa_sem_prazo_nao_atrasa_e_nao_tem_contagem():
    assert task_deadline(None, False, HOJE) == (False, None)
    assert task_deadline(None, True, HOJE) == (False, None)


@given(
    prazo=st.dates(min_value=date(2000, 1, 1), max_value=date(2100, 12, 31)) | st.none(),
    concluida=st.booleans(),
    hoje=st.dates(min_value=date(2000, 1, 1), max_value=date(2100, 12, 31)),
)
def test_o_prazo_da_avulsa_segue_a_regra_do_marco_para_qualquer_data(prazo, concluida, hoje):
    atrasada, faltam = task_deadline(prazo, concluida, hoje)
    conta = prazo is not None and not concluida
    assert faltam == ((prazo - hoje).days if conta and prazo else None)
    assert atrasada == (conta and prazo is not None and prazo < hoje)
    assert atrasada == (faltam is not None and faltam < 0)


# --- a ordem da lista: concluídas por último, sem prazo por último, prazo, título, id --------


def _tarefa(n: int, titulo: str, prazo: date | None = None, concluida: bool = False) -> Task:
    estado = TaskState.DONE if concluida else TaskState.TODO
    return Task(UUID(int=n), titulo, ProfileKind.AMBOS, target_date=prazo, state=estado)


def test_a_ordem_poe_concluidas_e_sem_prazo_no_fim_e_desempata_por_titulo_e_id():
    lista = [
        _tarefa(1, "Z sem prazo"),
        _tarefa(2, "A concluída com prazo", date(2026, 1, 1), concluida=True),
        _tarefa(3, "B prazo tarde", date(2027, 5, 1)),
        _tarefa(4, "C prazo cedo", date(2026, 12, 1)),
        _tarefa(5, "A sem prazo"),
        _tarefa(6, "B prazo tarde", date(2027, 5, 1)),
        _tarefa(7, "A concluída sem prazo", concluida=True),
    ]
    ordenada = sorted(lista, key=task_order_key)
    assert [t.id.int for t in ordenada] == [4, 3, 6, 5, 1, 2, 7]
