from datetime import date, timedelta
from uuid import UUID

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

HOJE = date(2026, 10, 27)


def marco(numero, *, depende=(), manual=None, standing=None, prazo=None):
    return MilestoneFacts(
        id=UUID(int=numero),
        manual_state=manual,
        standing=standing,
        target_date=prazo,
        depends_on=tuple(UUID(int=n) for n in depende),
    )


def derivar(*marcos, hoje=HOJE):
    return derive(marcos, hoje)


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
