from datetime import UTC, date, datetime, timedelta
from uuid import UUID

import pytest
from tests.modules.schedule.catalog import MARCOS, categoria_id, marco_id
from tests.modules.schedule.conftest import NOIVA, NOIVO

from wedding.modules.schedule.application.commands.change_milestone_state import (
    ChangeMilestoneStateCommand,
)
from wedding.modules.schedule.application.commands.update_milestone import UpdateMilestoneCommand
from wedding.modules.schedule.application.dto import (
    CATEGORY_UNCLASSIFIED_LABEL,
    ScheduleDto,
    WarningKind,
)
from wedding.modules.schedule.application.ports import CategoryInfo, WeddingDate
from wedding.modules.schedule.domain.errors import InvalidScheduleValue, MilestoneBlocked
from wedding.modules.schedule.domain.values import (
    BlockerKind,
    ManualState,
    MilestoneState,
    Standing,
)
from wedding.shared_kernel.errors import NotFound, VersionConflict
from wedding.shared_kernel.profile import ProfileKind

ENTRA = Standing.ENTERS


def ler(world, ator=NOIVO) -> ScheduleDto:
    return world.use_cases().read_schedule.execute(ator)


def marco(cronograma: ScheduleDto, codigo: str):
    return next(m for f in cronograma.phases for m in f.milestones if m.id == marco_id(codigo))


def marcar(world, codigo, estado, *, ignorar=False, ator=NOIVO, versao=None):
    atual = versao if versao is not None else marco(ler(world), codigo).version
    return world.use_cases().change_milestone_state.execute(
        ChangeMilestoneStateCommand(marco_id(codigo), estado, ignorar, atual), ator
    )


def concluir(world, *codigos, ignorar=False):
    for codigo in codigos:
        marcar(world, codigo, ManualState.DONE, ignorar=ignorar)


def editar(
    world, codigo, *, responsavel=ProfileKind.AMBOS, nota=None, prazo=None, versao=None, ator=NOIVO
):
    atual = versao if versao is not None else marco(ler(world), codigo).version
    return world.use_cases().update_milestone.execute(
        UpdateMilestoneCommand(marco_id(codigo), responsavel, nota, prazo, atual), ator
    )


def rotulos(item) -> list[str]:
    return [b.label for b in item.blocked_by]


def test_casamento_recem_criado_tem_29_marcos_em_5_fases_todos_ambos_e_sem_prazo(world):  # F-CRN-02
    cronograma = ler(world)
    assert [f.title for f in cronograma.phases] == [
        "Marco Zero",
        "Contrato Âncora",
        "Fornecedores Essenciais",
        "Identidade, Complementares e Convidados",
        "Reta Final",
    ]
    todos = [m for f in cronograma.phases for m in f.milestones]
    assert len(todos) == 29 == len(MARCOS)
    assert {m.responsible for m in todos} == {ProfileKind.AMBOS}
    assert {m.target_date for m in todos} == {None}
    assert {m.note for m in todos} == {None}


def test_as_fases_e_os_marcos_vem_na_ordem_do_catalogo(world):
    cronograma = ler(world)
    codigos = [c[0] for c in MARCOS]
    assert [m.id for f in cronograma.phases for m in f.milestones] == [marco_id(c) for c in codigos]


def test_com_todas_as_categorias_em_discussao_os_marcos_ligados_aguardam_a_classificacao(
    world,
):  # F-CRN-02
    cronograma = ler(world)
    for codigo, _f, _t, categoria, _d, _j in MARCOS:
        item = marco(cronograma, codigo)
        if categoria:
            assert item.state is MilestoneState.BLOCKED, codigo
            assert item.blocked_by[0].kind is BlockerKind.CATEGORY_UNCLASSIFIED, codigo
            assert item.blocked_by[0].label == CATEGORY_UNCLASSIFIED_LABEL, codigo
            assert item.blocked_by[0].milestone_id is None
    assert CATEGORY_UNCLASSIFIED_LABEL == "Aguardando classificar a categoria no Mapa de Escopo"


