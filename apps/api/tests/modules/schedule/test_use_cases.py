from datetime import UTC, date, datetime, timedelta
from uuid import UUID

import pytest
from tests.modules.schedule.catalog import MARCOS, categoria_id, marco_id
from tests.modules.schedule.conftest import NOIVA, NOIVO

from wedding.modules.schedule.application.commands.change_milestone_state import (
    ChangeMilestoneStateCommand,
)
from wedding.modules.schedule.application.commands.delete_milestone import DeleteMilestoneCommand
from wedding.modules.schedule.application.commands.update_milestone import UpdateMilestoneCommand
from wedding.modules.schedule.application.commands.update_milestone_window import (
    UpdateMilestoneWindowCommand,
)
from wedding.modules.schedule.application.dto import (
    CATEGORY_UNCLASSIFIED_LABEL,
    DateChangeDto,
    DateMode,
    DateRangeDto,
    MilestoneWindowDto,
    ScheduleDto,
    WarningKind,
)
from wedding.modules.schedule.application.ports import CategoryInfo, WeddingDate
from wedding.modules.schedule.application.queries.preview_date_change import (
    PreviewDateChangeCommand,
)
from wedding.modules.schedule.domain.errors import (
    InvalidMilestoneWindow,
    InvalidScheduleValue,
    MilestoneBlocked,
)
from wedding.modules.schedule.domain.values import (
    BlockerKind,
    ManualState,
    MilestoneState,
    Standing,
)
from wedding.modules.schedule.domain.windows import WindowUnit, window_dates
from wedding.shared_kernel.errors import DomainRuleViolated, NotFound, VersionConflict
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
    cronograma = ler(world)
    item = marco(cronograma, codigo)
    fase = next(f for f in cronograma.phases if item in f.milestones)
    atual = versao if versao is not None else item.version
    categoria = item.category.id if item.category else None
    return world.use_cases().update_milestone.execute(
        UpdateMilestoneCommand(
            marco_id(codigo), item.title, fase.id, responsavel, categoria, nota, prazo, atual
        ),
        ator,
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
    world.categories[categoria_id("Espaço")] = CategoryInfo("Espaço renomeado", ENTRA, True)
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


def test_sem_data_e_sem_prazo_manual_nao_ha_atraso_nem_prazo_efetivo(world):  # F-CRN-05
    todos = [m for f in ler(world).phases for m in f.milestones]
    assert not any(m.overdue for m in todos)
    assert {m.effective_target for m in todos} == {None}


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
            UpdateMilestoneCommand(
                desconhecido, "Marco Exemplo", UUID(int=1), ProfileKind.AMBOS, None, None, None, 1
            ),
            NOIVO,
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


# --- Janelas, prazo efetivo e Modos Sem/Com Data (F-CRN-02 e F-CRN-05) -------------------------

DATA_DO_CASAMENTO = date(2027, 6, 12)  # a data fictícia de aceite de F-CRN-05


def definir_janela(
    world, codigo, inicio, fim, unidade=WindowUnit.MONTHS, *, versao=None, ator=NOIVO
):
    atual = versao if versao is not None else marco(ler(world), codigo).version
    return world.use_cases().update_milestone_window.execute(
        UpdateMilestoneWindowCommand(marco_id(codigo), inicio, fim, unidade, atual), ator
    )


def prever(world, exact=None, ator=NOIVO):
    return world.use_cases().preview_date_change.execute(PreviewDateChangeCommand(exact), ator)


def test_a_janela_sugerida_chega_em_deslocamentos_e_e_marcada_como_sugestao(world):  # F-CRN-02
    cronograma = ler(world)
    assert marco(cronograma, "C06").window == MilestoneWindowDto(
        14, 10, WindowUnit.MONTHS, is_suggestion=True
    )
    assert marco(cronograma, "C28").window == MilestoneWindowDto(
        4, 1, WindowUnit.WEEKS, is_suggestion=True
    )
    for codigo in ("C01", "C02", "C03", "C04", "C05"):
        assert marco(cronograma, codigo).window is None


def test_sem_data_a_janela_vem_em_deslocamentos_mas_nenhuma_data_e_calculada(world):  # F-CRN-05
    item = marco(ler(world), "C06")
    assert item.window is not None
    assert (item.window_start, item.window_end, item.effective_target) == (None, None, None)
    assert (item.target_date, item.days_left, item.overdue) == (None, None, False)


def test_com_data_fechar_o_espaco_tem_janela_e_prazo_efetivo_sem_prazo_manual(world):  # F-CRN-05
    world.set_wedding_date(DATA_DO_CASAMENTO)
    item = marco(ler(world), "C06")
    assert (item.window_start, item.window_end) == (date(2026, 4, 12), date(2026, 8, 12))
    assert item.effective_target == date(2026, 8, 12)
    assert item.target_date is None  # o prazo manual continua sendo só o digitado


def test_prazo_manual_vira_o_efetivo_e_limpar_devolve_o_fim_da_janela(world):  # F-CRN-05
    world.set_wedding_date(DATA_DO_CASAMENTO)
    editar(world, "C06", prazo=date(2026, 7, 30))
    item = marco(ler(world), "C06")
    assert (item.target_date, item.effective_target) == (
        date(2026, 7, 30),
        date(2026, 8, 12) and date(2026, 7, 30),
    )
    assert item.window_end == date(2026, 8, 12)
    editar(world, "C06", prazo=None)
    voltou = marco(ler(world), "C06")
    assert (voltou.target_date, voltou.effective_target) == (None, date(2026, 8, 12))


def test_sem_data_o_prazo_manual_segue_com_a_contagem_regressiva(world, clock):  # F-CRN-05
    clock._now = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)
    editar(world, "C06", prazo=date(2026, 11, 6))
    item = marco(ler(world), "C06")
    assert (item.window_start, item.window_end) == (None, None)
    assert (item.effective_target, item.days_left) == (date(2026, 11, 6), 10)


