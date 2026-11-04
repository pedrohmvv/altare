"""O checklist (F-CRN-07) de marcos e de avulsas como casos de uso: adicionar, marcar e editar,
remover, reordenar, o limite de 50, o dono excluído e concluir o marco com itens em aberto. O item
nunca toca o dono: o estado e a `version` dele ficam como estavam."""

import pytest
from tests.modules.schedule.catalog import marco_id
from tests.modules.schedule.conftest import NOIVA, NOIVO

from wedding.modules.schedule.application.commands.add_checklist_item import (
    AddChecklistItemCommand,
)
from wedding.modules.schedule.application.commands.change_milestone_state import (
    ChangeMilestoneStateCommand,
)
from wedding.modules.schedule.application.commands.create_task import CreateTaskCommand
from wedding.modules.schedule.application.commands.delete_milestone import DeleteMilestoneCommand
from wedding.modules.schedule.application.commands.delete_task import DeleteTaskCommand
from wedding.modules.schedule.application.commands.remove_checklist_item import (
    RemoveChecklistItemCommand,
)
from wedding.modules.schedule.application.commands.reorder_checklist import (
    ReorderChecklistCommand,
)
from wedding.modules.schedule.application.commands.restore_milestone import (
    RestoreMilestoneCommand,
)
from wedding.modules.schedule.application.commands.restore_task import RestoreTaskCommand
from wedding.modules.schedule.application.commands.update_checklist_item import (
    UpdateChecklistItemCommand,
)
from wedding.modules.schedule.application.dto import ChecklistItemDto, ScheduleDto
from wedding.modules.schedule.domain.errors import (
    ChecklistFull,
    ChecklistOpenItems,
    ChecklistTextRequired,
    InvalidChecklistOrder,
    InvalidScheduleValue,
    MilestoneBlocked,
)
from wedding.modules.schedule.domain.values import (
    MAX_CHECKLIST_ITEMS,
    ManualState,
    MilestoneState,
    OwnerKind,
    Standing,
)
from wedding.shared_kernel.errors import NotFound, VersionConflict

# C01 não depende de ninguém e não tem categoria: nasce `Destravado`, o ponto de partida limpo.
LIVRE = "C01"
# C03 aguarda C01 e C02: nasce `Bloqueado`.
BLOQUEADO = "C03"


def ler(world, ator=NOIVO) -> ScheduleDto:
    return world.use_cases().read_schedule.execute(ator)


def marco(world, codigo):
    return next(m for f in ler(world).phases for m in f.milestones if m.id == marco_id(codigo))


def itens_do_marco(world, codigo) -> tuple[ChecklistItemDto, ...]:
    return marco(world, codigo).checklist


def adicionar(world, tipo, dono, texto="Pedir orçamento", ator=NOIVO) -> ScheduleDto:
    return world.use_cases().add_checklist_item.execute(
        AddChecklistItemCommand(tipo, dono, texto), ator
    )


def adicionar_ao_marco(world, codigo, texto="Pedir orçamento"):
    return adicionar(world, OwnerKind.MILESTONE, marco_id(codigo), texto)


def nova_avulsa(world, titulo="Pesquisar Alianças"):
    depois = world.use_cases().create_task.execute(
        CreateTaskCommand(titulo, None, None, None), NOIVA
    )
    return next(t for t in depois.tasks if t.title == titulo)


def itens_da_avulsa(world, tarefa_id):
    return next(t for t in ler(world).tasks if t.id == tarefa_id).checklist


def atualizar(world, item, *, texto=None, feito=None, versao=None, ator=NOIVO):
    return world.use_cases().update_checklist_item.execute(
        UpdateChecklistItemCommand(
            item.id,
            item.text if texto is None else texto,
            item.done if feito is None else feito,
            item.version if versao is None else versao,
        ),
        ator,
    )


