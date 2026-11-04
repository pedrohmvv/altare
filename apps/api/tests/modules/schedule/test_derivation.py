from datetime import date, timedelta
from uuid import UUID

import pytest
from hypothesis import given
from hypothesis import strategies as st

from wedding.modules.schedule.domain.derivation import (
    Blocker,
    DependencyStatus,
    MilestoneFacts,
    derive,
    phase_progress,
    waiting_on,
)
from wedding.modules.schedule.domain.values import (
    BlockerKind,
    ManualState,
    MilestoneState,
    Standing,
)
from wedding.modules.schedule.domain.windows import Window, WindowUnit

HOJE = date(2026, 10, 27)
DATA_DO_CASAMENTO = date(2027, 6, 12)  # a data fictícia de aceite de F-CRN-05
FECHAR_O_ESPACO = Window(14, 10, WindowUnit.MONTHS)


def marco(numero, *, depende=(), manual=None, standing=None, prazo=None, janela=None):
    return MilestoneFacts(
        id=UUID(int=numero),
        manual_state=manual,
        standing=standing,
        target_date=prazo,
        depends_on=tuple(UUID(int=n) for n in depende),
        window=janela,
    )


def derivar(*marcos, hoje=HOJE, data=None):
    return derive(marcos, hoje, data)


def id_(numero):
    return UUID(int=numero)


def test_marco_sem_dependencia_nem_categoria_esta_destravado():  # F-CRN-03
    derivado = derivar(marco(1))[id_(1)]
    assert derivado.state is MilestoneState.UNLOCKED
    assert derivado.blockers == ()
    assert (derivado.optional, derivado.archived, derivado.overdue) == (False, False, False)


def test_categoria_em_discussao_bloqueia_com_o_motivo_da_categoria():  # F-CRN-04
    derivado = derivar(marco(1, standing=Standing.IN_DISCUSSION))[id_(1)]
    assert derivado.state is MilestoneState.BLOCKED
    assert derivado.blockers == (Blocker(BlockerKind.CATEGORY_UNCLASSIFIED, None),)


def test_categoria_que_entra_nao_bloqueia():
    assert derivar(marco(1, standing=Standing.ENTERS))[id_(1)].state is MilestoneState.UNLOCKED


def test_dependencia_pendente_bloqueia_e_lista_o_marco_que_falta():  # F-CRN-03
    derivado = derivar(marco(1), marco(2, depende=(1,)))[id_(2)]
    assert derivado.state is MilestoneState.BLOCKED
    assert derivado.blockers == (Blocker(BlockerKind.MILESTONE, id_(1)),)
    assert derivado.dependencies == (DependencyStatus(id_(1), False),)


def test_dependencia_concluida_resolve():  # F-CRN-03, regra 1
    derivado = derivar(marco(1, manual=ManualState.DONE), marco(2, depende=(1,)))[id_(2)]
    assert derivado.state is MilestoneState.UNLOCKED
    assert derivado.dependencies == (DependencyStatus(id_(1), True),)


def test_dependencia_em_andamento_ainda_nao_resolve():
    derivado = derivar(marco(1, manual=ManualState.IN_PROGRESS), marco(2, depende=(1,)))[id_(2)]
    assert derivado.state is MilestoneState.BLOCKED


def test_dependencia_arquivada_resolve_sem_estar_concluida():  # F-CRN-04
    derivado = derivar(marco(1, standing=Standing.OUT), marco(2, depende=(1,)))[id_(2)]
    assert derivado.state is MilestoneState.UNLOCKED


def test_dependencia_opcional_resolve_sem_estar_concluida():  # F-CRN-04
    derivado = derivar(marco(1, standing=Standing.MAYBE), marco(2, depende=(1,)))[id_(2)]
    assert derivado.state is MilestoneState.UNLOCKED


def test_dependencia_em_discussao_nao_resolve():
    derivado = derivar(marco(1, standing=Standing.IN_DISCUSSION), marco(2, depende=(1,)))[id_(2)]
    assert derivado.state is MilestoneState.BLOCKED


