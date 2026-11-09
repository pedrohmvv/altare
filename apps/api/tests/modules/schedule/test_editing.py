"""Fases e marcos editáveis (F-CRN-01) e dependências sem ciclo (F-CRN-03, regra 2), nos casos de
uso, com as portas de mentira e o catálogo inicial inteiro em memória."""

from uuid import UUID

import pytest
from tests.modules.schedule.catalog import categoria_id, fase_id, marco_id
from tests.modules.schedule.conftest import NOIVA, NOIVO

from wedding.modules.schedule.application.commands.change_milestone_state import (
    ChangeMilestoneStateCommand,
)
from wedding.modules.schedule.application.commands.create_milestone import CreateMilestoneCommand
from wedding.modules.schedule.application.commands.create_phase import CreatePhaseCommand
from wedding.modules.schedule.application.commands.delete_milestone import DeleteMilestoneCommand
from wedding.modules.schedule.application.commands.rename_phase import RenamePhaseCommand
from wedding.modules.schedule.application.commands.reorder_phases import ReorderPhasesCommand
from wedding.modules.schedule.application.commands.restore_milestone import (
    RestoreMilestoneCommand,
)
from wedding.modules.schedule.application.commands.set_milestone_dependencies import (
    SetMilestoneDependenciesCommand,
)
from wedding.modules.schedule.application.commands.update_milestone import UpdateMilestoneCommand
from wedding.modules.schedule.application.dto import (
    CATEGORY_UNCLASSIFIED_LABEL,
    LeftOutDirection,
    ScheduleDto,
)
from wedding.modules.schedule.application.ports import CategoryInfo
from wedding.modules.schedule.domain.errors import (
    CategoryNotAvailable,
    DependencyCycle,
    InvalidPhaseOrder,
    InvalidScheduleValue,
    MilestoneTitleRequired,
    PhaseTitleRequired,
    SelfDependency,
)
from wedding.modules.schedule.domain.values import ManualState, MilestoneState, Standing
from wedding.shared_kernel.errors import NotFound, VersionConflict
from wedding.shared_kernel.profile import ProfileKind

ENTRA = Standing.ENTERS


def ler(world, ator=NOIVO) -> ScheduleDto:
    return world.use_cases().read_schedule.execute(ator)


def marco(cronograma: ScheduleDto, codigo: str):
    return next(m for f in cronograma.phases for m in f.milestones if m.id == marco_id(codigo))


def por_titulo(cronograma: ScheduleDto, titulo: str):
    return next(m for f in cronograma.phases for m in f.milestones if m.title == titulo)


def fase(cronograma: ScheduleDto, numero: int):
    return next(f for f in cronograma.phases if f.id == fase_id(numero))


def ids_da_fase(cronograma: ScheduleDto, numero: int) -> list[UUID]:
    return [m.id for m in fase(cronograma, numero).milestones]


def criar(world, titulo="Marco Exemplo", numero_da_fase=1, *, depende=(), categoria=None, **extra):
    ator = extra.pop("ator", NOIVO)
    comando = CreateMilestoneCommand(
        title=titulo,
        phase_id=extra.pop("phase_id", fase_id(numero_da_fase)),
        responsible=extra.pop("responsavel", ProfileKind.AMBOS),
        category_id=categoria,
        depends_on=tuple(depende),
    )
    return world.use_cases().create_milestone.execute(comando, ator).schedule


def editar(world, codigo, *, versao=None, ator=NOIVO, **campos):
    cronograma = ler(world)
    item = marco(cronograma, codigo)
    dono = next(f for f in cronograma.phases if item in f.milestones)
    comando = UpdateMilestoneCommand(
        milestone_id=marco_id(codigo),
        title=campos.get("titulo", item.title),
        phase_id=campos.get("phase_id", dono.id),
        responsible=campos.get("responsavel", item.responsible),
        category_id=campos.get("categoria", item.category.id if item.category else None),
        note=item.note,
        target_date=item.target_date,
        version=versao if versao is not None else item.version,
    )
    return world.use_cases().update_milestone.execute(comando, ator)


def dependencias(world, codigo, *predecessores, versao=None, ator=NOIVO):
    atual = versao if versao is not None else marco(ler(world), codigo).version
    comando = SetMilestoneDependenciesCommand(
        marco_id(codigo),
        tuple(marco_id(p) if isinstance(p, str) else p for p in predecessores),
        atual,
    )
    return world.use_cases().set_milestone_dependencies.execute(comando, ator)


