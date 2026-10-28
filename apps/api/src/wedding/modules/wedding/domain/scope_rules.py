from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum

from wedding.modules.wedding.domain.scope_values import Priority, ScopeStatus
from wedding.shared_kernel.profile import ProfileKind


class AlignmentState(StrEnum):
    ALIGNED = "alinhados"
    DIVERGENT = "divergem"
    MISSING = "falta"


@dataclass(frozen=True)
class Alignment:
    state: AlignmentState
    missing: tuple[ProfileKind, ...] = ()


@dataclass(frozen=True)
class CategoryFacts:
    """O que o progresso e os totais precisam saber de uma categoria."""

    status: ScopeStatus
    estimate_cents: int | None
    visible: bool


@dataclass(frozen=True)
class Progress:
    classified: int
    total: int


@dataclass(frozen=True)
class Totals:
    essential_cents: int
    essential_without_estimate: int
    maybe_cents: int
    maybe_without_estimate: int


def alignment(noivo: Priority | None, noiva: Priority | None) -> Alignment:
    """Derivado, nunca editado (F-PLN-04): iguais alinham, diferentes divergem, e falta quem não
    avaliou."""
    missing = tuple(
        profile
        for profile, priority in ((ProfileKind.NOIVO, noivo), (ProfileKind.NOIVA, noiva))
        if priority is None
    )
    if missing:
        return Alignment(AlignmentState.MISSING, missing)
    state = AlignmentState.ALIGNED if noivo is noiva else AlignmentState.DIVERGENT
    return Alignment(state)


def is_visible(*, category_hidden: bool, group_hidden: bool, deleted: bool) -> bool:
    """Uma frente aparece nas telas se nem ela nem o grupo estão ocultos nem foi excluída."""
    return not (category_hidden or group_hidden or deleted)


def progress(facts: Iterable[CategoryFacts]) -> Progress:
    """ "N de M categorias classificadas": M exclui as ocultas e "classificada" é qualquer status
    diferente de `Em discussão` (F-PLN-08)."""
    visible = [fact for fact in facts if fact.visible]
    classified = sum(fact.status is not ScopeStatus.IN_DISCUSSION for fact in visible)
    return Progress(classified=classified, total=len(visible))


def totals(facts: Iterable[CategoryFacts]) -> Totals:
    """A soma das estimativas de `Entra` e, à parte, de `Talvez`. Estimativa vazia não conta como
    zero: entra na contagem de quem está sem estimativa (F-PLN-05)."""
    sums = {ScopeStatus.ESSENTIAL: [0, 0], ScopeStatus.MAYBE: [0, 0]}
    for fact in facts:
        if fact.visible and fact.status in sums:
            bucket = sums[fact.status]
            if fact.estimate_cents is None:
                bucket[1] += 1
            else:
                bucket[0] += fact.estimate_cents
    essential, maybe = sums[ScopeStatus.ESSENTIAL], sums[ScopeStatus.MAYBE]
    return Totals(essential[0], essential[1], maybe[0], maybe[1])


def last_discard_reason(changes: Iterable[tuple[ScopeStatus, str | None]]) -> str | None:
    """Das mudanças do mais antigo ao mais novo, o motivo da última para `Fica de fora`."""
    reason = None
    for to_status, why in changes:
        if to_status is ScopeStatus.OUT:
            reason = why
    return reason
