from dataclasses import dataclass
from datetime import date
from uuid import UUID

from wedding.modules.schedule.application.dates import today_in_brazil
from wedding.modules.schedule.application.dto import (
    CATEGORY_UNCLASSIFIED_LABEL,
    BlockerDto,
    CategoryLinkDto,
    CategoryOptionDto,
    DependencyDto,
    MilestoneDto,
    MilestoneRefDto,
    MilestoneWindowDto,
    PhaseDto,
    ScheduleDto,
    WarningDto,
    WarningKind,
)
from wedding.modules.schedule.application.ports import (
    CategoryInfo,
    CategoryReader,
    ScheduleRepository,
    WeddingDateReader,
)
from wedding.modules.schedule.domain.derivation import (
    Blocker,
    Derived,
    MilestoneFacts,
    derive,
    phase_progress,
)
from wedding.modules.schedule.domain.entities import Milestone, Phase
from wedding.modules.schedule.domain.errors import CategoryNotAvailable
from wedding.modules.schedule.domain.values import BlockerKind, Standing
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.clock import Clock
from wedding.shared_kernel.errors import NotFound


@dataclass(frozen=True)
class _Loaded:
    phases: list[Phase]
    milestones: list[Milestone]
    categories: dict[UUID, CategoryInfo]
    facts: list[MilestoneFacts]


class ScheduleReader:
    """Monta o cronograma inteiro, com tudo o que é derivado calculado aqui e nunca gravado
    (`architecture.md` §5): bloqueios, opcional, arquivado, datas das janelas, prazo efetivo,
    contagem regressiva, atraso, avisos e progresso por fase."""

    def __init__(
        self, categories: CategoryReader, wedding_date: WeddingDateReader, clock: Clock
    ) -> None:
        self._categories = categories
        self._wedding_date = wedding_date
        self._clock = clock

    def _load(self, schedule: ScheduleRepository, actor: Actor) -> _Loaded:
        categories = self._categories.categories(actor)
        depends_on: dict[UUID, list[UUID]] = {}
        for link in schedule.dependencies():
            depends_on.setdefault(link.milestone_id, []).append(link.depends_on_id)
        phases = sorted(schedule.list_phases(), key=lambda phase: (phase.position, phase.title))
        phase_order = {phase.id: index for index, phase in enumerate(phases)}
        # A ordem do cronograma inteiro (fase, posição, título): quem lê "libera" a recebe também.
        ordered = sorted(
            schedule.list_milestones(),
            key=lambda item: (phase_order[item.phase_id], item.position, item.title),
        )
        facts = [
            MilestoneFacts(
                id=item.id,
                manual_state=item.manual_state,
                standing=_standing(item, categories),
                target_date=item.target_date,
                depends_on=tuple(depends_on.get(item.id, ())),
                window=item.window,
            )
            for item in ordered
        ]
        return _Loaded(phases, ordered, categories, facts)

    def facts(self, schedule: ScheduleRepository, actor: Actor) -> list[MilestoneFacts]:
        """Os fatos de cada marco, na ordem do cronograma, como a derivação os recebe."""
        return self._load(schedule, actor).facts

    def today(self) -> date:
        """Hoje é o dia em Brasília (`D-031`)."""
        return today_in_brazil(self._clock)

    def exact_wedding_date(self, actor: Actor) -> date | None:
        """A data do casamento que liga o Modo Com Data: só vale `Definida` e exata."""
        wedding_date = self._wedding_date.wedding_date(actor)
        return wedding_date.exact if wedding_date.is_exact_and_defined else None

    def read(self, schedule: ScheduleRepository, actor: Actor) -> ScheduleDto:
        loaded = self._load(schedule, actor)
        exact = self.exact_wedding_date(actor)
        derived = derive(loaded.facts, self.today(), exact)
        titles = {item.id: item.title for item in loaded.milestones}

        phase_dtos = []
        for phase in loaded.phases:
            members = [item for item in loaded.milestones if item.phase_id == phase.id]
            phase_dtos.append(
                PhaseDto(
                    id=phase.id,
                    title=phase.title,
                    position=phase.position,
                    progress=phase_progress(derived[item.id] for item in members),
                    milestones=tuple(
                        _milestone_dto(item, derived[item.id], titles, loaded.categories)
                        for item in members
                    ),
                    version=phase.version,
                )
            )
        linked = {item.category_id for item in loaded.milestones if item.category_id}
        return ScheduleDto(
            phases=tuple(phase_dtos),
            category_options=tuple(
                CategoryOptionDto(category_id, info.name)
                for category_id, info in loaded.categories.items()
                if info.visible or category_id in linked
            ),
            has_exact_date=exact is not None,
        )