def excluir(world, codigo, *, versao=None, ator=NOIVO):
    atual = versao if versao is not None else marco(ler(world), codigo).version
    return world.use_cases().delete_milestone.execute(
        DeleteMilestoneCommand(marco_id(codigo), atual), ator
    )


def restaurar(world, codigo, ator=NOIVO):
    return world.use_cases().restore_milestone.execute(
        RestoreMilestoneCommand(marco_id(codigo)), ator
    )


def depende_de(cronograma, codigo):
    return [d.id for d in marco(cronograma, codigo).depends_on]


def libera(cronograma, codigo):
    return [u.id for u in marco(cronograma, codigo).unlocks]


# --- criar marco -------------------------------------------------------------------------------


def test_marco_novo_nasce_no_fim_da_fase_sem_estado_manual_sem_prazo_e_ambos(world):  # F-CRN-01
    antes = ids_da_fase(ler(world), 4)
    cronograma = criar(world, "  Marco Novo Exemplo ", 4)
    novo = por_titulo(cronograma, "Marco Novo Exemplo")
    assert ids_da_fase(cronograma, 4) == [*antes, novo.id]
    assert novo.position == len(antes)
    assert (novo.responsible, novo.target_date, novo.note) == (ProfileKind.AMBOS, None, None)
    assert (novo.version, novo.category, novo.depends_on, novo.unlocks) == (1, None, (), ())
    assert novo.id not in {marco_id(f"C{n:02d}") for n in range(1, 30)}


def test_marco_novo_sem_dependencias_nem_categoria_esta_destravado(world):  # F-CRN-01
    novo = por_titulo(criar(world), "Marco Exemplo")
    assert novo.state is MilestoneState.UNLOCKED
    assert novo.blocked_by == ()


def test_marco_novo_com_categoria_em_discussao_nasce_bloqueado_pela_categoria(world):  # F-CRN-04
    cronograma = criar(world, categoria=categoria_id("Espaço"))
    novo = por_titulo(cronograma, "Marco Exemplo")
    assert novo.state is MilestoneState.BLOCKED
    assert [b.label for b in novo.blocked_by] == [CATEGORY_UNCLASSIFIED_LABEL]
    assert novo.category is not None
    assert (novo.category.id, novo.category.name) == (categoria_id("Espaço"), "Espaço")


def test_marco_novo_com_categoria_que_entra_nasce_destravado(world):
    world.classify_all(ENTRA)
    novo = por_titulo(criar(world, categoria=categoria_id("Espaço")), "Marco Exemplo")
    assert novo.state is MilestoneState.UNLOCKED


def test_marco_novo_com_dependencias_aguarda_os_predecessores_e_aparece_em_libera(world):
    cronograma = criar(world, depende=[marco_id("C01"), marco_id("C02")])
    novo = por_titulo(cronograma, "Marco Exemplo")
    assert novo.state is MilestoneState.BLOCKED
    assert [b.label for b in novo.blocked_by] == [
        "Classificar o Mapa de Escopo",
        "Montar a lista preliminar de convidados",
    ]
    assert {d.id for d in novo.depends_on} == {marco_id("C01"), marco_id("C02")}
    assert novo.id in libera(cronograma, "C01")


def test_dependencia_repetida_na_criacao_e_tratada_como_conjunto(world):
    cronograma = criar(world, depende=[marco_id("C01"), marco_id("C01")])
    assert len(por_titulo(cronograma, "Marco Exemplo").depends_on) == 1
    assert len(world.store.links) == 31 + 1


def test_marco_sem_titulo_e_recusado(world):  # F-CRN-01
    for titulo in ("", "   "):
        with pytest.raises(MilestoneTitleRequired):
            criar(world, titulo)
    assert len(ler(world).phases[0].milestones) == 4


def test_titulo_longo_demais_e_recusado(world):
    with pytest.raises(InvalidScheduleValue):
        criar(world, "x" * 121)


def test_criar_em_fase_inexistente_ou_com_predecessor_inexistente_e_nao_encontrado(world):
    with pytest.raises(NotFound):
        criar(world, phase_id=UUID(int=4242))
    with pytest.raises(NotFound):
        criar(world, depende=[UUID(int=4242)])


def test_predecessor_excluido_nao_vale(world):
    excluir(world, "C01")
    with pytest.raises(NotFound):
        criar(world, depende=[marco_id("C01")])


def test_categoria_oculta_ou_inexistente_nao_pode_ser_ligada(world):
    world.classify("Espaço", ENTRA, visible=False)
    with pytest.raises(CategoryNotAvailable):
        criar(world, categoria=categoria_id("Espaço"))
    with pytest.raises(CategoryNotAvailable):
        criar(world, categoria=UUID(int=4242))


