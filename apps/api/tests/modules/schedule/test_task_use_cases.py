"""As tarefas avulsas (F-CRN-06) como casos de uso, com as portas em memória: criar com o
responsável da sessão, editar, mudar de estado (inclusive concluir com itens em aberto), excluir,
restaurar e o prazo pelo dia de Brasília. Avulsa nunca entra nos bloqueios dos marcos."""

from datetime import UTC, date, datetime

import pytest
from tests.modules.schedule.conftest import NOIVA, NOIVO

from wedding.modules.schedule.application.commands.add_checklist_item import (
    AddChecklistItemCommand,
)
from wedding.modules.schedule.application.commands.change_task_state import ChangeTaskStateCommand
from wedding.modules.schedule.application.commands.create_task import CreateTaskCommand
from wedding.modules.schedule.application.commands.delete_task import DeleteTaskCommand
from wedding.modules.schedule.application.commands.restore_task import RestoreTaskCommand
from wedding.modules.schedule.application.commands.update_task import UpdateTaskCommand
from wedding.modules.schedule.application.dto import ScheduleDto, TaskDto
from wedding.modules.schedule.domain.errors import (
    ChecklistOpenItems,
    InvalidScheduleValue,
    TaskTitleRequired,
)
from wedding.modules.schedule.domain.values import OwnerKind, TaskState
from wedding.shared_kernel.errors import NotFound, VersionConflict
from wedding.shared_kernel.profile import ProfileKind


def ler(world, ator=NOIVO) -> ScheduleDto:
    return world.use_cases().read_schedule.execute(ator)


def criar(
    world, titulo="Pesquisar Alianças", *, ator=NOIVA, responsavel=None, nota=None, prazo=None
) -> TaskDto:
    depois = world.use_cases().create_task.execute(
        CreateTaskCommand(titulo, responsavel, nota, prazo), ator
    )
    return next(t for t in depois.tasks if t.title == titulo.strip())


def da_lista(world, tarefa: TaskDto) -> TaskDto:
    return next(t for t in ler(world).tasks if t.id == tarefa.id)


def mudar_estado(world, tarefa, estado, *, ignorar=False, versao=None, ator=NOIVO):
    atual = versao if versao is not None else da_lista(world, tarefa).version
    return world.use_cases().change_task_state.execute(
        ChangeTaskStateCommand(tarefa.id, estado, ignorar, atual), ator
    )


def editar(world, tarefa, *, versao=None, ator=NOIVO, **campos):
    atual = da_lista(world, tarefa)
    padrao = {
        "title": atual.title,
        "responsible": atual.responsible,
        "note": atual.note,
        "target_date": atual.target_date,
    }
    comando = UpdateTaskCommand(
        tarefa.id, **{**padrao, **campos}, version=versao if versao is not None else atual.version
    )
    return world.use_cases().update_task.execute(comando, ator)


def adicionar_item(world, tarefa, texto="Ligar para a joalheria", ator=NOIVO):
    return world.use_cases().add_checklist_item.execute(
        AddChecklistItemCommand(OwnerKind.TASK, tarefa.id, texto), ator
    )


# --- criar ----------------------------------------------------------------------------------


def test_o_cronograma_recem_criado_nao_tem_avulsas(world):
    assert ler(world).tasks == ()


@pytest.mark.parametrize(
    ("ator", "perfil"), [(NOIVA, ProfileKind.NOIVA), (NOIVO, ProfileKind.NOIVO)]
)
def test_sem_responsavel_a_avulsa_e_de_quem_criou_pelo_perfil_da_sessao(
    world, ator, perfil
):  # F-CRN-06: padrão, quem criou
    tarefa = criar(world, ator=ator)
    assert tarefa.responsible is perfil


def test_ambos_explicito_passa_e_nunca_e_o_padrao(world):
    assert criar(world, "Ambos explícito", responsavel=ProfileKind.AMBOS).responsible is (
        ProfileKind.AMBOS
    )
    assert criar(world, "Sem responsável", ator=NOIVO).responsible is not ProfileKind.AMBOS


def test_responsavel_explicito_vence_o_perfil_da_sessao(world):
    assert criar(world, ator=NOIVA, responsavel=ProfileKind.NOIVO).responsible is ProfileKind.NOIVO