def _standing(milestone: Milestone, categories: dict[UUID, CategoryInfo]) -> Standing | None:
    if milestone.category_id is None:
        return None
    info = categories.get(milestone.category_id)
    # A categoria que a leitura não traz foi excluída, e a excluída conta como `Fica de fora`.
    return info.standing if info else Standing.OUT


def _category_link(
    milestone: Milestone, categories: dict[UUID, CategoryInfo]
) -> CategoryLinkDto | None:
    if milestone.category_id is None:
        return None
    info = categories.get(milestone.category_id)
    return CategoryLinkDto(milestone.category_id, info.name if info else None)


def _blocker_dto(blocker: Blocker, titles: dict[UUID, str]) -> BlockerDto:
    if blocker.kind is BlockerKind.CATEGORY_UNCLASSIFIED or blocker.milestone_id is None:
        return BlockerDto(blocker.kind, None, CATEGORY_UNCLASSIFIED_LABEL)
    return BlockerDto(blocker.kind, blocker.milestone_id, titles[blocker.milestone_id])


def _milestone_dto(
    milestone: Milestone,
    derived: Derived,
    titles: dict[UUID, str],
    categories: dict[UUID, CategoryInfo],
) -> MilestoneDto:
    return MilestoneDto(
        id=milestone.id,
        title=milestone.title,
        position=milestone.position,
        responsible=milestone.responsible,
        note=milestone.note,
        target_date=milestone.target_date,
        state=derived.state,
        optional=derived.optional,
        archived=derived.archived,
        overdue=derived.overdue,
        blocked_by=tuple(_blocker_dto(blocker, titles) for blocker in derived.blockers),
        depends_on=tuple(
            DependencyDto(dep.milestone_id, titles[dep.milestone_id], dep.resolved)
            for dep in derived.dependencies
        ),
        unlocks=tuple(MilestoneRefDto(other, titles[other]) for other in derived.unlocks),
        warnings=tuple(
            WarningDto(WarningKind.DEPENDS_ON_UNRESOLVED, other, titles[other])
            for other in derived.unresolved
        ),
        category=_category_link(milestone, categories),
        window=(
            MilestoneWindowDto(
                milestone.window.start_before,
                milestone.window.end_before,
                milestone.window.unit,
                milestone.window_is_suggestion,
            )
            if milestone.window
            else None
        ),
        window_start=derived.window_start,
        window_end=derived.window_end,
        effective_target=derived.effective_target,
        days_left=derived.days_left,
        version=milestone.version,
    )


def require_milestone(schedule: ScheduleRepository, milestone_id: UUID) -> Milestone:
    milestone = schedule.get_milestone(milestone_id)
    if milestone is None:
        raise NotFound()
    return milestone


def require_phase(schedule: ScheduleRepository, phase_id: UUID) -> Phase:
    phase = schedule.get_phase(phase_id)
    if phase is None:
        raise NotFound()
    return phase


def require_linkable_category(
    categories: dict[UUID, CategoryInfo], category_id: UUID | None, current: UUID | None = None
) -> None:
    """A categoria que o casal liga existe no Mapa e não está oculta. Manter a que o marco já tem,
    mesmo oculta, não é uma nova ligação e passa (F-CRN-04)."""
    if category_id is None or category_id == current:
        return
    info = categories.get(category_id)
    if info is None or not info.visible:
        raise CategoryNotAvailable()