def test_criar_nao_altera_o_resto_do_cronograma(world):
    antes = ler(world)
    depois = criar(world)
    for codigo in ("C01", "C06", "C29"):
        assert marco(depois, codigo) == marco(antes, codigo)


def test_criar_marco_devolve_o_id_do_marco_criado_junto_com_o_cronograma(world):
    comando = CreateMilestoneCommand(
        "Marco Com Id Exemplo", fase_id(4), ProfileKind.AMBOS, None, ()
    )
    criado = world.use_cases().create_milestone.execute(comando, NOIVO)
    assert criado.milestone_id == por_titulo(criado.schedule, "Marco Com Id Exemplo").id
    assert ids_da_fase(criado.schedule, 4)[-1] == criado.milestone_id
    assert criado.schedule == ler(world)


# --- editar marco ------------------------------------------------------------------------------


def test_renomear_o_marco_troca_o_titulo_e_aparece_nas_listas_dos_outros(world):  # F-CRN-01
    cronograma = editar(world, "C06", titulo="  Fechar o Salão ")
    assert marco(cronograma, "C06").title == "Fechar o Salão"
    assert marco(cronograma, "C06").version == 2
    assert [d.title for d in marco(cronograma, "C07").depends_on] == ["Fechar o Salão"]
    assert [b.label for b in marco(cronograma, "C06").blocked_by][-1] == (
        "Definir a data (ou janela de datas)"
    )


def test_renomear_para_vazio_e_recusado(world):
    with pytest.raises(MilestoneTitleRequired):
        editar(world, "C06", titulo=" ")


def test_mover_de_fase_vai_para_o_fim_da_nova_fase_sem_mexer_nas_dependencias(world):  # F-CRN-01
    antes = ler(world)
    nova = fase_id(5)
    cronograma = editar(world, "C06", phase_id=nova)
    assert ids_da_fase(cronograma, 5)[-1] == marco_id("C06")
    assert marco(cronograma, "C06").position == len(ids_da_fase(antes, 5))
    assert marco_id("C06") not in ids_da_fase(cronograma, 2)
    assert depende_de(cronograma, "C06") == depende_de(antes, "C06")
    assert libera(cronograma, "C06") == libera(antes, "C06")
    assert marco(cronograma, "C06").state == marco(antes, "C06").state


def test_mover_nao_muda_a_posicao_dos_outros_marcos(world):
    antes = ler(world)
    cronograma = editar(world, "C07", phase_id=fase_id(1))
    for codigo in ("C08", "C09", "C10"):
        assert marco(cronograma, codigo).position == marco(antes, codigo).position


def test_mover_para_a_fase_em_que_ja_esta_nao_muda_nada(world):
    antes = ler(world)
    assert editar(world, "C07", phase_id=fase_id(3)) == antes


def test_mover_para_fase_inexistente_e_nao_encontrado(world):
    with pytest.raises(NotFound):
        editar(world, "C06", phase_id=UUID(int=4242))


def test_trocar_a_categoria_muda_o_efeito_derivado_e_nao_o_estado_marcado(world):  # F-CRN-04
    world.classify_all(ENTRA)
    world.classify("Fotografia", Standing.OUT)
    antes = marco(ler(world), "C08")
    assert antes.archived is True
    cronograma = editar(world, "C08", categoria=categoria_id("Buffet"))
    assert marco(cronograma, "C08").archived is False
    assert marco(cronograma, "C08").category.id == categoria_id("Buffet")  # type: ignore[union-attr]
    sem = editar(world, "C08", categoria=None)
    assert marco(sem, "C08").category is None


def test_trocar_para_categoria_em_discussao_bloqueia_e_guarda_o_estado_manual(world):
    world.classify_all(ENTRA)
    world.classify("Buffet", Standing.IN_DISCUSSION)
    editar(world, "C01", categoria=None)
    cronograma = editar(world, "C01", categoria=categoria_id("Buffet"))
    assert marco(cronograma, "C01").state is MilestoneState.BLOCKED


def test_manter_a_categoria_ja_ligada_mesmo_oculta_nao_e_erro(world):
    world.classify("Espaço", ENTRA, visible=False)
    cronograma = editar(world, "C06", titulo="Fechar o Salão")
    assert marco(cronograma, "C06").title == "Fechar o Salão"
    assert marco(cronograma, "C06").category.id == categoria_id("Espaço")  # type: ignore[union-attr]


def test_trocar_para_categoria_oculta_e_recusado(world):
    world.classify("Buffet", ENTRA, visible=False)
    with pytest.raises(CategoryNotAvailable):
        editar(world, "C06", categoria=categoria_id("Buffet"))