def test_a_contagem_regressiva_usa_o_dia_de_brasilia(world, clock):  # F-CRN-05, D-031
    editar(world, "C01", prazo=date(2026, 10, 27))
    # 02:00 UTC de 27/10 ainda é 23:00 de 26/10 em Brasília: falta 1 dia, não 0.
    clock._now = datetime(2026, 10, 27, 2, 0, tzinfo=UTC)
    assert marco(ler(world), "C01").days_left == 1
    clock._now = datetime(2026, 10, 27, 3, 0, tzinfo=UTC)
    assert marco(ler(world), "C01").days_left == 0
    clock._now = datetime(2026, 10, 28, 3, 0, tzinfo=UTC)
    assert marco(ler(world), "C01").days_left == -1


def test_o_fim_da_janela_vencido_atrasa_o_marco_e_concluir_apaga_o_sinal(world):  # F-CRN-03
    world.classify_all(ENTRA)
    world.set_wedding_date(DATA_DO_CASAMENTO)  # o fim de C06 foi em 12/08/2026; hoje é 27/10/2026
    item = marco(ler(world), "C06")
    assert (item.overdue, item.days_left) == (True, -76)
    marcar(world, "C06", ManualState.DONE, ignorar=True)
    concluido = marco(ler(world), "C06")
    assert (concluido.overdue, concluido.days_left) == (False, None)
    assert concluido.window_end == date(2026, 8, 12)


def test_marco_arquivado_nao_tem_contagem_nem_atraso_mas_tem_as_datas(world):  # F-CRN-04
    world.classify_all(ENTRA)
    world.classify("Espaço", Standing.OUT)
    world.set_wedding_date(DATA_DO_CASAMENTO)
    item = marco(ler(world), "C06")
    assert (item.archived, item.overdue, item.days_left) == (True, False, None)
    assert item.effective_target == date(2026, 8, 12)