def test_a_avulsa_nasce_a_fazer_sem_prazo_nem_nota_na_versao_1(world):  # F-CRN-06
    tarefa = criar(world)
    assert tarefa.state is TaskState.TODO
    assert (tarefa.note, tarefa.target_date, tarefa.version) == (None, None, 1)
    assert tarefa.checklist == ()
    assert (tarefa.checklist_progress.done, tarefa.checklist_progress.total) == (0, 0)


def test_criar_aceita_nota_e_prazo_opcionais_e_apara_o_titulo(world):
    tarefa = criar(world, "  Cotar a lua de mel  ", nota=" ver pacotes ", prazo=date(2027, 3, 1))
    assert (tarefa.title, tarefa.note, tarefa.target_date) == (
        "Cotar a lua de mel",
        "ver pacotes",
        date(2027, 3, 1),
    )


@pytest.mark.parametrize("titulo", ["", "   "])
def test_criar_sem_titulo_e_recusado_e_nada_e_gravado(world, titulo):
    with pytest.raises(TaskTitleRequired):
        criar(world, titulo)
    assert world.store.tasks == {}


def test_criar_com_valor_fora_do_limite_e_recusado(world):
    with pytest.raises(InvalidScheduleValue):
        criar(world, "x" * 121)
    with pytest.raises(InvalidScheduleValue):
        criar(world, nota="x" * 501)
    with pytest.raises(InvalidScheduleValue):
        criar(world, prazo=date(2101, 1, 1))
    assert world.store.tasks == {}


def test_a_avulsa_nao_tem_fase_e_nunca_aparece_nos_marcos(world):  # F-CRN-06, regras 1 e 3
    antes = ler(world).phases
    criar(world)
    depois = ler(world)
    assert depois.phases == antes
    for fase in depois.phases:
        for marco in fase.milestones:
            assert all("Alianças" not in x.title for x in (*marco.unlocks, *marco.depends_on))
            assert all("Alianças" not in b.label for b in marco.blocked_by)


# --- a lista: prazo pelo dia de Brasília e a ordem ----------------------------------------------


def test_avulsa_vencida_esta_atrasada_e_mostra_os_dias_negativos(world):  # F-CRN-06, regra 3
    # O relógio do teste marca 27/10 às 12h UTC, 9h em Brasília.
    tarefa = criar(world, prazo=date(2026, 10, 25))
    assert (tarefa.overdue, tarefa.days_left) == (True, -2)


def test_o_prazo_de_hoje_nao_atrasa_e_o_dia_e_o_de_brasilia(world, clock):
    tarefa = criar(world, prazo=date(2026, 10, 27))
    assert (tarefa.overdue, tarefa.days_left) == (False, 0)
    # 01:00 UTC de 28/10 ainda é 22h de 27/10 em Brasília.
    clock.advance(hours=13)
    assert clock.now() == datetime(2026, 10, 28, 1, 0, tzinfo=UTC)
    assert (da_lista(world, tarefa).overdue, da_lista(world, tarefa).days_left) == (False, 0)
    clock.advance(hours=2)  # 03:00 UTC é 00h do dia 28 em Brasília
    assert (da_lista(world, tarefa).overdue, da_lista(world, tarefa).days_left) == (True, -1)


def test_concluida_nao_atrasa_e_nao_conta_dias(world):
    tarefa = criar(world, prazo=date(2026, 10, 1))
    mudar_estado(world, tarefa, TaskState.DONE)
    concluida = da_lista(world, tarefa)
    assert (concluida.overdue, concluida.days_left) == (False, None)
    mudar_estado(world, tarefa, TaskState.TODO)  # reabrir volta a contar
    assert (da_lista(world, tarefa).overdue, da_lista(world, tarefa).days_left) == (True, -26)


def test_a_lista_vem_com_concluidas_e_sem_prazo_no_fim_e_depois_prazo_titulo(world):
    sem_prazo = criar(world, "A sem prazo")
    tarde = criar(world, "B tarde", prazo=date(2027, 5, 1))
    cedo = criar(world, "C cedo", prazo=date(2026, 12, 1))
    feita = criar(world, "D feita", prazo=date(2026, 11, 1))
    mudar_estado(world, feita, TaskState.DONE)
    assert [t.id for t in ler(world).tasks] == [cedo.id, tarde.id, sem_prazo.id, feita.id]


# --- editar -----------------------------------------------------------------------------------