def test_classificadas_as_categorias_o_c06_c12_e_c13_aguardam_a_data_e_c07_a_c11_o_espaco(
    world,
):  # F-CRN-02
    world.classify_all(ENTRA)
    cronograma = ler(world)
    for codigo in ("C06", "C12", "C13"):
        assert rotulos(marco(cronograma, codigo)) == ["Definir a data (ou janela de datas)"], codigo
    for codigo in ("C07", "C08", "C09", "C10", "C11"):
        assert rotulos(marco(cronograma, codigo)) == ["Fechar o Espaço"], codigo


def test_concluir_o_c06_destrava_os_marcos_que_dependem_dele_sem_digitar_nada(world):  # F-CRN-03
    world.classify_all(ENTRA)
    concluir(world, "C01", "C02", "C03", "C04", "C05", "C06")
    cronograma = ler(world)
    for codigo in ("C07", "C08", "C09", "C10", "C11", "C14", "C15", "C21", "C24", "C20"):
        assert marco(cronograma, codigo).state is MilestoneState.UNLOCKED, codigo


def test_o_c20_so_destrava_com_o_c02_tambem_concluido(world):  # F-CRN-03
    world.classify_all(ENTRA)
    concluir(world, "C01", "C03", "C04", "C05", ignorar=True)
    concluir(world, "C06")
    antes = marco(ler(world), "C20")
    assert antes.state is MilestoneState.BLOCKED
    assert rotulos(antes) == ["Montar a lista preliminar de convidados"]
    concluir(world, "C02")
    assert marco(ler(world), "C20").state is MilestoneState.UNLOCKED


def test_concluir_o_c06_com_categoria_em_discussao_nao_destrava_quem_aguarda_a_categoria(world):
    concluir(world, "C01", "C02", "C03", "C04", "C05", "C06", ignorar=True)
    item = marco(ler(world), "C07")
    assert item.state is MilestoneState.BLOCKED
    assert rotulos(item) == [CATEGORY_UNCLASSIFIED_LABEL]


def test_fotografia_fica_de_fora_arquiva_o_c08(world):  # F-CRN-04
    world.classify_all(ENTRA)
    world.classify("Fotografia", Standing.OUT)
    item = marco(ler(world), "C08")
    assert item.archived is True
    assert item.optional is False


def test_marco_arquivado_nao_bloqueia_quem_dependia_dele(world):  # F-CRN-04
    world.classify_all(ENTRA)
    concluir(world, "C01", "C02", "C03", "C04", "C05", "C06")
    assert rotulos(marco(ler(world), "C16")) == ["Fechar o Buffet"]
    world.classify("Buffet", Standing.OUT)
    cronograma = ler(world)
    assert marco(cronograma, "C07").archived is True
    for dependente in ("C16", "C17"):
        assert marco(cronograma, dependente).state is MilestoneState.UNLOCKED, dependente


def test_musica_talvez_mostra_o_c11_opcional_e_nao_afeta_o_c29(world):  # F-CRN-04
    world.classify_all(ENTRA)
    antes = marco(ler(world), "C29")
    world.classify("Música (DJ, banda)", Standing.MAYBE)
    cronograma = ler(world)
    assert marco(cronograma, "C11").optional is True
    assert marco(cronograma, "C11").archived is False
    assert marco(cronograma, "C29").blocked_by == antes.blocked_by
    assert [b.label for b in marco(cronograma, "C29").blocked_by] == [
        "Fechar o Cerimonial do dia",
        "Confirmar as presenças",
    ]


def test_reabrir_a_fotografia_restaura_o_c08_no_estado_em_que_estava(world):  # F-CRN-04, regra 1
    world.classify_all(ENTRA)
    marcar(world, "C08", ManualState.IN_PROGRESS, ignorar=True)
    world.classify("Fotografia", Standing.OUT)
    arquivado = marco(ler(world), "C08")
    assert (arquivado.archived, arquivado.state) == (True, MilestoneState.IN_PROGRESS)
    world.classify("Fotografia", ENTRA)
    restaurado = marco(ler(world), "C08")
    assert (restaurado.archived, restaurado.state) == (False, MilestoneState.IN_PROGRESS)