def test_so_um_dos_predecessores_pendente_continua_bloqueando_e_lista_so_o_que_falta():
    derivado = derivar(marco(1, manual=ManualState.DONE), marco(2), marco(3, depende=(1, 2)))[
        id_(3)
    ]
    assert derivado.blockers == (Blocker(BlockerKind.MILESTONE, id_(2)),)


def test_categoria_e_dependencia_aparecem_juntas_com_a_categoria_primeiro():
    derivado = derivar(marco(1), marco(2, depende=(1,), standing=Standing.IN_DISCUSSION))[id_(2)]
    assert [b.kind for b in derivado.blockers] == [
        BlockerKind.CATEGORY_UNCLASSIFIED,
        BlockerKind.MILESTONE,
    ]


def test_estado_manual_vence_o_derivado_e_concluido_nao_tem_bloqueios():
    derivado = derivar(
        marco(1), marco(2, depende=(1,), manual=ManualState.DONE, standing=Standing.IN_DISCUSSION)
    )[id_(2)]
    assert derivado.state is MilestoneState.DONE
    assert derivado.blockers == ()


def test_em_andamento_guarda_o_estado_mas_continua_listando_o_que_falta():
    derivado = derivar(marco(1), marco(2, depende=(1,), manual=ManualState.IN_PROGRESS))[id_(2)]
    assert derivado.state is MilestoneState.IN_PROGRESS
    assert derivado.blockers == (Blocker(BlockerKind.MILESTONE, id_(1)),)


def test_opcional_e_arquivado_sao_etiquetas_que_nao_mudam_o_estado():  # F-CRN-04
    talvez = derivar(marco(1, standing=Standing.MAYBE))[id_(1)]
    fora = derivar(marco(1, standing=Standing.OUT))[id_(1)]
    assert (talvez.optional, talvez.archived, talvez.state) == (
        True,
        False,
        MilestoneState.UNLOCKED,
    )
    assert (fora.optional, fora.archived, fora.state) == (False, True, MilestoneState.UNLOCKED)


def test_arquivado_guarda_o_estado_manual_para_restaurar():  # F-CRN-04, regra 1
    fora = derivar(marco(1, standing=Standing.OUT, manual=ManualState.IN_PROGRESS))[id_(1)]
    voltou = derivar(marco(1, standing=Standing.ENTERS, manual=ManualState.IN_PROGRESS))[id_(1)]
    assert fora.state is voltou.state is MilestoneState.IN_PROGRESS


def test_libera_e_o_inverso_de_depende_de():  # F-CRN-09
    derivados = derivar(marco(1), marco(2, depende=(1,)), marco(3, depende=(1, 2)))
    assert derivados[id_(1)].unlocks == (id_(2), id_(3))
    assert derivados[id_(2)].unlocks == (id_(3),)
    assert derivados[id_(3)].unlocks == ()


def test_dependencia_de_marco_que_nao_existe_e_ignorada():
    derivado = derivar(marco(2, depende=(99,)))[id_(2)]
    assert derivado.state is MilestoneState.UNLOCKED
    assert derivado.dependencies == ()


def test_prazo_ontem_e_nao_concluido_esta_atrasado():  # F-CRN-03
    ontem = HOJE - timedelta(days=1)
    assert derivar(marco(1, prazo=ontem))[id_(1)].overdue is True


def test_prazo_hoje_ou_futuro_nao_esta_atrasado():
    assert derivar(marco(1, prazo=HOJE))[id_(1)].overdue is False
    assert derivar(marco(1, prazo=HOJE + timedelta(days=1)))[id_(1)].overdue is False


def test_sem_prazo_nao_ha_atraso():
    assert derivar(marco(1))[id_(1)].overdue is False


def test_concluir_apaga_o_atraso():  # F-CRN-03
    ontem = HOJE - timedelta(days=1)
    assert derivar(marco(1, prazo=ontem, manual=ManualState.DONE))[id_(1)].overdue is False


def test_bloqueado_e_em_andamento_com_prazo_vencido_tambem_atrasam():
    ontem = HOJE - timedelta(days=1)
    bloqueado = derivar(marco(1), marco(2, depende=(1,), prazo=ontem))[id_(2)]
    andamento = derivar(marco(1, prazo=ontem, manual=ManualState.IN_PROGRESS))[id_(1)]
    assert bloqueado.overdue is True
    assert andamento.overdue is True