def test_voltar_ao_modo_sem_data_apaga_as_datas_calculadas_e_mantem_o_prazo_manual(world):
    world.set_wedding_date(DATA_DO_CASAMENTO)  # F-CRN-05, regra 6
    editar(world, "C06", prazo=date(2026, 7, 30))
    world.set_wedding_date(DATA_DO_CASAMENTO, defined=False)
    item = marco(ler(world), "C06")
    assert (item.window_start, item.window_end) == (None, None)
    assert (item.target_date, item.effective_target) == (date(2026, 7, 30), date(2026, 7, 30))


def test_editar_a_janela_troca_os_deslocamentos_e_deixa_de_ser_sugestao(world):  # F-CRN-05, regra 5
    cronograma = definir_janela(world, "C06", 12, 8, WindowUnit.WEEKS)
    item = marco(cronograma, "C06")
    assert item.window == MilestoneWindowDto(12, 8, WindowUnit.WEEKS, is_suggestion=False)
    assert item.version == 2
    assert len(cronograma.phases) == 5


def test_editar_a_janela_recalcula_as_datas_e_o_prazo_efetivo_com_data(world):
    world.set_wedding_date(DATA_DO_CASAMENTO)
    item = marco(definir_janela(world, "C06", 12, 8), "C06")
    assert (item.window_start, item.window_end) == (date(2026, 6, 12), date(2026, 10, 12))
    assert item.effective_target == date(2026, 10, 12)


def test_confirmar_a_janela_sugerida_com_os_mesmos_valores_ja_conta_como_edicao(world):
    item = marco(definir_janela(world, "C06", 14, 10), "C06")
    assert item.window == MilestoneWindowDto(14, 10, WindowUnit.MONTHS, is_suggestion=False)
    assert item.version == 2


def test_repetir_a_janela_ja_editada_nao_sobe_a_version(world):
    definir_janela(world, "C06", 12, 8)
    assert marco(definir_janela(world, "C06", 12, 8), "C06").version == 2


def test_dar_janela_a_marco_sem_janela_vale_e_nao_e_sugestao(world):  # C01 a C05 não têm janela
    item = marco(definir_janela(world, "C01", 3, 1), "C01")
    assert item.window == MilestoneWindowDto(3, 1, WindowUnit.MONTHS, is_suggestion=False)


def test_editar_a_janela_vale_sem_data_do_casamento_e_em_marco_arquivado(world):
    world.classify_all(ENTRA)
    world.classify("Espaço", Standing.OUT)
    item = marco(definir_janela(world, "C06", 12, 8), "C06")
    assert item.archived is True
    assert item.window is not None
    assert item.window.start_before == 12


def test_editar_a_janela_nunca_vira_prazo_manual(world):  # F-CRN-05, regra 2
    world.set_wedding_date(DATA_DO_CASAMENTO)
    item = marco(definir_janela(world, "C06", 12, 8), "C06")
    assert item.target_date is None
    editar(world, "C06", prazo=date(2026, 12, 1))
    assert marco(ler(world), "C06").window is not None


@pytest.mark.parametrize(
    ("inicio", "fim", "unidade"),
    [
        (3, 4, WindowUnit.MONTHS),
        (3, -1, WindowUnit.MONTHS),
        (121, 0, WindowUnit.MONTHS),
        (521, 0, WindowUnit.WEEKS),
    ],
)
def test_janela_invalida_e_recusada_sem_gravar(world, inicio, fim, unidade):
    with pytest.raises(InvalidMilestoneWindow):
        definir_janela(world, "C06", inicio, fim, unidade)
    assert marco(ler(world), "C06").version == 1


def test_editar_a_janela_com_version_velha_e_conflito(world):
    with pytest.raises(VersionConflict):
        definir_janela(world, "C06", 12, 8, versao=7)


def test_editar_a_janela_de_marco_inexistente_ou_excluido_e_nao_encontrado(world):
    with pytest.raises(NotFound):
        world.use_cases().update_milestone_window.execute(
            UpdateMilestoneWindowCommand(UUID(int=99), 12, 8, WindowUnit.MONTHS, 1), NOIVO
        )
    world.use_cases().delete_milestone.execute(DeleteMilestoneCommand(marco_id("C06"), 1), NOIVO)
    with pytest.raises(NotFound):
        definir_janela(world, "C06", 12, 8, versao=1)