def test_categoria_excluida_do_mapa_arquiva_o_marco_e_nao_tem_nome(world):
    world.classify_all(ENTRA)
    del world.categories[categoria_id("Fotografia")]
    item = marco(ler(world), "C08")
    assert item.archived is True
    assert item.category is not None
    assert item.category.id == categoria_id("Fotografia")
    assert item.category.name is None


def test_o_marco_traz_a_categoria_ligada_com_o_nome_de_hoje(world):
    world.categories[categoria_id("Espaço")] = CategoryInfo("Espaço renomeado", ENTRA)
    categoria = marco(ler(world), "C06").category
    assert categoria is not None
    assert categoria.name == "Espaço renomeado"
    assert marco(ler(world), "C01").category is None


def test_marcar_concluido_um_marco_bloqueado_sem_ignorar_e_recusado(world):  # F-CRN-03, regra 4
    antes = ler(world)
    with pytest.raises(MilestoneBlocked):
        marcar(world, "C03", ManualState.DONE)
    assert ler(world) == antes
    assert world.store.changes == []


def test_marcar_em_andamento_um_marco_bloqueado_tambem_exige_ignorar(world):
    with pytest.raises(MilestoneBlocked):
        marcar(world, "C03", ManualState.IN_PROGRESS)


def test_ignorando_o_bloqueio_passa_e_o_historico_registra(world):  # F-CRN-03, regra 4
    cronograma = marcar(world, "C03", ManualState.DONE, ignorar=True, ator=NOIVA)
    assert marco(cronograma, "C03").state is MilestoneState.DONE
    [mudanca] = world.store.changes
    assert mudanca.milestone_id == marco_id("C03")
    assert (mudanca.state_before, mudanca.state_after) == (None, ManualState.DONE)
    assert mudanca.ignored_block is True
    assert mudanca.profile is ProfileKind.NOIVA


def test_ignorar_um_bloqueio_que_nao_existe_nao_registra_que_ignorou(world):
    marcar(world, "C01", ManualState.DONE, ignorar=True)
    [mudanca] = world.store.changes
    assert mudanca.ignored_block is False


def test_so_a_mudanca_real_vai_para_o_historico_com_o_antes_e_o_depois(world):
    marcar(world, "C01", ManualState.IN_PROGRESS)
    marcar(world, "C01", ManualState.IN_PROGRESS)
    marcar(world, "C01", ManualState.DONE, ator=NOIVA)
    marcar(world, "C01", None)
    marcar(world, "C01", None)
    assert [(c.state_before, c.state_after, c.profile) for c in world.store.changes] == [
        (None, ManualState.IN_PROGRESS, ProfileKind.NOIVO),
        (ManualState.IN_PROGRESS, ManualState.DONE, ProfileKind.NOIVA),
        (ManualState.DONE, None, ProfileKind.NOIVO),
    ]
    assert all(c.id and c.profile is not ProfileKind.AMBOS for c in world.store.changes)


def test_reabrir_nunca_exige_ignorar_e_volta_ao_estado_derivado(world):  # F-CRN-03, regra 5
    marcar(world, "C03", ManualState.DONE, ignorar=True)
    reaberto = marcar(world, "C03", None)
    assert marco(reaberto, "C03").state is MilestoneState.BLOCKED
    [_, volta] = world.store.changes
    assert (volta.state_before, volta.state_after, volta.ignored_block) == (
        ManualState.DONE,
        None,
        False,
    )