def test_editar_marco_arquivado_continua_permitido(world):
    world.classify_all(ENTRA)
    world.classify("Fotografia", Standing.OUT)
    cronograma = editar(world, "C08", titulo="Fotos", responsavel=ProfileKind.NOIVA)
    assert (marco(cronograma, "C08").title, marco(cronograma, "C08").archived) == ("Fotos", True)


def test_editar_igual_nao_sobe_a_version(world):
    antes = ler(world)
    assert editar(world, "C06") == antes


def test_editar_com_version_velha_e_conflito(world):
    editar(world, "C06", titulo="Fechar o Salão")
    with pytest.raises(VersionConflict):
        editar(world, "C06", titulo="Outro", versao=1)


# --- excluir marco -----------------------------------------------------------------------------


def test_excluir_marco_tira_ele_das_fases_e_das_listas_dos_outros(world):  # F-CRN-01
    cronograma = excluir(world, "C06")
    assert marco_id("C06") not in {m.id for f in cronograma.phases for m in f.milestones}
    assert marco_id("C06") not in depende_de(cronograma, "C07")
    assert marco_id("C06") not in libera(cronograma, "C05")
    assert marco_id("C06") not in [
        b.milestone_id for m in fase(cronograma, 3).milestones for b in m.blocked_by
    ]


def test_os_dependentes_mantem_as_demais_dependencias_e_o_estado_e_recalculado(world):
    world.classify_all(ENTRA)
    antes = ler(world)
    assert [b.label for b in marco(antes, "C20").blocked_by] == [
        "Montar a lista preliminar de convidados",
        "Fechar o Espaço",
    ]
    cronograma = excluir(world, "C06")
    assert depende_de(cronograma, "C20") == [marco_id("C02")]
    assert [b.label for b in marco(cronograma, "C20").blocked_by] == [
        "Montar a lista preliminar de convidados"
    ]
    # O C07 só dependia do C06: sem ele, destrava.
    assert marco(antes, "C07").state is MilestoneState.BLOCKED
    assert marco(cronograma, "C07").state is MilestoneState.UNLOCKED


def test_excluir_carimba_o_marco_e_os_vinculos_dos_dois_sentidos_com_o_mesmo_instante(world):
    world.clock.advance(minutes=5)
    excluir(world, "C06", ator=NOIVA)
    agora = world.clock.now()
    marco_excluido = world.store.milestones[marco_id("C06")]
    assert (marco_excluido.deleted_at, marco_excluido.deleted_by) == (agora, NOIVA.user_id)
    tocam = [
        link
        for link in world.store.links
        if marco_id("C06") in (link.milestone_id, link.depends_on_id)
    ]
    assert len(tocam) == 1 + 10  # C06 depende do C05 e libera 10 marcos
    assert {(link.deleted_at, link.deleted_by) for link in tocam} == {(agora, NOIVA.user_id)}
    assert all(
        link.deleted_at is None
        for link in world.store.links
        if marco_id("C06") not in (link.milestone_id, link.depends_on_id)
    )


def test_excluir_preserva_o_historico_de_estado(world):
    world.use_cases().change_milestone_state.execute(
        ChangeMilestoneStateCommand(marco_id("C01"), ManualState.DONE, False, 1),
        NOIVO,
    )
    excluir(world, "C01")
    assert [c.milestone_id for c in world.store.changes] == [marco_id("C01")]


def test_excluir_diminui_o_progresso_da_fase(world):
    assert fase(ler(world), 1).progress.total == 4
    assert fase(excluir(world, "C01"), 1).progress.total == 3


def test_excluir_com_version_velha_e_conflito_e_nao_muda_nada(world):
    editar(world, "C06", titulo="Fechar o Salão")
    with pytest.raises(VersionConflict):
        excluir(world, "C06", versao=1)
    assert world.store.milestones[marco_id("C06")].deleted_at is None


def test_excluir_marco_inexistente_ou_ja_excluido_e_nao_encontrado(world):
    with pytest.raises(NotFound):
        world.use_cases().delete_milestone.execute(DeleteMilestoneCommand(UUID(int=4242), 1), NOIVO)
    excluir(world, "C06")
    with pytest.raises(NotFound):
        world.use_cases().delete_milestone.execute(
            DeleteMilestoneCommand(marco_id("C06"), 1), NOIVO
        )


# --- restaurar marco ---------------------------------------------------------------------------


