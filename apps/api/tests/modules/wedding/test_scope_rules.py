from hypothesis import given
from hypothesis import strategies as st

from wedding.modules.wedding.domain.scope_rules import (
    AlignmentState,
    CategoryFacts,
    alignment,
    is_visible,
    last_discard_reason,
    progress,
    totals,
)
from wedding.modules.wedding.domain.scope_values import Priority, ScopeStatus
from wedding.shared_kernel.profile import ProfileKind

PRIORIDADES = st.one_of(st.none(), st.sampled_from(list(Priority)))
FATOS = st.builds(
    CategoryFacts,
    status=st.sampled_from(list(ScopeStatus)),
    estimate_cents=st.one_of(st.none(), st.integers(min_value=1, max_value=10**9)),
    visible=st.booleans(),
)


def test_iguais_alinham_e_diferentes_divergem():  # F-PLN-04
    assert alignment(Priority.IF_FITS, Priority.IF_FITS).state is AlignmentState.ALIGNED
    assert alignment(Priority.IF_FITS, Priority.DISPENSE).state is AlignmentState.DIVERGENT


def test_falta_diz_quem_falta():
    assert alignment(None, Priority.IF_FITS).missing == (ProfileKind.NOIVO,)
    assert alignment(Priority.IF_FITS, None).missing == (ProfileKind.NOIVA,)
    assert alignment(None, None).missing == (ProfileKind.NOIVO, ProfileKind.NOIVA)
    assert alignment(None, None).state is AlignmentState.MISSING


@given(PRIORIDADES, PRIORIDADES)
def test_alinhamento_e_simetrico_e_so_depende_de_igualdade_e_de_falta(a, b):
    resultado = alignment(a, b)
    assert resultado.state is alignment(b, a).state
    if a is None or b is None:
        assert resultado.state is AlignmentState.MISSING
        assert len(resultado.missing) == (a is None) + (b is None)
    else:
        assert resultado.missing == ()
        assert (resultado.state is AlignmentState.ALIGNED) == (a is b)


def test_visivel_so_se_nada_esconde_nem_exclui():
    assert is_visible(category_hidden=False, group_hidden=False, deleted=False)
    assert not is_visible(category_hidden=True, group_hidden=False, deleted=False)
    assert not is_visible(category_hidden=False, group_hidden=True, deleted=False)
    assert not is_visible(category_hidden=False, group_hidden=False, deleted=True)


def test_progresso_conta_so_as_visiveis_e_classificada_e_nao_estar_em_discussao():  # F-PLN-08
    fatos = [
        CategoryFacts(ScopeStatus.ESSENTIAL, None, True),
        CategoryFacts(ScopeStatus.IN_DISCUSSION, None, True),
        CategoryFacts(ScopeStatus.OUT, None, True),
        CategoryFacts(ScopeStatus.ESSENTIAL, None, False),
    ]
    assert (progress(fatos).classified, progress(fatos).total) == (2, 3)


@given(st.lists(FATOS))
def test_progresso_nunca_passa_do_total_e_bate_com_a_conta_direta(fatos):
    resultado = progress(fatos)
    visiveis = [f for f in fatos if f.visible]
    assert resultado.total == len(visiveis)
    assert resultado.classified == sum(f.status is not ScopeStatus.IN_DISCUSSION for f in visiveis)
    assert resultado.classified <= resultado.total


def test_totais_somam_entra_e_talvez_separados_e_contam_quem_nao_tem_estimativa():  # F-PLN-05
    fatos = [
        CategoryFacts(ScopeStatus.ESSENTIAL, 100, True),
        CategoryFacts(ScopeStatus.ESSENTIAL, None, True),
        CategoryFacts(ScopeStatus.MAYBE, 50, True),
        CategoryFacts(ScopeStatus.OUT, 999, True),
        CategoryFacts(ScopeStatus.IN_DISCUSSION, 999, True),
        CategoryFacts(ScopeStatus.ESSENTIAL, 999, False),
    ]
    assert totals(fatos) == totals(list(reversed(fatos)))
    resultado = totals(fatos)
    assert (resultado.essential_cents, resultado.essential_without_estimate) == (100, 1)
    assert (resultado.maybe_cents, resultado.maybe_without_estimate) == (50, 0)


@given(st.lists(FATOS), st.randoms())
def test_totais_nao_dependem_da_ordem_e_batem_com_a_conta_direta(fatos, aleatorio):
    embaralhado = list(fatos)
    aleatorio.shuffle(embaralhado)
    assert totals(fatos) == totals(embaralhado)
    resultado = totals(fatos)
    entra = [f for f in fatos if f.visible and f.status is ScopeStatus.ESSENTIAL]
    assert resultado.essential_cents == sum(f.estimate_cents or 0 for f in entra)
    assert resultado.essential_without_estimate == sum(f.estimate_cents is None for f in entra)


def test_motivo_do_descarte_anterior_e_o_da_ultima_mudanca_para_fica_de_fora():  # F-PLN-03, regra 3
    historico = [
        (ScopeStatus.OUT, "primeiro motivo"),
        (ScopeStatus.IN_DISCUSSION, None),
        (ScopeStatus.OUT, "segundo motivo"),
        (ScopeStatus.ESSENTIAL, None),
    ]
    assert last_discard_reason(historico) == "segundo motivo"
    assert last_discard_reason([(ScopeStatus.ESSENTIAL, None)]) is None
    assert last_discard_reason([]) is None