def test_reabrir_o_c06_bloqueia_os_nao_concluidos_e_avisa_os_concluidos_sem_altera_los(
    world,
):  # F-CRN-03, regra 5
    world.classify_all(ENTRA)
    concluir(world, "C01", "C02", "C03", "C04", "C05", "C06", "C07")
    assert marco(ler(world), "C08").state is MilestoneState.UNLOCKED
    marcar(world, "C06", None)
    cronograma = ler(world)
    assert marco(cronograma, "C08").state is MilestoneState.BLOCKED
    assert rotulos(marco(cronograma, "C08")) == ["Fechar o Espaço"]
    concluido = marco(cronograma, "C07")
    assert concluido.state is MilestoneState.DONE
    assert [(w.kind, w.milestone_id, w.title) for w in concluido.warnings] == [
        (WarningKind.DEPENDS_ON_UNRESOLVED, marco_id("C06"), "Fechar o Espaço")
    ]
    assert concluido.version == marco(cronograma, "C07").version
    assert marco(cronograma, "C08").warnings == ()


def test_reabrir_nao_altera_a_version_de_quem_depende(world):
    world.classify_all(ENTRA)
    concluir(world, "C01", "C02", "C03", "C04", "C05", "C06", "C07")
    antes = marco(ler(world), "C07").version
    marcar(world, "C06", None)
    assert marco(ler(world), "C07").version == antes


def test_marco_com_prazo_ontem_e_destravado_aparece_atrasado_e_ao_concluir_o_sinal_some(
    world,
):  # F-CRN-03
    hoje = date(2026, 10, 27)
    editar(world, "C01", prazo=hoje - timedelta(days=1))
    item = marco(ler(world), "C01")
    assert (item.state, item.overdue) == (MilestoneState.UNLOCKED, True)
    marcar(world, "C01", ManualState.DONE)
    assert marco(ler(world), "C01").overdue is False


def test_prazo_hoje_nao_atrasa_e_o_dia_e_o_de_brasilia(world, clock):
    editar(world, "C01", prazo=date(2026, 10, 27))
    # 01:00 UTC de 28/10 ainda é 22:00 de 27/10 em Brasília.
    clock._now = datetime(2026, 10, 28, 1, 0, tzinfo=UTC)
    assert marco(ler(world), "C01").overdue is False
    clock._now = datetime(2026, 10, 28, 3, 0, tzinfo=UTC)
    assert marco(ler(world), "C01").overdue is True


def test_sem_prazo_manual_nao_ha_atraso(world):
    assert not any(m.overdue for f in ler(world).phases for m in f.milestones)


def test_cada_marco_diz_de_quem_depende_e_o_que_libera(world):  # F-CRN-09
    cronograma = ler(world)
    c06 = marco(cronograma, "C06")
    assert [(d.id, d.title, d.resolved) for d in c06.depends_on] == [
        (marco_id("C05"), "Definir a data (ou janela de datas)", False)
    ]
    assert [u.id for u in c06.unlocks] == [
        marco_id(c) for c in ("C07", "C08", "C09", "C10", "C11", "C14", "C15", "C20", "C21", "C24")
    ]


def test_progresso_por_fase_conta_opcionais_e_tira_os_arquivados(world):
    world.classify_all(ENTRA)
    world.classify("Fotografia", Standing.OUT)
    world.classify("Vídeo", Standing.MAYBE)
    concluir(world, "C01", "C02", "C03", "C04", "C05", "C06", "C07", "C09")
    fases = {f.title: f.progress for f in ler(world).phases}
    assert (fases["Marco Zero"].done, fases["Marco Zero"].total) == (4, 4)
    assert (fases["Contrato Âncora"].done, fases["Contrato Âncora"].total) == (2, 2)
    # Fornecedores: 7 marcos, menos o arquivado (C08) = 6; concluídos C07 e o opcional C09.
    assert (fases["Fornecedores Essenciais"].done, fases["Fornecedores Essenciais"].total) == (2, 6)


def test_so_a_data_definida_e_exata_liga_o_modo_com_data(world):
    assert ler(world).has_exact_date is False
    world.wedding_date = WeddingDate(defined=False, exact=date(2027, 6, 12))
    assert ler(world).has_exact_date is False
    world.wedding_date = WeddingDate(defined=True, exact=None)
    assert ler(world).has_exact_date is False
    world.wedding_date = WeddingDate(defined=True, exact=date(2027, 6, 12))
    assert ler(world).has_exact_date is True