def test_excluir_marco_com_dois_dependentes_e_restaurar_traz_o_marco_e_as_dependencias(
    world,
):  # F-CRN-01
    antes = ler(world)
    assert len(libera(antes, "C26")) == 2  # C28 e C29
    excluir(world, "C26")
    resposta = restaurar(world, "C26")
    assert resposta.left_out == ()
    depois = resposta.schedule
    assert depende_de(depois, "C26") == depende_de(antes, "C26")
    assert libera(depois, "C26") == libera(antes, "C26")
    assert depende_de(depois, "C28") == depende_de(antes, "C28")
    assert depende_de(depois, "C29") == depende_de(antes, "C29")


def test_restaurar_o_marco_manda_ele_para_o_fim_da_fase_original(world):
    excluir(world, "C07")
    resposta = restaurar(world, "C07")
    assert ids_da_fase(resposta.schedule, 3)[-1] == marco_id("C07")
    assert marco(resposta.schedule, "C07").position == 7


def test_restaurar_mantem_o_estado_marcado_antes_de_excluir(world):
    world.use_cases().change_milestone_state.execute(
        ChangeMilestoneStateCommand(marco_id("C01"), ManualState.DONE, False, 1),
        NOIVO,
    )
    excluir(world, "C01")
    assert marco(restaurar(world, "C01").schedule, "C01").state is MilestoneState.DONE


def test_restaurar_deixa_de_fora_a_dependencia_que_hoje_fecharia_um_ciclo(world):  # D-080
    antes = ler(world)
    excluir(world, "C26")  # C26 depende do C25; C28 e C29 dependem do C26
    dependencias(
        world, "C25", "C28"
    )  # agora o C25 depende do C28: restaurar fecharia C26→C25→C28→C26
    resposta = restaurar(world, "C26")
    depois = resposta.schedule
    assert [(x.milestone_id, x.title, x.direction) for x in resposta.left_out] == [
        (marco_id("C28"), "Quitar os contratos", LeftOutDirection.DEPENDENCY_OF)
    ]
    assert depende_de(depois, "C26") == depende_de(antes, "C26")
    assert depende_de(depois, "C28") == []
    assert depende_de(depois, "C29") == depende_de(antes, "C29")


def test_restaurar_deixa_de_fora_tambem_o_dependente_que_fecharia_ciclo_pelo_que_voltou(world):
    excluir(world, "C26")
    # Hoje o C25 depende do C29, que dependia do C26: voltar C26→C25 e C29→C26 fecharia um ciclo.
    dependencias(world, "C25", "C29")
    resposta = restaurar(world, "C26")
    assert [(x.milestone_id, x.direction) for x in resposta.left_out] == [
        (marco_id("C29"), LeftOutDirection.DEPENDENCY_OF)
    ]
    assert depende_de(resposta.schedule, "C26") == [marco_id("C25")]
    assert depende_de(resposta.schedule, "C28") == [marco_id("C26")]


def test_restaurar_deixa_de_fora_a_dependencia_do_marco_cuja_ponta_esta_excluida(world):
    excluir(world, "C26")  # o C26 depende do C25
    world.clock.advance(minutes=1)
    excluir(world, "C25")
    resposta = restaurar(world, "C26")
    assert [(x.milestone_id, x.title, x.direction) for x in resposta.left_out] == [
        (marco_id("C25"), "Enviar os convites", LeftOutDirection.DEPENDS_ON)
    ]
    assert depende_de(resposta.schedule, "C26") == []
    assert libera(resposta.schedule, "C26") == [marco_id("C28"), marco_id("C29")]


def test_restaurar_deixa_de_fora_a_dependencia_cuja_outra_ponta_esta_excluida(world):
    excluir(world, "C06")
    world.clock.advance(minutes=1)
    excluir(world, "C07")  # o vínculo C07→C06 saiu com o carimbo do C06
    resposta = restaurar(world, "C06")
    assert [(x.milestone_id, x.title, x.direction) for x in resposta.left_out] == [
        (marco_id("C07"), "Fechar o Buffet", LeftOutDirection.DEPENDENCY_OF)
    ]
    assert marco_id("C07") not in libera(resposta.schedule, "C06")


def test_restaurar_o_outro_depois_nao_recompoe_o_que_ficou_de_fora(world):
    excluir(world, "C06")
    world.clock.advance(minutes=1)
    excluir(world, "C07")
    restaurar(world, "C06")
    depois = restaurar(world, "C07")
    assert marco_id("C06") not in depende_de(depois.schedule, "C07")
    # O C07 volta com as dependências que saíram com ele: nenhuma (o C07 só dependia do C06).
    assert depende_de(depois.schedule, "C07") == []