def estado_do_marco(world, codigo, estado, *, ignorar_bloqueio=False, ignorar_itens=False):
    comando = ChangeMilestoneStateCommand(
        marco_id(codigo),
        estado,
        ignorar_bloqueio,
        marco(world, codigo).version,
        ignore_open_items=ignorar_itens,
    )
    return world.use_cases().change_milestone_state.execute(comando, NOIVO)


# --- adicionar -------------------------------------------------------------------------------


def test_marco_e_avulsa_nascem_sem_itens_e_com_progresso_zero(world):
    assert marco(world, LIVRE).checklist == ()
    assert marco(world, LIVRE).checklist_progress.total == 0


def test_adicionar_ao_marco_poe_o_item_no_fim_nao_feito_e_com_version_propria(world):  # F-CRN-07
    adicionar_ao_marco(world, LIVRE, "Primeiro")
    adicionar_ao_marco(world, LIVRE, "  Segundo  ")
    itens = itens_do_marco(world, LIVRE)
    assert [(i.text, i.done, i.position, i.version) for i in itens] == [
        ("Primeiro", False, 0, 1),
        ("Segundo", False, 1, 1),
    ]


def test_adicionar_a_avulsa_funciona_do_mesmo_jeito(world):
    tarefa = nova_avulsa(world)
    adicionar(world, OwnerKind.TASK, tarefa.id, "Ligar para a joalheria")
    itens = itens_da_avulsa(world, tarefa.id)
    assert [(i.text, i.position) for i in itens] == [("Ligar para a joalheria", 0)]


def test_a_posicao_do_novo_item_e_a_maior_viva_mais_um_mesmo_com_buraco(world):
    for texto in ("A", "B", "C"):
        adicionar_ao_marco(world, LIVRE, texto)
    b = itens_do_marco(world, LIVRE)[1]
    world.use_cases().remove_checklist_item.execute(
        RemoveChecklistItemCommand(b.id, b.version), NOIVO
    )
    adicionar_ao_marco(world, LIVRE, "D")
    assert [(i.text, i.position) for i in itens_do_marco(world, LIVRE)] == [
        ("A", 0),
        ("C", 2),
        ("D", 3),
    ]


def test_o_item_so_fica_no_dono_dele(world):
    adicionar_ao_marco(world, LIVRE, "Do C01")
    tarefa = nova_avulsa(world)
    assert marco(world, "C02").checklist == ()
    assert itens_da_avulsa(world, tarefa.id) == ()


def test_adicionar_o_item_nao_toca_o_dono(world):  # F-CRN-07, regra 4
    antes = marco(world, LIVRE)
    adicionar_ao_marco(world, LIVRE)
    depois = marco(world, LIVRE)
    assert depois.version == antes.version
    assert depois.state is antes.state
    tarefa = nova_avulsa(world)
    adicionar(world, OwnerKind.TASK, tarefa.id)
    assert next(t for t in ler(world).tasks if t.id == tarefa.id).version == tarefa.version


@pytest.mark.parametrize("texto", ["", "   "])
def test_item_sem_texto_e_recusado(world, texto):
    with pytest.raises(ChecklistTextRequired):
        adicionar_ao_marco(world, LIVRE, texto)
    assert world.store.items == {}


def test_item_com_texto_acima_de_200_e_recusado(world):
    with pytest.raises(InvalidScheduleValue):
        adicionar_ao_marco(world, LIVRE, "x" * 201)
    adicionar_ao_marco(world, LIVRE, "x" * 200)


def test_adicionar_ao_dono_que_nao_existe_ou_foi_excluido_e_404(world):
    with pytest.raises(NotFound):
        adicionar(world, OwnerKind.MILESTONE, world.ids.new_id())
    with pytest.raises(NotFound):
        adicionar(world, OwnerKind.TASK, world.ids.new_id())
    # O id de um marco não vale como o de uma avulsa, e o contrário também.
    with pytest.raises(NotFound):
        adicionar(world, OwnerKind.TASK, marco_id(LIVRE))
    tarefa = nova_avulsa(world)
    with pytest.raises(NotFound):
        adicionar(world, OwnerKind.MILESTONE, tarefa.id)
    world.use_cases().delete_task.execute(DeleteTaskCommand(tarefa.id, tarefa.version), NOIVO)
    with pytest.raises(NotFound):
        adicionar(world, OwnerKind.TASK, tarefa.id)