def test_arquivado_nao_atrasa_porque_saiu_das_listas_ativas():
    ontem = HOJE - timedelta(days=1)
    assert derivar(marco(1, prazo=ontem, standing=Standing.OUT))[id_(1)].overdue is False


def test_concluido_com_predecessor_nao_resolvido_avisa_sem_mudar_o_estado():  # F-CRN-03, regra 5
    derivados = derivar(marco(1), marco(2, depende=(1,), manual=ManualState.DONE))
    assert derivados[id_(2)].state is MilestoneState.DONE
    assert derivados[id_(2)].unresolved == (id_(1),)


def test_concluido_com_predecessores_resolvidos_nao_avisa():
    derivados = derivar(
        marco(1, manual=ManualState.DONE),
        marco(2, standing=Standing.OUT),
        marco(3, depende=(1, 2), manual=ManualState.DONE),
    )
    assert derivados[id_(3)].unresolved == ()


def test_nao_concluido_nunca_tem_aviso_de_predecessor_nao_resolvido():
    assert derivar(marco(1), marco(2, depende=(1,)))[id_(2)].unresolved == ()


def test_reabrir_bloqueia_os_nao_concluidos_e_avisa_os_concluidos():  # F-CRN-03, regra 5
    cadeia = [
        marco(1, manual=ManualState.DONE),
        marco(2, depende=(1,)),
        marco(3, depende=(1,), manual=ManualState.DONE),
    ]
    antes = derive(cadeia, HOJE)
    assert antes[id_(2)].state is MilestoneState.UNLOCKED
    cadeia[0] = marco(1)  # reabriu
    depois = derive(cadeia, HOJE)
    assert depois[id_(2)].state is MilestoneState.BLOCKED
    assert depois[id_(3)].state is MilestoneState.DONE
    assert depois[id_(3)].unresolved == (id_(1),)


def test_progresso_conta_opcionais_e_tira_so_os_arquivados():
    derivados = derivar(
        marco(1, manual=ManualState.DONE),
        marco(2),
        marco(3, standing=Standing.MAYBE, manual=ManualState.DONE),
        marco(4, standing=Standing.MAYBE),
        marco(5, standing=Standing.OUT, manual=ManualState.DONE),
        marco(6, standing=Standing.OUT),
    )
    progresso = phase_progress(derivados.values())
    assert (progresso.done, progresso.total) == (2, 4)


def test_fase_vazia_tem_progresso_zero():
    assert phase_progress([]) == phase_progress(())
    assert phase_progress([]).total == 0


def test_concluido_ignorando_o_bloqueio_tambem_avisa_sem_nada_ter_sido_reaberto():
    # Nada foi reaberto: o C2 foi concluído com o C1 ainda pendente. O aviso diz a verdade.
    derivados = derivar(marco(1), marco(2, depende=(1,), manual=ManualState.DONE))
    assert derivados[id_(2)].unresolved == (id_(1),)


def test_libera_nao_lista_os_marcos_arquivados():  # F-CRN-04
    derivados = derivar(
        marco(1),
        marco(2, depende=(1,), standing=Standing.OUT),
        marco(3, depende=(1,), standing=Standing.MAYBE),
        marco(4, depende=(1,)),
    )
    assert derivados[id_(1)].unlocks == (id_(3), id_(4))


def test_o_que_aguarda_independe_da_marca_manual():  # F-CRN-03, regra 4
    fatos = [marco(1), marco(2, depende=(1,), manual=ManualState.DONE)]
    assert waiting_on(fatos, id_(2)) == (Blocker(BlockerKind.MILESTONE, id_(1)),)
    andamento = [marco(1), marco(2, depende=(1,), manual=ManualState.IN_PROGRESS)]
    assert waiting_on(andamento, id_(2)) == (Blocker(BlockerKind.MILESTONE, id_(1)),)