def test_editar_a_janela_registra_o_autor_da_sessao(world):
    definir_janela(world, "C06", 12, 8, versao=1, ator=NOIVA)
    assert set(world.actors) == {NOIVA}


# --- A prévia de mudar a data do casamento (F-CRN-05, regra 4) ---------------------------------


def _janela(inicio, fim):
    return DateRangeDto(inicio, fim)


def test_previa_com_para_com_lista_os_marcos_que_mudam_de_janela_e_mantem_o_de_prazo_manual(world):
    world.set_wedding_date(DATA_DO_CASAMENTO)
    editar(world, "C07", prazo=date(2026, 12, 1))  # F-CRN-05: o de prazo manual não muda
    previa = prever(world, date(2027, 7, 12))
    assert (previa.mode_before, previa.mode_after) == (DateMode.WITH_DATE, DateMode.WITH_DATE)
    por_id = {c.id: c for c in previa.changes}
    assert marco_id("C06") in por_id
    assert por_id[marco_id("C06")] == DateChangeDto(
        marco_id("C06"),
        "Fechar o Espaço",
        _janela(date(2026, 4, 12), date(2026, 8, 12)),
        _janela(date(2026, 5, 12), date(2026, 9, 12)),
        date(2026, 8, 12),
        date(2026, 9, 12),
    )
    assert marco_id("C07") not in por_id
    assert marco_id("C01") not in por_id  # sem janela, nada a mudar
    assert len(previa.changes) == 23  # C06 a C29 (24 marcos com janela) sem o C07, de prazo manual
    assert previa.manual_kept == 1


def test_previa_sem_data_para_com_data_traz_janela_antes_nula(world):
    previa = prever(world, DATA_DO_CASAMENTO)
    assert (previa.mode_before, previa.mode_after) == (DateMode.NO_DATE, DateMode.WITH_DATE)
    c06 = next(c for c in previa.changes if c.id == marco_id("C06"))
    assert (c06.window_before, c06.target_before) == (None, None)
    assert c06.window_after == _janela(date(2026, 4, 12), date(2026, 8, 12))
    assert c06.target_after == date(2026, 8, 12)
    assert len(previa.changes) == 24


def test_previa_com_data_para_sem_data_traz_janela_depois_nula(world):
    world.set_wedding_date(DATA_DO_CASAMENTO)
    previa = prever(world, None)
    assert (previa.mode_before, previa.mode_after) == (DateMode.WITH_DATE, DateMode.NO_DATE)
    c06 = next(c for c in previa.changes if c.id == marco_id("C06"))
    assert c06.window_before == _janela(date(2026, 4, 12), date(2026, 8, 12))
    assert (c06.window_after, c06.target_after) == (None, None)
    assert c06.target_before == date(2026, 8, 12)
    assert len(previa.changes) == 24


def test_previa_da_mesma_data_ou_de_sem_data_para_sem_data_nao_muda_nada(world):
    assert prever(world, None).changes == ()
    world.set_wedding_date(DATA_DO_CASAMENTO)
    assert prever(world, DATA_DO_CASAMENTO).changes == ()
    assert prever(world, DATA_DO_CASAMENTO).newly_overdue == 0


def test_previa_conta_so_marcos_ativos_e_nao_concluidos(world):
    world.classify_all(ENTRA)
    world.classify("Fotografia", Standing.OUT)  # C08 arquivado
    concluir(world, "C01", "C02", "C03", "C04", "C05", "C06")  # C06 concluído
    previa = prever(world, DATA_DO_CASAMENTO)
    ids = {c.id for c in previa.changes}
    assert marco_id("C06") not in ids
    assert marco_id("C08") not in ids
    assert len(ids) == 24 - 2


def _fim_da_janela(codigo, data):
    janela = next(m[5] for m in MARCOS if m[0] == codigo)
    resultado = window_dates(data, janela[0], janela[1], WindowUnit(janela[2]))
    assert resultado is not None
    return resultado[1]