def test_o_cinquenta_e_um_item_vivo_e_recusado_e_remover_um_abre_vaga(world):
    for numero in range(MAX_CHECKLIST_ITEMS):
        adicionar_ao_marco(world, LIVRE, f"Item {numero}")
    with pytest.raises(ChecklistFull):
        adicionar_ao_marco(world, LIVRE, "Item demais")
    assert len(itens_do_marco(world, LIVRE)) == MAX_CHECKLIST_ITEMS
    primeiro = itens_do_marco(world, LIVRE)[0]
    world.use_cases().remove_checklist_item.execute(
        RemoveChecklistItemCommand(primeiro.id, primeiro.version), NOIVO
    )
    adicionar_ao_marco(world, LIVRE, "Cabe agora")
    assert len(itens_do_marco(world, LIVRE)) == MAX_CHECKLIST_ITEMS


def test_o_limite_e_por_dono(world):
    for numero in range(MAX_CHECKLIST_ITEMS):
        adicionar_ao_marco(world, LIVRE, f"Item {numero}")
    adicionar_ao_marco(world, "C02", "Outro dono")
    assert len(itens_do_marco(world, "C02")) == 1


# --- progresso ------------------------------------------------------------------------------


def test_o_progresso_conta_os_feitos_de_dois_em_cinco(world):  # F-CRN-07, critério de aceite
    for numero in range(5):
        adicionar_ao_marco(world, LIVRE, f"Item {numero}")
    for item in itens_do_marco(world, LIVRE)[:2]:
        atualizar(world, item, feito=True)
    progresso = marco(world, LIVRE).checklist_progress
    assert (progresso.done, progresso.total) == (2, 5)


def test_o_progresso_nao_conta_item_removido(world):
    adicionar_ao_marco(world, LIVRE, "A")
    adicionar_ao_marco(world, LIVRE, "B")
    a = itens_do_marco(world, LIVRE)[0]
    atualizar(world, a, feito=True)
    feito = itens_do_marco(world, LIVRE)[0]
    world.use_cases().remove_checklist_item.execute(
        RemoveChecklistItemCommand(feito.id, feito.version), NOIVO
    )
    progresso = marco(world, LIVRE).checklist_progress
    assert (progresso.done, progresso.total) == (0, 1)


# --- marcar e editar ------------------------------------------------------------------------


def test_marcar_e_desmarcar_mexem_so_na_version_do_item_e_nao_no_dono(world):  # F-CRN-07
    adicionar_ao_marco(world, LIVRE)
    dono = marco(world, LIVRE)
    item = dono.checklist[0]
    atualizar(world, item, feito=True)
    depois = marco(world, LIVRE)
    assert (depois.checklist[0].done, depois.checklist[0].version) == (True, item.version + 1)
    assert depois.version == dono.version
    assert depois.state is dono.state
    atualizar(world, depois.checklist[0], feito=False)
    assert marco(world, LIVRE).checklist[0].done is False


def test_editar_o_texto_substitui_texto_e_feito(world):
    adicionar_ao_marco(world, LIVRE)
    item = itens_do_marco(world, LIVRE)[0]
    atualizar(world, item, texto=" Pedir três orçamentos ", feito=True)
    depois = itens_do_marco(world, LIVRE)[0]
    assert (depois.text, depois.done) == ("Pedir três orçamentos", True)


def test_editar_sem_mudanca_real_nao_grava_nem_sobe_a_version(world):
    adicionar_ao_marco(world, LIVRE)
    item = itens_do_marco(world, LIVRE)[0]
    atualizar(world, item)
    atualizar(world, item, texto="  Pedir orçamento  ")
    assert itens_do_marco(world, LIVRE)[0] == item