def test_o_que_aguarda_inclui_a_categoria_em_discussao_mesmo_concluido():
    fatos = [marco(1, standing=Standing.IN_DISCUSSION, manual=ManualState.DONE)]
    assert waiting_on(fatos, id_(1)) == (Blocker(BlockerKind.CATEGORY_UNCLASSIFIED, None),)


def test_nada_aguarda_quando_os_predecessores_estao_resolvidos():
    fatos = [
        marco(1, manual=ManualState.DONE),
        marco(2, standing=Standing.OUT),
        marco(3, depende=(1, 2), manual=ManualState.DONE),
    ]
    assert waiting_on(fatos, id_(3)) == ()


@st.composite
def cronogramas(draw):
    """Cronogramas pequenos e arbitrários: estado manual, categoria e dependências quaisquer
    (inclusive entre si e para marcos que não existem)."""
    total = draw(st.integers(min_value=1, max_value=8))
    marcos = []
    for numero in range(1, total + 1):
        marcos.append(
            marco(
                numero,
                depende=draw(st.lists(st.integers(1, total + 1), max_size=4, unique=True)),
                manual=draw(st.sampled_from([None, *ManualState])),
                standing=draw(st.sampled_from([None, *Standing])),
            )
        )
    return marcos


@given(cronogramas())
def test_os_bloqueios_da_derivacao_sao_o_que_aguarda_todo_marco_nao_concluido(marcos):
    derivados = derive(marcos, HOJE)
    for item in marcos:
        if item.manual_state is not ManualState.DONE:
            assert waiting_on(marcos, item.id) == derivados[item.id].blockers


# --- Modo Com Data e Sem Data (F-CRN-05) -------------------------------------------------------


def test_com_data_a_janela_e_o_prazo_efetivo_vem_da_data_do_casamento():  # F-CRN-05
    derivado = derivar(marco(1, janela=FECHAR_O_ESPACO), data=DATA_DO_CASAMENTO)[id_(1)]
    assert derivado.window_start == date(2026, 4, 12)
    assert derivado.window_end == date(2026, 8, 12)
    assert derivado.effective_target == date(2026, 8, 12)


def test_prazo_manual_prevalece_sobre_o_fim_da_janela_e_a_janela_continua_calculada():  # F-CRN-05
    derivado = derivar(
        marco(1, janela=FECHAR_O_ESPACO, prazo=date(2026, 7, 30)), data=DATA_DO_CASAMENTO
    )[id_(1)]
    assert derivado.effective_target == date(2026, 7, 30)
    assert (derivado.window_start, derivado.window_end) == (date(2026, 4, 12), date(2026, 8, 12))


def test_limpar_o_prazo_manual_devolve_o_fim_da_janela():  # F-CRN-05
    com_manual = marco(1, janela=FECHAR_O_ESPACO, prazo=date(2026, 7, 30))
    sem_manual = marco(1, janela=FECHAR_O_ESPACO)
    assert derivar(com_manual, data=DATA_DO_CASAMENTO)[id_(1)].effective_target == date(2026, 7, 30)
    assert derivar(sem_manual, data=DATA_DO_CASAMENTO)[id_(1)].effective_target == date(2026, 8, 12)


def test_sem_data_nada_e_calculado_mas_o_prazo_manual_segue_valendo():  # F-CRN-05
    hoje = date(2026, 7, 1)
    derivado = derivar(marco(1, janela=FECHAR_O_ESPACO, prazo=date(2026, 7, 30)), hoje=hoje)[id_(1)]
    assert (derivado.window_start, derivado.window_end) == (None, None)
    assert derivado.effective_target == date(2026, 7, 30)
    assert derivado.days_left == 29


def test_sem_data_e_sem_prazo_manual_nao_ha_prazo_efetivo_nem_contagem():
    derivado = derivar(marco(1, janela=FECHAR_O_ESPACO))[id_(1)]
    assert (derivado.effective_target, derivado.days_left, derivado.overdue) == (None, None, False)


def test_marco_sem_janela_com_data_nao_calcula_nada_e_so_tem_o_prazo_manual():
    sem_prazo = derivar(marco(1), data=DATA_DO_CASAMENTO)[id_(1)]
    assert (sem_prazo.window_start, sem_prazo.window_end) == (None, None)
    assert (sem_prazo.effective_target, sem_prazo.days_left) == (None, None)
    com_prazo = derivar(marco(1, prazo=date(2026, 12, 1)), data=DATA_DO_CASAMENTO)[id_(1)]
    assert com_prazo.effective_target == date(2026, 12, 1)