def test_restaurar_o_marco_que_saiu_depois_traz_o_que_saiu_com_ele(world):
    excluir(world, "C06")
    world.clock.advance(minutes=1)
    excluir(world, "C07")
    restaurar(world, "C07")  # o C06 ainda está excluído; o C07→C06 não volta
    restaurar(world, "C06")
    # Os vínculos do C07 com o carimbo dele (C16, C17, C27 dependem do C07) voltaram.
    final = ler(world)
    assert {marco_id("C16"), marco_id("C17"), marco_id("C27")} <= set(libera(final, "C07"))


def test_restaurar_marco_que_nao_foi_excluido_ou_nao_existe_e_nao_encontrado(world):
    with pytest.raises(NotFound):
        restaurar(world, "C06")
    with pytest.raises(NotFound):
        world.use_cases().restore_milestone.execute(RestoreMilestoneCommand(UUID(int=4242)), NOIVO)


def test_restaurar_duas_vezes_a_segunda_e_nao_encontrado(world):
    excluir(world, "C06")
    restaurar(world, "C06")
    with pytest.raises(NotFound):
        restaurar(world, "C06")


def test_o_vinculo_tirado_a_mao_antes_nao_volta_com_o_marco(world):
    world.clock.advance(minutes=1)
    dependencias(world, "C07")  # tira o C07→C06 a mão
    world.clock.advance(minutes=1)
    excluir(world, "C06")
    resposta = restaurar(world, "C06")
    assert marco_id("C07") not in libera(resposta.schedule, "C06")
    assert resposta.left_out == ()


# --- dependências ------------------------------------------------------------------------------


def test_definir_dependencias_troca_o_conjunto_e_sobe_a_version_do_marco(world):  # F-CRN-03
    cronograma = dependencias(world, "C07", "C01", "C02")
    assert set(depende_de(cronograma, "C07")) == {marco_id("C01"), marco_id("C02")}
    assert marco_id("C07") in libera(cronograma, "C01")
    assert marco_id("C07") not in libera(cronograma, "C06")
    assert marco(cronograma, "C07").version == 2


def test_definir_dependencias_recalcula_o_estado_do_marco(world):
    world.classify_all(ENTRA)
    assert marco(ler(world), "C07").state is MilestoneState.BLOCKED
    assert marco(dependencias(world, "C07"), "C07").state is MilestoneState.UNLOCKED


def test_dependencia_repetida_na_lista_e_um_conjunto(world):
    cronograma = dependencias(world, "C07", "C01", "C01", "C06")
    assert len(depende_de(cronograma, "C07")) == 2


def test_repetir_o_mesmo_conjunto_nao_grava_nada(world):
    antes = ler(world)
    links = len(world.store.links)
    assert dependencias(world, "C07", "C06") == antes
    assert dependencias(world, "C20", "C06", "C02") == antes  # a ordem não importa
    assert len(world.store.links) == links


def test_so_o_que_mudou_e_desativado_ou_criado(world):
    world.clock.advance(minutes=1)
    dependencias(world, "C20", "C02", "C01")  # tira o C06, mantém o C02, acrescenta o C01
    vivos = {
        (link.milestone_id, link.depends_on_id)
        for link in world.store.links
        if link.deleted_at is None and link.milestone_id == marco_id("C20")
    }
    assert vivos == {(marco_id("C20"), marco_id("C02")), (marco_id("C20"), marco_id("C01"))}
    tirados = [
        link
        for link in world.store.links
        if link.deleted_at is not None and link.milestone_id == marco_id("C20")
    ]
    assert [(link.depends_on_id, link.deleted_at) for link in tirados] == [
        (marco_id("C06"), world.clock.now())
    ]


def test_lista_vazia_tira_todas_as_dependencias(world):
    cronograma = dependencias(world, "C20")
    assert depende_de(cronograma, "C20") == []


def test_auto_dependencia_e_recusada(world):
    with pytest.raises(SelfDependency):
        dependencias(world, "C07", "C07")


def test_predecessor_inexistente_ou_excluido_e_nao_encontrado(world):
    with pytest.raises(NotFound):
        dependencias(world, "C07", UUID(int=4242))
    excluir(world, "C01")
    with pytest.raises(NotFound):
        dependencias(world, "C07", "C01")


def test_ciclo_direto_e_recusado_com_o_caminho(world):  # F-CRN-03, regra 2
    # C05 depende de C04; fazer o C04 depender do C05 fecha C04 → C05 → C04.
    with pytest.raises(DependencyCycle) as erro:
        dependencias(world, "C04", "C05")
    assert [p["title"] for p in erro.value.data["path"]] == [
        "Escolher o caminho macro (formato e região)",
        "Definir a data (ou janela de datas)",
        "Escolher o caminho macro (formato e região)",
    ]
    assert erro.value.data["path"][0]["id"] == marco_id("C04")