def test_editar_item_com_version_velha_e_conflito(world):
    adicionar_ao_marco(world, LIVRE)
    item = itens_do_marco(world, LIVRE)[0]
    atualizar(world, item, feito=True)
    with pytest.raises(VersionConflict):
        atualizar(world, item, texto="Outro texto")
    assert itens_do_marco(world, LIVRE)[0].text == "Pedir orçamento"


def test_editar_item_com_texto_vazio_e_recusado(world):
    adicionar_ao_marco(world, LIVRE)
    item = itens_do_marco(world, LIVRE)[0]
    with pytest.raises(ChecklistTextRequired):
        atualizar(world, item, texto="   ")
    assert itens_do_marco(world, LIVRE)[0] == item


def test_editar_item_inexistente_e_404(world):
    adicionar_ao_marco(world, LIVRE)
    item = itens_do_marco(world, LIVRE)[0]
    fantasma = ChecklistItemDto(world.ids.new_id(), "x", False, 0, 1)
    with pytest.raises(NotFound):
        atualizar(world, fantasma)
    assert item


# --- remover ---------------------------------------------------------------------------------


def test_remover_e_logico_some_da_lista_e_nao_toca_o_dono(world):
    adicionar_ao_marco(world, LIVRE)
    adicionar_ao_marco(world, LIVRE, "Fica")
    dono = marco(world, LIVRE)
    item = dono.checklist[0]
    world.use_cases().remove_checklist_item.execute(
        RemoveChecklistItemCommand(item.id, item.version), NOIVA
    )
    depois = marco(world, LIVRE)
    assert [i.text for i in depois.checklist] == ["Fica"]
    assert depois.version == dono.version
    guardado = world.store.items[item.id]
    assert (guardado.deleted_at, guardado.deleted_by) == (world.clock.now(), NOIVA.user_id)


def test_remover_com_version_velha_e_conflito(world):
    adicionar_ao_marco(world, LIVRE)
    item = itens_do_marco(world, LIVRE)[0]
    atualizar(world, item, feito=True)
    with pytest.raises(VersionConflict):
        world.use_cases().remove_checklist_item.execute(
            RemoveChecklistItemCommand(item.id, item.version), NOIVO
        )
    assert len(itens_do_marco(world, LIVRE)) == 1


def test_remover_duas_vezes_e_404_e_nao_ha_como_restaurar_o_item(world):
    adicionar_ao_marco(world, LIVRE)
    item = itens_do_marco(world, LIVRE)[0]
    comando = RemoveChecklistItemCommand(item.id, item.version)
    world.use_cases().remove_checklist_item.execute(comando, NOIVO)
    with pytest.raises(NotFound):
        world.use_cases().remove_checklist_item.execute(comando, NOIVO)
    with pytest.raises(NotFound):
        atualizar(world, item, texto="Voltar")


# --- reordenar -------------------------------------------------------------------------------


def _ordenar(world, tipo, dono, ids):
    return world.use_cases().reorder_checklist.execute(
        ReorderChecklistCommand(tipo, dono, tuple(ids)), NOIVO
    )


def test_reordenar_aplica_a_permutacao_e_reatribui_as_posicoes_de_zero_a_n_menos_1(world):
    for texto in ("A", "B", "C", "D"):
        adicionar_ao_marco(world, LIVRE, texto)
    a, b, c, d = itens_do_marco(world, LIVRE)
    _ordenar(world, OwnerKind.MILESTONE, marco_id(LIVRE), [d.id, b.id, a.id, c.id])
    depois = itens_do_marco(world, LIVRE)
    assert [(i.text, i.position) for i in depois] == [("D", 0), ("B", 1), ("A", 2), ("C", 3)]