def test_previa_conta_os_marcos_que_passam_a_atrasado_com_a_data_hipotetica(world):
    # Hoje é 27/10/2026. O C10 (10 a 7 meses) acaba em 12/11/2026 com a data atual e em 12/10/2026
    # com a hipotética: passa a Atrasado. O C06 já estava atrasado nas duas e não conta.
    world.set_wedding_date(DATA_DO_CASAMENTO)
    hipotetica = date(2027, 5, 12)
    previa = prever(world, hipotetica)
    hoje = date(2026, 10, 27)
    assert _fim_da_janela("C10", DATA_DO_CASAMENTO) >= hoje > _fim_da_janela("C10", hipotetica)
    assert _fim_da_janela("C06", DATA_DO_CASAMENTO) < hoje
    esperados = {
        marco_id(m[0])
        for m in MARCOS
        if m[5]
        and _fim_da_janela(m[0], DATA_DO_CASAMENTO) >= hoje > _fim_da_janela(m[0], hipotetica)
    }
    assert marco_id("C10") in esperados
    assert previa.newly_overdue == len(esperados)


def test_sem_data_para_com_data_conta_como_novo_atraso_o_que_ja_vence_antes_de_hoje(world):
    previa = prever(world, DATA_DO_CASAMENTO)
    esperados = [
        m[0]
        for m in MARCOS
        if m[5] and _fim_da_janela(m[0], DATA_DO_CASAMENTO) < date(2026, 10, 27)
    ]
    assert marco_id("C06") in {marco_id(c) for c in esperados}
    assert previa.newly_overdue == len(esperados)


def test_o_prazo_manual_futuro_nao_vira_novo_atraso_embora_a_janela_dele_acompanhe_a_data(world):
    world.set_wedding_date(DATA_DO_CASAMENTO)
    editar(world, "C10", prazo=date(2027, 1, 1))
    hipotetica = date(2027, 5, 12)
    sem_manual = prever(world, hipotetica).newly_overdue
    assert marco_id("C10") not in {c.id for c in prever(world, hipotetica).changes}
    # Sem o prazo manual, o C10 entraria na conta: a diferença é exatamente ele.
    editar(world, "C10", prazo=None)
    assert prever(world, hipotetica).newly_overdue == sem_manual + 1


def test_quem_ja_esta_atrasado_com_a_data_atual_nao_conta_como_novo_atraso(world):
    world.set_wedding_date(DATA_DO_CASAMENTO)
    ja_atrasados = {m.id for f in ler(world).phases for m in f.milestones if m.overdue}
    assert marco_id("C06") in ja_atrasados
    previa = prever(world, date(2027, 6, 13))  # um dia depois: ninguém cruza o dia de hoje
    assert previa.newly_overdue == 0


def test_previa_nao_grava_nada(world):
    antes = (ler(world), len(world.actors))
    prever(world, DATA_DO_CASAMENTO)
    assert world.wedding_date.exact is None
    assert ler(world) == antes[0]
    assert {m.version for m in world.store.milestones.values()} == {1}


def test_previa_com_ano_fora_de_2000_a_2100_e_recusada(world):
    for fora in (date(1999, 12, 31), date(2101, 1, 1)):
        with pytest.raises(DomainRuleViolated) as erro:
            prever(world, fora)
        assert erro.value.code == "invalid_preview_date"


def test_previa_calcula_a_manual_mantida_so_de_marco_ativo_nao_concluido_com_janela(world):
    world.classify_all(ENTRA)
    world.classify("Fotografia", Standing.OUT)
    editar(world, "C07", prazo=date(2026, 12, 1))  # conta
    editar(world, "C08", prazo=date(2026, 12, 1))  # arquivado: fica fora
    editar(world, "C01", prazo=date(2026, 12, 1))  # sem janela: fica fora
    editar(world, "C09", prazo=date(2026, 12, 1))
    marcar(world, "C09", ManualState.DONE, ignorar=True)  # concluído: fica fora
    assert prever(world, DATA_DO_CASAMENTO).manual_kept == 1