def test_ciclo_transitivo_mostra_o_caminho_inteiro(world):  # F-CRN-03, regra 2
    # C01 ← C03 ← C04 ← C05: fazer o C01 depender do C05 fecha C01 → C05 → C04 → C03 → C01.
    with pytest.raises(DependencyCycle) as erro:
        dependencias(world, "C01", "C05")
    assert [p["id"] for p in erro.value.data["path"]] == [
        marco_id(c) for c in ("C01", "C05", "C04", "C03", "C01")
    ]
    assert erro.value.detail_params["path"].count(" → ") == 4


def test_ciclo_recusado_nao_grava_nada(world):
    antes = ler(world)
    with pytest.raises(DependencyCycle):
        dependencias(world, "C01", "C05")
    assert ler(world) == antes


def test_dependencias_com_version_velha_e_conflito(world):
    dependencias(world, "C07", "C01")
    with pytest.raises(VersionConflict):
        dependencias(world, "C07", "C02", versao=1)


def test_marco_inexistente_nas_dependencias_e_nao_encontrado(world):
    with pytest.raises(NotFound):
        world.use_cases().set_milestone_dependencies.execute(
            SetMilestoneDependenciesCommand(UUID(int=4242), (), 1), NOIVO
        )


# --- fases -------------------------------------------------------------------------------------


def criar_fase(world, titulo="Fase Exemplo", ator=NOIVO):
    return world.use_cases().create_phase.execute(CreatePhaseCommand(titulo), ator)


def renomear_fase(world, numero, titulo, versao=None):
    atual = versao if versao is not None else fase(ler(world), numero).version
    return world.use_cases().rename_phase.execute(
        RenamePhaseCommand(fase_id(numero), titulo, atual), NOIVO
    )


def reordenar(world, ids):
    return world.use_cases().reorder_phases.execute(ReorderPhasesCommand(tuple(ids)), NOIVO)


def test_fase_nova_vai_para_o_fim_vazia(world):  # F-CRN-01
    cronograma = criar_fase(world, "  Fase Nova Exemplo ")
    ultima = cronograma.phases[-1]
    assert (ultima.title, ultima.position, ultima.milestones, ultima.version) == (
        "Fase Nova Exemplo",
        5,
        (),
        1,
    )
    assert (ultima.progress.done, ultima.progress.total) == (0, 0)
    assert len(cronograma.phases) == 6


def test_fase_sem_titulo_ou_longa_demais_e_recusada(world):
    with pytest.raises(PhaseTitleRequired):
        criar_fase(world, "  ")
    with pytest.raises(InvalidScheduleValue):
        criar_fase(world, "x" * 61)
    criar_fase(world, "x" * 60)


def test_renomear_a_fase_nao_perde_nenhum_marco_dela(world):  # F-CRN-01
    antes = ler(world)
    cronograma = renomear_fase(world, 3, "Fornecedores")
    assert fase(cronograma, 3).title == "Fornecedores"
    assert ids_da_fase(cronograma, 3) == ids_da_fase(antes, 3)
    assert fase(cronograma, 3).milestones == fase(antes, 3).milestones
    assert fase(cronograma, 3).version == 2


def test_renomear_igual_nao_sobe_a_version_e_titulo_vazio_e_recusado(world):
    antes = ler(world)
    assert renomear_fase(world, 3, "Fornecedores Essenciais") == antes
    with pytest.raises(PhaseTitleRequired):
        renomear_fase(world, 3, "")


def test_renomear_com_version_velha_e_conflito_e_fase_inexistente_e_404(world):
    renomear_fase(world, 3, "Fornecedores")
    with pytest.raises(VersionConflict):
        renomear_fase(world, 3, "Outro", versao=1)
    with pytest.raises(NotFound):
        world.use_cases().rename_phase.execute(RenamePhaseCommand(UUID(int=4242), "X", 1), NOIVO)


def test_reordenar_as_fases_troca_as_posicoes_a_partir_de_zero_e_sobe_so_a_version_de_quem_mudou(
    world,
):
    ordem = [fase_id(n) for n in (2, 1, 3, 4, 5)]
    cronograma = reordenar(world, ordem)
    assert [f.id for f in cronograma.phases] == ordem
    assert [f.position for f in cronograma.phases] == [0, 1, 2, 3, 4]
    assert {f.id: f.version for f in cronograma.phases} == {
        fase_id(2): 2,
        fase_id(1): 2,
        fase_id(3): 1,
        fase_id(4): 1,
        fase_id(5): 1,
    }