def test_reordenar_so_mexe_nos_vivos_e_deixa_as_posicoes_densas(world):
    for texto in ("A", "B", "C"):
        adicionar_ao_marco(world, LIVRE, texto)
    a, b, c = itens_do_marco(world, LIVRE)
    world.use_cases().remove_checklist_item.execute(
        RemoveChecklistItemCommand(b.id, b.version), NOIVO
    )
    _ordenar(world, OwnerKind.MILESTONE, marco_id(LIVRE), [c.id, a.id])
    assert [(i.text, i.position) for i in itens_do_marco(world, LIVRE)] == [("C", 0), ("A", 1)]
    assert world.store.items[b.id].position == 1  # o removido não é tocado


def test_reordenar_nao_usa_version_e_nao_toca_o_dono(world):
    for texto in ("A", "B"):
        adicionar_ao_marco(world, LIVRE, texto)
    a, b = itens_do_marco(world, LIVRE)
    dono = marco(world, LIVRE)
    _ordenar(world, OwnerKind.MILESTONE, marco_id(LIVRE), [b.id, a.id])
    assert marco(world, LIVRE).version == dono.version


def test_reordenar_a_avulsa(world):
    tarefa = nova_avulsa(world)
    for texto in ("A", "B"):
        adicionar(world, OwnerKind.TASK, tarefa.id, texto)
    a, b = itens_da_avulsa(world, tarefa.id)
    _ordenar(world, OwnerKind.TASK, tarefa.id, [b.id, a.id])
    assert [i.text for i in itens_da_avulsa(world, tarefa.id)] == ["B", "A"]


def test_reordenar_com_a_mesma_ordem_nao_sobe_nenhuma_version(world):
    for texto in ("A", "B"):
        adicionar_ao_marco(world, LIVRE, texto)
    antes = itens_do_marco(world, LIVRE)
    _ordenar(world, OwnerKind.MILESTONE, marco_id(LIVRE), [i.id for i in antes])
    assert itens_do_marco(world, LIVRE) == antes


def test_reordenar_dono_sem_itens_com_lista_vazia_vale(world):
    _ordenar(world, OwnerKind.MILESTONE, marco_id(LIVRE), [])


def test_reordenar_o_que_nao_e_permutacao_exata_dos_vivos_e_422_e_nao_muda_nada(world):
    for texto in ("A", "B", "C"):
        adicionar_ao_marco(world, LIVRE, texto)
    adicionar_ao_marco(world, "C02", "De outro marco")
    a, b, c = itens_do_marco(world, LIVRE)
    de_outro = itens_do_marco(world, "C02")[0]
    removido_pelo_usuario = ChecklistItemDto(world.ids.new_id(), "x", False, 0, 1)
    invalidas = [
        [a.id, b.id],  # falta um
        [a.id, b.id, c.id, c.id],  # repete
        [a.id, b.id, c.id, de_outro.id],  # sobra um de outro dono
        [a.id, b.id, de_outro.id],  # troca um por outro dono
        [a.id, b.id, c.id, removido_pelo_usuario.id],  # item que não existe
        [],
    ]
    for ids in invalidas:
        with pytest.raises(InvalidChecklistOrder):
            _ordenar(world, OwnerKind.MILESTONE, marco_id(LIVRE), ids)
    assert [i.text for i in itens_do_marco(world, LIVRE)] == ["A", "B", "C"]


def test_reordenar_com_item_removido_na_lista_e_422(world):
    for texto in ("A", "B"):
        adicionar_ao_marco(world, LIVRE, texto)
    a, b = itens_do_marco(world, LIVRE)
    world.use_cases().remove_checklist_item.execute(
        RemoveChecklistItemCommand(b.id, b.version), NOIVO
    )
    with pytest.raises(InvalidChecklistOrder):
        _ordenar(world, OwnerKind.MILESTONE, marco_id(LIVRE), [a.id, b.id])