def test_editar_substitui_os_quatro_campos(world):
    tarefa = criar(world)
    editar(
        world,
        tarefa,
        title="Cotar alianças",
        responsible=ProfileKind.AMBOS,
        note="duas lojas",
        target_date=date(2027, 2, 1),
    )
    depois = da_lista(world, tarefa)
    assert (depois.title, depois.responsible, depois.note, depois.target_date) == (
        "Cotar alianças",
        ProfileKind.AMBOS,
        "duas lojas",
        date(2027, 2, 1),
    )
    assert depois.version == tarefa.version + 1


def test_editar_nulo_apaga_nota_e_prazo(world):
    tarefa = criar(world, nota="nota", prazo=date(2027, 2, 1))
    editar(world, tarefa, note=None, target_date=None)
    depois = da_lista(world, tarefa)
    assert (depois.note, depois.target_date) == (None, None)


def test_editar_com_os_mesmos_valores_nao_grava_nem_sobe_a_version(world):
    tarefa = criar(world)
    editar(world, tarefa)
    assert da_lista(world, tarefa).version == tarefa.version


def test_editar_com_version_velha_e_conflito_e_nao_grava(world):
    tarefa = criar(world)
    editar(world, tarefa, note="primeira")
    with pytest.raises(VersionConflict):
        editar(world, tarefa, versao=tarefa.version, note="segunda")
    assert da_lista(world, tarefa).note == "primeira"


def test_editar_com_titulo_vazio_e_recusado_sem_gravar(world):
    tarefa = criar(world)
    with pytest.raises(TaskTitleRequired):
        editar(world, tarefa, title="  ")
    assert da_lista(world, tarefa) == tarefa


def test_editar_avulsa_inexistente_ou_excluida_e_404(world):
    tarefa = criar(world)
    world.use_cases().delete_task.execute(DeleteTaskCommand(tarefa.id, tarefa.version), NOIVO)
    with pytest.raises(NotFound):
        world.use_cases().update_task.execute(
            UpdateTaskCommand(tarefa.id, "x", ProfileKind.AMBOS, None, None, tarefa.version + 1),
            NOIVO,
        )


# --- o estado ---------------------------------------------------------------------------------


def test_o_estado_muda_livremente_nos_dois_sentidos(world):  # F-CRN-06
    tarefa = criar(world)
    for estado in (
        TaskState.DONE,
        TaskState.IN_PROGRESS,
        TaskState.TODO,
        TaskState.IN_PROGRESS,
        TaskState.DONE,
        TaskState.TODO,
    ):
        mudar_estado(world, tarefa, estado)
        assert da_lista(world, tarefa).state is estado


def test_mudar_o_estado_sobe_a_version_e_repetir_nao_grava(world):
    tarefa = criar(world)
    mudar_estado(world, tarefa, TaskState.IN_PROGRESS)
    assert da_lista(world, tarefa).version == tarefa.version + 1
    mudar_estado(world, tarefa, TaskState.IN_PROGRESS)
    assert da_lista(world, tarefa).version == tarefa.version + 1


def test_mudar_o_estado_com_version_velha_e_conflito(world):
    tarefa = criar(world)
    mudar_estado(world, tarefa, TaskState.IN_PROGRESS)
    with pytest.raises(VersionConflict):
        mudar_estado(world, tarefa, TaskState.DONE, versao=tarefa.version)


def test_concluir_com_item_em_aberto_pede_a_confirmacao(world):  # F-CRN-07, regra 5
    tarefa = criar(world)
    adicionar_item(world, tarefa)
    with pytest.raises(ChecklistOpenItems):
        mudar_estado(world, tarefa, TaskState.DONE)
    assert da_lista(world, tarefa).state is TaskState.TODO


def test_concluir_mesmo_assim_preserva_os_itens(world):  # F-CRN-07, critério de aceite
    tarefa = criar(world)
    adicionar_item(world, tarefa, "Primeiro")
    adicionar_item(world, tarefa, "Segundo")
    antes = da_lista(world, tarefa).checklist
    mudar_estado(world, tarefa, TaskState.DONE, ignorar=True)
    depois = da_lista(world, tarefa)
    assert depois.state is TaskState.DONE
    assert depois.checklist == antes
    assert (depois.checklist_progress.done, depois.checklist_progress.total) == (0, 2)


