from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date
from uuid import UUID

from wedding.modules.schedule.domain.values import (
    BlockerKind,
    ManualState,
    MilestoneState,
    Standing,
)
from wedding.modules.schedule.domain.windows import Window, window_dates


@dataclass(frozen=True)
class MilestoneFacts:
    """O que a derivação precisa saber de um marco. `standing` é `None` no marco sem categoria."""

    id: UUID
    manual_state: ManualState | None
    standing: Standing | None
    target_date: date | None
    depends_on: tuple[UUID, ...]
    window: Window | None = None


@dataclass(frozen=True)
class Blocker:
    kind: BlockerKind
    milestone_id: UUID | None


@dataclass(frozen=True)
class DependencyStatus:
    milestone_id: UUID
    resolved: bool


@dataclass(frozen=True)
class Derived:
    state: MilestoneState
    optional: bool
    archived: bool
    overdue: bool
    blockers: tuple[Blocker, ...]
    dependencies: tuple[DependencyStatus, ...]
    unlocks: tuple[UUID, ...]
    unresolved: tuple[UUID, ...]
    window_start: date | None = None
    window_end: date | None = None
    effective_target: date | None = None
    days_left: int | None = None


@dataclass(frozen=True)
class PhaseProgress:
    done: int
    total: int


def _is_resolved(predecessor: MilestoneFacts) -> bool:
    """ "A depende de B" está resolvida quando B está concluído, arquivado (`Fica de fora`) ou
    opcional (`Talvez`) (F-CRN-03, regra 1). Não é transitiva: só olha o estado do próprio B."""
    return predecessor.manual_state is ManualState.DONE or predecessor.standing in (
        Standing.OUT,
        Standing.MAYBE,
    )


def _blockers(facts: MilestoneFacts, pending: tuple[UUID, ...]) -> tuple[Blocker, ...]:
    category = (
        (Blocker(BlockerKind.CATEGORY_UNCLASSIFIED, None),)
        if facts.standing is Standing.IN_DISCUSSION
        else ()
    )
    return (*category, *(Blocker(BlockerKind.MILESTONE, dependency) for dependency in pending))


def _state(facts: MilestoneFacts, blockers: tuple[Blocker, ...]) -> MilestoneState:
    """O estado manual vence o derivado; sem marca, há bloqueio ou não."""
    if facts.manual_state is ManualState.DONE:
        return MilestoneState.DONE
    if facts.manual_state is ManualState.IN_PROGRESS:
        return MilestoneState.IN_PROGRESS
    return MilestoneState.BLOCKED if blockers else MilestoneState.UNLOCKED


def _dependencies(
    item: MilestoneFacts, by_id: dict[UUID, MilestoneFacts]
) -> tuple[DependencyStatus, ...]:
    return tuple(
        DependencyStatus(predecessor, _is_resolved(by_id[predecessor]))
        for predecessor in item.depends_on
        if predecessor in by_id
    )


def _pending(dependencies: tuple[DependencyStatus, ...]) -> tuple[UUID, ...]:
    return tuple(dep.milestone_id for dep in dependencies if not dep.resolved)


def _waiting(
    item: MilestoneFacts, dependencies: tuple[DependencyStatus, ...]
) -> tuple[Blocker, ...]:
    return _blockers(item, _pending(dependencies))


def waiting_on(facts: Sequence[MilestoneFacts], milestone_id: UUID) -> tuple[Blocker, ...]:
    """O que o marco aguarda, sem olhar a marca manual dele: a categoria `Em discussão` e as
    dependências não resolvidas. É o que decide se marcar `Em andamento` ou `Concluído` precisa
    da confirmação "ignorar o bloqueio" (F-CRN-03, regra 4), inclusive saindo de `Concluído`."""
    by_id = {item.id: item for item in facts}
    return _waiting(by_id[milestone_id], _dependencies(by_id[milestone_id], by_id))


def derive(
    facts: Sequence[MilestoneFacts], today: date, wedding_date: date | None = None
) -> dict[UUID, Derived]:
    """Tudo o que se deriva dos marcos, do Mapa de Escopo e do dia de hoje (`architecture.md` §5).
    Função pura: o mesmo cronograma no mesmo dia dá sempre a mesma resposta e nada é gravado.

    Os bloqueios existem para todo marco não concluído (o `Em andamento` guarda o estado, mas a
    lista continua dizendo o que falta); o concluído tem, em vez deles, o aviso de quais
    predecessores não estão resolvidos (F-CRN-03, regra 5), tenham sido reabertos ou nunca
    concluídos. "Libera" não lista os arquivados, que saíram das listas ativas, e o atraso e a
    contagem regressiva também não valem para eles (F-CRN-04).

    `wedding_date` é a data exata `Definida` do casamento (Modo Com Data) ou `None` (Modo Sem
    Data): só com ela as janelas ganham datas e o fim delas vira o prazo-alvo padrão. O atraso
    olha o prazo efetivo, o manual ou o fim da janela (F-CRN-05)."""
    by_id = {item.id: item for item in facts}
    unlocks: dict[UUID, list[UUID]] = {item.id: [] for item in facts}
    for item in facts:
        if item.standing is Standing.OUT:
            continue
        for predecessor in item.depends_on:
            if predecessor in by_id:
                unlocks[predecessor].append(item.id)

    result: dict[UUID, Derived] = {}
    for item in facts:
        dependencies = _dependencies(item, by_id)
        done = item.manual_state is ManualState.DONE
        blockers = () if done else _waiting(item, dependencies)
        archived = item.standing is Standing.OUT
        calculated = _calculated_window(item, wedding_date)
        # O prazo digitado à mão prevalece; sem ele, o fim da janela calculada (F-CRN-05).
        effective_target = item.target_date or (calculated[1] if calculated else None)
        counts = not done and not archived
        overdue = effective_target is not None and effective_target < today and counts
        result[item.id] = Derived(
            state=_state(item, blockers),
            optional=item.standing is Standing.MAYBE,
            archived=archived,
            overdue=overdue,
            blockers=blockers,
            dependencies=dependencies,
            unlocks=tuple(unlocks[item.id]),
            unresolved=_pending(dependencies) if done else (),
            window_start=calculated[0] if calculated else None,
            window_end=calculated[1] if calculated else None,
            effective_target=effective_target,
            days_left=(effective_target - today).days if effective_target and counts else None,
        )
    return result


def _calculated_window(item: MilestoneFacts, wedding_date: date | None) -> tuple[date, date] | None:
    """As datas da janela só existem no Modo Com Data e para o marco que tem janela."""
    if wedding_date is None or item.window is None:
        return None
    return window_dates(
        wedding_date, item.window.start_before, item.window.end_before, item.window.unit
    )


def phase_progress(members: Iterable[Derived]) -> PhaseProgress:
    """ "N de M concluídos": os opcionais contam e só os arquivados saem (F-CRN-09)."""
    active = [member for member in members if not member.archived]
    return PhaseProgress(
        done=sum(member.state is MilestoneState.DONE for member in active), total=len(active)
    )