def test_reordenar_dono_inexistente_e_404(world):
    with pytest.raises(NotFound):
        _ordenar(world, OwnerKind.TASK, world.ids.new_id(), [])
    with pytest.raises(NotFound):
        _ordenar(world, OwnerKind.MILESTONE, world.ids.new_id(), [])


# --- o dono excluído ------------------------------------------------------------------------


def test_excluir_o_marco_esconde_os_itens_sem_apagar_e_restaurar_traz_de_volta(world):
    adicionar_ao_marco(world, LIVRE, "A")
    adicionar_ao_marco(world, LIVRE, "B")
    item_a = itens_do_marco(world, LIVRE)[0]
    atualizar(world, item_a, feito=True)
    estavam = itens_do_marco(world, LIVRE)
    dono = marco(world, LIVRE)
    world.use_cases().delete_milestone.execute(DeleteMilestoneCommand(dono.id, dono.version), NOIVO)
    assert all(m.id != dono.id for f in ler(world).phases for m in f.milestones)
    assert all(i.deleted_at is None for i in world.store.items.values())  # nada foi apagado

    world.use_cases().restore_milestone.execute(RestoreMilestoneCommand(dono.id), NOIVO)
    assert itens_do_marco(world, LIVRE) == estavam


def test_com_o_marco_excluido_nada_se_faz_com_os_itens_dele(world):
    adicionar_ao_marco(world, LIVRE)
    item = itens_do_marco(world, LIVRE)[0]
    dono = marco(world, LIVRE)
    world.use_cases().delete_milestone.execute(DeleteMilestoneCommand(dono.id, dono.version), NOIVO)
    with pytest.raises(NotFound):
        atualizar(world, item, feito=True)
    with pytest.raises(NotFound):
        world.use_cases().remove_checklist_item.execute(
            RemoveChecklistItemCommand(item.id, item.version), NOIVO
        )
    with pytest.raises(NotFound):
        adicionar_ao_marco(world, LIVRE)
    with pytest.raises(NotFound):
        _ordenar(world, OwnerKind.MILESTONE, marco_id(LIVRE), [item.id])


def test_excluir_a_avulsa_esconde_os_itens_e_restaurar_traz_de_volta(world):
    tarefa = nova_avulsa(world)
    adicionar(world, OwnerKind.TASK, tarefa.id, "A")
    estavam = itens_da_avulsa(world, tarefa.id)
    item = estavam[0]
    world.use_cases().delete_task.execute(DeleteTaskCommand(tarefa.id, tarefa.version), NOIVO)
    with pytest.raises(NotFound):
        atualizar(world, item, feito=True)
    restaurada = world.use_cases().restore_task.execute(RestoreTaskCommand(tarefa.id), NOIVO)
    volta = next(t for t in restaurada.tasks if t.id == tarefa.id)
    assert volta.checklist == estavam
    atualizar(world, item, feito=True)  # e o item volta a responder


# --- concluir o marco com itens em aberto (F-CRN-07, regra 5) ---------------------------------


def test_concluir_o_marco_com_item_em_aberto_pede_a_confirmacao_e_nao_grava(world):
    adicionar_ao_marco(world, LIVRE)
    with pytest.raises(ChecklistOpenItems):
        estado_do_marco(world, LIVRE, ManualState.DONE)
    assert marco(world, LIVRE).state is MilestoneState.UNLOCKED
    assert world.store.changes == []


def test_concluir_mesmo_assim_preserva_os_itens_e_grava_o_historico_de_sempre(world):
    adicionar_ao_marco(world, LIVRE, "A")
    adicionar_ao_marco(world, LIVRE, "B")
    antes = itens_do_marco(world, LIVRE)
    estado_do_marco(world, LIVRE, ManualState.DONE, ignorar_itens=True)
    depois = marco(world, LIVRE)
    assert depois.state is MilestoneState.DONE
    assert depois.checklist == antes
    assert (depois.checklist_progress.done, depois.checklist_progress.total) == (0, 2)
    (mudanca,) = world.store.changes
    assert (mudanca.state_before, mudanca.state_after, mudanca.ignored_block) == (
        None,
        ManualState.DONE,
        False,
    )