def test_concluir_com_todos_os_itens_feitos_ou_sem_itens_nao_pede_nada(world):
    sem_itens = criar(world, "Sem itens")
    mudar_estado(world, sem_itens, TaskState.DONE)
    assert da_lista(world, sem_itens).state is TaskState.DONE


def test_ignore_open_items_so_vale_ao_concluir_e_com_outro_destino_e_ignorado(world):
    tarefa = criar(world)
    adicionar_item(world, tarefa)
    mudar_estado(world, tarefa, TaskState.IN_PROGRESS, ignorar=True)  # não é 422
    assert da_lista(world, tarefa).state is TaskState.IN_PROGRESS
    mudar_estado(world, tarefa, TaskState.TODO)  # sem a permissão, itens abertos não atrapalham
    assert da_lista(world, tarefa).state is TaskState.TODO


def test_repetir_o_estado_atual_nao_checa_os_itens(world):
    tarefa = criar(world)
    mudar_estado(world, tarefa, TaskState.DONE)
    adicionar_item(world, tarefa)  # um item novo e aberto numa avulsa já concluída
    atual = da_lista(world, tarefa)
    mudar_estado(world, tarefa, TaskState.DONE)  # no-op: nem erro nem gravação
    assert da_lista(world, tarefa) == atual


def test_a_version_vem_antes_da_confirmacao_dos_itens(world):
    tarefa = criar(world)
    adicionar_item(world, tarefa)
    with pytest.raises(VersionConflict):
        mudar_estado(world, tarefa, TaskState.DONE, versao=tarefa.version + 5)


# --- excluir e restaurar --------------------------------------------------------------------


def test_excluir_e_logico_e_a_avulsa_some_da_lista(world):
    tarefa = criar(world)
    outra = criar(world, "Outra")
    depois = world.use_cases().delete_task.execute(
        DeleteTaskCommand(tarefa.id, tarefa.version), NOIVO
    )
    assert [t.id for t in depois.tasks] == [outra.id]
    guardada = world.store.tasks[tarefa.id]
    assert guardada.deleted_at is not None
    assert guardada.deleted_by == NOIVO.user_id


def test_excluir_com_version_velha_e_conflito_e_nao_exclui(world):
    tarefa = criar(world)
    mudar_estado(world, tarefa, TaskState.IN_PROGRESS)
    with pytest.raises(VersionConflict):
        world.use_cases().delete_task.execute(DeleteTaskCommand(tarefa.id, tarefa.version), NOIVO)
    assert len(ler(world).tasks) == 1


def test_excluir_duas_vezes_ou_o_que_nao_existe_e_404(world):
    tarefa = criar(world)
    world.use_cases().delete_task.execute(DeleteTaskCommand(tarefa.id, tarefa.version), NOIVO)
    with pytest.raises(NotFound):
        world.use_cases().delete_task.execute(
            DeleteTaskCommand(tarefa.id, tarefa.version + 1), NOIVO
        )
    with pytest.raises(NotFound):
        world.use_cases().delete_task.execute(DeleteTaskCommand(world.ids.new_id(), 1), NOIVO)


def test_restaurar_devolve_a_avulsa_como_estava_com_os_itens(world):
    tarefa = criar(world, prazo=date(2027, 1, 5), nota="nota")
    adicionar_item(world, tarefa, "Primeiro")
    mudar_estado(world, tarefa, TaskState.IN_PROGRESS)
    estava = da_lista(world, tarefa)
    world.use_cases().delete_task.execute(DeleteTaskCommand(estava.id, estava.version), NOIVO)
    assert ler(world).tasks == ()

    restaurada = world.use_cases().restore_task.execute(RestoreTaskCommand(estava.id), NOIVA)
    volta = next(t for t in restaurada.tasks if t.id == estava.id)
    assert (volta.title, volta.state, volta.note, volta.target_date, volta.responsible) == (
        estava.title,
        estava.state,
        estava.note,
        estava.target_date,
        estava.responsible,
    )
    assert volta.checklist == estava.checklist
    assert world.store.tasks[estava.id].deleted_at is None


def test_restaurar_o_que_esta_vivo_ou_nao_existe_e_404(world):
    tarefa = criar(world)
    with pytest.raises(NotFound):
        world.use_cases().restore_task.execute(RestoreTaskCommand(tarefa.id), NOIVO)
    with pytest.raises(NotFound):
        world.use_cases().restore_task.execute(RestoreTaskCommand(world.ids.new_id()), NOIVO)