def test_reordenar_do_jeito_que_ja_esta_nao_muda_nada(world):
    antes = ler(world)
    assert reordenar(world, [f.id for f in antes.phases]) == antes


def test_reordenar_nao_mexe_nos_marcos(world):
    antes = ler(world)
    cronograma = reordenar(world, [fase_id(n) for n in (5, 4, 3, 2, 1)])
    for numero in range(1, 6):
        # "Libera" segue a ordem do cronograma, que muda com a das fases; o resto não.
        assert [
            (m.id, m.title, m.position, m.state, m.version)
            for m in fase(cronograma, numero).milestones
        ] == [
            (m.id, m.title, m.position, m.state, m.version) for m in fase(antes, numero).milestones
        ]


@pytest.mark.parametrize(
    "ordem",
    [
        [],
        [1, 2, 3, 4],
        [1, 2, 3, 4, 5, 5],
        [1, 1, 2, 3, 4],
        [1, 2, 3, 4, 5, 99],
        [1, 2, 3, 4, 99],
    ],
)
def test_reordenar_exige_exatamente_as_fases_vivas(world, ordem):
    ids = [fase_id(n) if n < 10 else UUID(int=4242) for n in ordem]
    with pytest.raises(InvalidPhaseOrder):
        reordenar(world, ids)


# --- categorias que o casal pode ligar ---------------------------------------------------------


def test_as_opcoes_de_categoria_sao_as_visiveis_na_ordem_do_mapa(world):  # F-CRN-01
    world.categories[UUID(int=900)] = CategoryInfo("Frente A Exemplo", ENTRA, True)
    world.categories[UUID(int=901)] = CategoryInfo("Frente B Exemplo", ENTRA, False)
    opcoes = ler(world).category_options
    nomes = [o.name for o in opcoes]
    assert "Frente A Exemplo" in nomes
    assert "Frente B Exemplo" not in nomes
    esperado = [(i, c.name) for i, c in world.categories.items() if c.visible]
    assert [(o.id, o.name) for o in opcoes] == esperado


def test_a_categoria_oculta_ligada_a_um_marco_continua_nas_opcoes(world):
    world.classify("Espaço", ENTRA, visible=False)
    assert categoria_id("Espaço") in [o.id for o in ler(world).category_options]


def test_toda_escrita_devolve_as_opcoes_de_categoria(world):
    total = len(world.categories)
    assert len(criar(world).category_options) == total
    assert len(editar(world, "C06", titulo="Salão").category_options) == total


# --- excluir e restaurar mudam as dependências dos outros: a version deles acompanha ------------


def test_excluir_sobe_a_version_do_dependente_que_perdeu_o_vinculo(world):  # F-CRN-03
    antes = marco(ler(world), "C07").version
    cronograma = excluir(world, "C06")
    assert marco(cronograma, "C07").version == antes + 1
    # Quem não tinha vínculo com o excluído não muda.
    assert marco(cronograma, "C01").version == marco(ler(world), "C01").version == 1


def test_excluir_nao_sobe_a_version_do_predecessor(world):
    antes = marco(ler(world), "C05").version
    assert marco(excluir(world, "C06"), "C05").version == antes


def test_restaurar_sobe_a_version_do_dependente_que_ganhou_o_vinculo_de_volta(world):
    excluir(world, "C06")
    meio = marco(ler(world), "C07").version
    depois = restaurar(world, "C06").schedule
    assert marco(depois, "C07").version == meio + 1


def test_restaurar_nao_sobe_a_version_do_dependente_cujo_vinculo_ficou_de_fora(world):
    excluir(world, "C26")
    dependencias(world, "C25", "C28")  # restaurar não traz o C28→C26
    meio = marco(ler(world), "C28").version
    resposta = restaurar(world, "C26")
    assert [x.milestone_id for x in resposta.left_out] == [marco_id("C28")]
    assert marco(resposta.schedule, "C28").version == meio


def test_dependencias_do_dependente_com_a_version_de_antes_da_exclusao_dao_conflito(world):
    velha = marco(ler(world), "C07").version
    excluir(world, "C06")
    with pytest.raises(VersionConflict):
        dependencias(world, "C07", "C01", versao=velha)


def test_dependencias_do_dependente_com_a_version_de_antes_da_restauracao_dao_conflito(world):
    excluir(world, "C06")
    guardada = marco(ler(world), "C07").version
    restaurar(world, "C06")
    with pytest.raises(VersionConflict):
        dependencias(world, "C07", "C01", versao=guardada)