def test_concluir_com_todos_os_itens_feitos_nao_pede_nada(world):
    adicionar_ao_marco(world, LIVRE)
    atualizar(world, itens_do_marco(world, LIVRE)[0], feito=True)
    estado_do_marco(world, LIVRE, ManualState.DONE)
    assert marco(world, LIVRE).state is MilestoneState.DONE


def test_item_removido_nao_conta_como_em_aberto(world):
    adicionar_ao_marco(world, LIVRE)
    item = itens_do_marco(world, LIVRE)[0]
    world.use_cases().remove_checklist_item.execute(
        RemoveChecklistItemCommand(item.id, item.version), NOIVO
    )
    estado_do_marco(world, LIVRE, ManualState.DONE)
    assert marco(world, LIVRE).state is MilestoneState.DONE


def test_ignore_open_items_so_vale_ao_concluir_e_nao_e_422_com_outro_destino(world):
    adicionar_ao_marco(world, LIVRE)
    estado_do_marco(world, LIVRE, ManualState.IN_PROGRESS, ignorar_itens=True)
    assert marco(world, LIVRE).state is MilestoneState.IN_PROGRESS
    estado_do_marco(world, LIVRE, ManualState.IN_PROGRESS)  # nem a permissão é preciso
    estado_do_marco(world, LIVRE, None)  # reabrir com item em aberto também passa
    assert marco(world, LIVRE).state is MilestoneState.UNLOCKED


def test_ir_para_em_andamento_com_item_em_aberto_nao_pede_a_confirmacao_dos_itens(world):
    adicionar_ao_marco(world, LIVRE)
    estado_do_marco(world, LIVRE, ManualState.IN_PROGRESS)
    assert marco(world, LIVRE).state is MilestoneState.IN_PROGRESS


def test_repetir_o_estado_concluido_nao_checa_nada(world):
    estado_do_marco(world, LIVRE, ManualState.DONE)
    adicionar_ao_marco(world, LIVRE)  # item aberto num marco já concluído
    estado_do_marco(world, LIVRE, ManualState.DONE)  # no-op
    assert marco(world, LIVRE).state is MilestoneState.DONE
    assert len(world.store.changes) == 1


def test_a_version_vem_antes_de_tudo(world):
    adicionar_ao_marco(world, LIVRE)
    comando = ChangeMilestoneStateCommand(marco_id(LIVRE), ManualState.DONE, False, 99)
    with pytest.raises(VersionConflict):
        world.use_cases().change_milestone_state.execute(comando, NOIVO)


def test_o_bloqueio_vem_antes_dos_itens_em_aberto(world):
    world.classify_all(Standing.ENTERS)
    adicionar_ao_marco(world, BLOQUEADO)
    assert marco(world, BLOQUEADO).state is MilestoneState.BLOCKED
    # Sem nenhuma das duas, o primeiro a falar é o bloqueio.
    with pytest.raises(MilestoneBlocked):
        estado_do_marco(world, BLOQUEADO, ManualState.DONE)
    # Nem a permissão dos itens substitui a confirmação do bloqueio.
    with pytest.raises(MilestoneBlocked):
        estado_do_marco(world, BLOQUEADO, ManualState.DONE, ignorar_itens=True)
    # Com a confirmação do bloqueio, os itens em aberto ainda pedem a deles.
    with pytest.raises(ChecklistOpenItems):
        estado_do_marco(world, BLOQUEADO, ManualState.DONE, ignorar_bloqueio=True)
    estado_do_marco(world, BLOQUEADO, ManualState.DONE, ignorar_bloqueio=True, ignorar_itens=True)
    (mudanca,) = world.store.changes
    assert mudanca.ignored_block is True
    assert marco(world, BLOQUEADO).state is MilestoneState.DONE