def test_editar_troca_responsavel_nota_e_prazo_e_devolve_o_cronograma_inteiro(world):  # F-CRN-01
    cronograma = editar(
        world,
        "C06",
        responsavel=ProfileKind.NOIVA,
        nota="  Visitar dois espaços  ",
        prazo=date(2027, 1, 15),
    )
    item = marco(cronograma, "C06")
    assert (item.responsible, item.note, item.target_date) == (
        ProfileKind.NOIVA,
        "Visitar dois espaços",
        date(2027, 1, 15),
    )
    assert item.version == 2
    assert len(cronograma.phases) == 5


def test_editar_igual_nao_sobe_a_version(world):
    editar(world, "C06", responsavel=ProfileKind.NOIVO)
    versao = marco(ler(world), "C06").version
    editar(world, "C06", responsavel=ProfileKind.NOIVO)
    assert marco(ler(world), "C06").version == versao


def test_editar_com_version_velha_e_conflito(world):
    editar(world, "C06", responsavel=ProfileKind.NOIVO)
    with pytest.raises(VersionConflict):
        editar(world, "C06", responsavel=ProfileKind.NOIVA, versao=1)


def test_mudar_estado_com_version_velha_e_conflito(world):
    marcar(world, "C01", ManualState.IN_PROGRESS)
    with pytest.raises(VersionConflict):
        marcar(world, "C01", ManualState.DONE, versao=1)


def test_a_version_e_por_marco(world):
    editar(world, "C01", responsavel=ProfileKind.NOIVO)
    assert marco(ler(world), "C02").version == 1
    editar(world, "C02", responsavel=ProfileKind.NOIVA, versao=1)


def test_nota_longa_demais_e_recusada(world):
    with pytest.raises(InvalidScheduleValue):
        editar(world, "C01", nota="x" * 501)


def test_marco_inexistente_e_nao_encontrado(world):
    desconhecido = UUID(int=424242)
    with pytest.raises(NotFound):
        world.use_cases().update_milestone.execute(
            UpdateMilestoneCommand(desconhecido, ProfileKind.AMBOS, None, None, 1), NOIVO
        )
    with pytest.raises(NotFound):
        world.use_cases().change_milestone_state.execute(
            ChangeMilestoneStateCommand(desconhecido, ManualState.DONE, False, 1), NOIVO
        )


def test_o_ator_da_sessao_chega_a_unidade_de_trabalho(world):
    ler(world, NOIVA)
    editar(world, "C01", ator=NOIVO)
    assert world.actors == [NOIVA, NOIVO, NOIVO]


def test_concluido_para_em_andamento_com_predecessor_pendente_exige_ignorar(world):  # F-CRN-03
    marcar(world, "C03", ManualState.DONE, ignorar=True)
    with pytest.raises(MilestoneBlocked):
        marcar(world, "C03", ManualState.IN_PROGRESS)
    assert marco(ler(world), "C03").state is MilestoneState.DONE
    assert len(world.store.changes) == 1


def test_concluido_para_em_andamento_ignorando_registra_que_ignorou(world):
    marcar(world, "C03", ManualState.DONE, ignorar=True)
    marcar(world, "C03", ManualState.IN_PROGRESS, ignorar=True)
    ultima = world.store.changes[-1]
    assert (ultima.state_before, ultima.state_after, ultima.ignored_block) == (
        ManualState.DONE,
        ManualState.IN_PROGRESS,
        True,
    )


def test_o_c06_nao_libera_a_fotografia_que_ficou_de_fora(world):  # F-CRN-04
    world.classify_all(ENTRA)
    world.classify("Fotografia", Standing.OUT)
    liberados = [u.id for u in marco(ler(world), "C06").unlocks]
    assert marco_id("C08") not in liberados
    assert marco_id("C07") in liberados