def test_dias_restantes_contam_do_dia_de_hoje_ao_prazo_efetivo():
    prazo = date(2026, 8, 12)
    marcos = marco(1, janela=FECHAR_O_ESPACO)
    assert derivar(marcos, hoje=date(2026, 8, 1), data=DATA_DO_CASAMENTO)[id_(1)].days_left == 11
    assert derivar(marcos, hoje=prazo, data=DATA_DO_CASAMENTO)[id_(1)].days_left == 0
    assert derivar(marcos, hoje=date(2026, 8, 13), data=DATA_DO_CASAMENTO)[id_(1)].days_left == -1


def test_fim_da_janela_vencido_e_nao_concluido_esta_atrasado_sem_prazo_manual():  # F-CRN-03
    marcos = marco(1, janela=FECHAR_O_ESPACO)
    atrasado = derivar(marcos, hoje=date(2026, 8, 13), data=DATA_DO_CASAMENTO)[id_(1)]
    no_dia = derivar(marcos, hoje=date(2026, 8, 12), data=DATA_DO_CASAMENTO)[id_(1)]
    assert (atrasado.overdue, no_dia.overdue) == (True, False)


def test_sem_data_a_janela_vencida_nao_atrasa_porque_nada_foi_calculado():
    assert derivar(marco(1, janela=FECHAR_O_ESPACO), hoje=date(2030, 1, 1))[id_(1)].overdue is False


def test_o_prazo_manual_futuro_prevalece_e_afasta_o_atraso_da_janela_vencida():
    marcos = marco(1, janela=FECHAR_O_ESPACO, prazo=date(2026, 12, 1))
    derivado = derivar(marcos, hoje=date(2026, 10, 27), data=DATA_DO_CASAMENTO)[id_(1)]
    assert derivado.overdue is False
    assert derivado.days_left == 35


def test_o_prazo_manual_vencido_atrasa_mesmo_com_o_fim_da_janela_no_futuro():
    marcos = marco(1, janela=FECHAR_O_ESPACO, prazo=date(2026, 6, 1))
    derivado = derivar(marcos, hoje=date(2026, 7, 1), data=DATA_DO_CASAMENTO)[id_(1)]
    assert derivado.overdue is True
    assert derivado.days_left == -30


@pytest.mark.parametrize("manual", [None, date(2026, 8, 1)])
def test_concluido_nao_tem_contagem_nem_atraso_mas_guarda_as_datas_calculadas(manual):
    marcos = marco(1, janela=FECHAR_O_ESPACO, prazo=manual, manual=ManualState.DONE)
    derivado = derivar(marcos, hoje=date(2027, 1, 1), data=DATA_DO_CASAMENTO)[id_(1)]
    assert (derivado.days_left, derivado.overdue) == (None, False)
    assert derivado.window_end == date(2026, 8, 12)
    assert derivado.effective_target == (manual or date(2026, 8, 12))


def test_arquivado_nao_tem_contagem_nem_atraso():  # F-CRN-04
    marcos = marco(1, janela=FECHAR_O_ESPACO, standing=Standing.OUT)
    derivado = derivar(marcos, hoje=date(2027, 1, 1), data=DATA_DO_CASAMENTO)[id_(1)]
    assert (derivado.days_left, derivado.overdue) == (None, False)


def test_data_do_casamento_fora_do_calendario_nao_calcula_a_janela_e_nao_quebra():
    marcos = marco(1, janela=FECHAR_O_ESPACO, prazo=date(2026, 7, 30))
    derivado = derivar(marcos, data=date(1, 1, 1))[id_(1)]
    assert (derivado.window_start, derivado.window_end) == (None, None)
    assert derivado.effective_target == date(2026, 7, 30)
    assert (
        derivar(marco(2, janela=FECHAR_O_ESPACO), data=date(1, 1, 1))[id_(2)].effective_target
        is None
    )
