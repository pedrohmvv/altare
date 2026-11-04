from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID

from wedding.modules.schedule.application.dates import today_in_brazil
from wedding.modules.schedule.application.dto import (
    CATEGORY_UNCLASSIFIED_LABEL,
    AttachmentDto,
    AttachmentFileDto,
    BlockerDto,
    CategoryLinkDto,
    CategoryOptionDto,
    ChecklistItemDto,
    DependencyDto,
    MilestoneDto,
    MilestoneRefDto,
    MilestoneWindowDto,
    PhaseDto,
    ScheduleDto,
    TaskDto,
    WarningDto,
    WarningKind,
)
from wedding.modules.schedule.application.ports import (
    CategoryInfo,
    CategoryReader,
    ScheduleRepository,
    WeddingDateReader,
)
from wedding.modules.schedule.domain.attachments import Attachment
from wedding.modules.schedule.domain.checklist import checklist_progress
from wedding.modules.schedule.domain.derivation import (
    Blocker,
    Derived,
    MilestoneFacts,
    derive,
    phase_progress,
)
from wedding.modules.schedule.domain.entities import ChecklistItem, Milestone, Phase, Task
from wedding.modules.schedule.domain.errors import CategoryNotAvailable
from wedding.modules.schedule.domain.tasks import task_deadline, task_order_key
from wedding.modules.schedule.domain.values import BlockerKind, OwnerKind, Standing, TaskState
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.clock import Clock
from wedding.shared_kernel.errors import NotFound


@dataclass(frozen=True)
class _Loaded:
    phases: list[Phase]
    milestones: list[Milestone]
    categories: dict[UUID, CategoryInfo]
    facts: list[MilestoneFacts]
    tasks: list[Task]
    # Os itens vivos agrupados pelo dono vivo, cada lista na ordem do checklist.
    checklists: dict[tuple[OwnerKind, UUID], list[ChecklistItem]]
    # Os anexos vivos agrupados pelo dono vivo, na ordem em que foram anexados.
    attachments: dict[tuple[OwnerKind, UUID], list[Attachment]]


class ScheduleReader:
    """Monta o cronograma inteiro, com tudo o que é derivado calculado aqui e nunca gravado
    (`architecture.md` §5): bloqueios, opcional, arquivado, datas das janelas, prazo efetivo,
    contagem regressiva, atraso, avisos e progresso por fase. As avulsas ficam fora da derivação dos
    marcos (entrariam em "libera" e nos bloqueios): têm o prazo calculado à parte."""

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
        tasks = sorted(schedule.list_tasks(), key=task_order_key)
        return _Loaded(
            phases,
            ordered,
            categories,
            facts,
            tasks,
            _group_checklists(schedule, ordered, tasks),
            _group_attachments(schedule, ordered, tasks),
        )

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
        today = self.today()
        derived = derive(loaded.facts, today, exact)
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
                        _milestone_dto(
                            item,
                            derived[item.id],
                            titles,
                            loaded.categories,
                            loaded.checklists.get((OwnerKind.MILESTONE, item.id), []),
                            self._attachment_dtos(
                                loaded.attachments.get((OwnerKind.MILESTONE, item.id), []), actor
                            ),
                        )
                        for item in members
                    ),
                    version=phase.version,
                )
            )
        linked = {item.category_id for item in loaded.milestones if item.category_id}
        return ScheduleDto(
            phases=tuple(phase_dtos),
            tasks=tuple(
                _task_dto(
                    task,
                    today,
                    loaded.checklists.get((OwnerKind.TASK, task.id), []),
                    self._attachment_dtos(
                        loaded.attachments.get((OwnerKind.TASK, task.id), []), actor
                    ),
                )
                for task in loaded.tasks
            ),
            category_options=tuple(
                CategoryOptionDto(category_id, info.name)
                for category_id, info in loaded.categories.items()
                if info.visible or category_id in linked
            ),
            has_exact_date=exact is not None,
        )

    def _attachment_dtos(
        self, attachments: list[Attachment], actor: Actor
    ) -> tuple[AttachmentDto, ...]:
        # `at` cai no instante de agora só para o anexo ainda não gravado (sem `created_at`).
        fallback = self._clock.now()
        return tuple(_attachment_dto(attachment, actor, fallback) for attachment in attachments)


def _attachment_dto(attachment: Attachment, actor: Actor, fallback: datetime) -> AttachmentDto:
    file = attachment.file
    return AttachmentDto(
        id=attachment.id,
        kind=attachment.kind,
        title=attachment.title,
        comment=attachment.comment,
        url=attachment.url,
        domain=attachment.domain,
        file=AttachmentFileDto(file.file_id, file.name, file.content_type, file.size_bytes)
        if file
        else None,
        profile=attachment.profile,
        added_at=attachment.created_at or fallback,
        can_remove=attachment.profile is actor.profile,
    )


def _group_attachments(
    schedule: ScheduleRepository, milestones: list[Milestone], tasks: list[Task]
) -> dict[tuple[OwnerKind, UUID], list[Attachment]]:
    """Uma consulta só para todos os anexos, agrupados pelo dono, na ordem do repositório. O anexo
    de um dono excluído fica de fora (o dono não está entre os vivos); restaurar o dono o traz de
    volta."""
    live_owners = {(OwnerKind.MILESTONE, item.id) for item in milestones}
    live_owners |= {(OwnerKind.TASK, task.id) for task in tasks}
    grouped: dict[tuple[OwnerKind, UUID], list[Attachment]] = {}
    for attachment in schedule.list_attachments():
        owner = (attachment.owner_kind, attachment.owner_id)
        if owner in live_owners:
            grouped.setdefault(owner, []).append(attachment)
    return grouped


def _group_checklists(
    schedule: ScheduleRepository, milestones: list[Milestone], tasks: list[Task]
) -> dict[tuple[OwnerKind, UUID], list[ChecklistItem]]:
    """Uma consulta só para todos os itens, agrupados pelo dono. O item de um dono excluído fica de
    fora (o dono não está entre os vivos); restaurar o dono o traz de volta."""
    live_owners = {(OwnerKind.MILESTONE, item.id) for item in milestones}
    live_owners |= {(OwnerKind.TASK, task.id) for task in tasks}
    grouped: dict[tuple[OwnerKind, UUID], list[ChecklistItem]] = {}
    for item in schedule.list_checklist_items():
        owner = (item.owner_kind, item.owner_id)
        if owner in live_owners:
            grouped.setdefault(owner, []).append(item)
    for items in grouped.values():
        items.sort(key=lambda item: (item.position, item.id))
    return grouped


def _checklist_dtos(items: list[ChecklistItem]) -> tuple[ChecklistItemDto, ...]:
    return tuple(
        ChecklistItemDto(item.id, item.text, item.done, item.position, item.version)
        for item in items
    )


def _task_dto(
    task: Task,
    today: date,
    items: list[ChecklistItem],
    attachments: tuple[AttachmentDto, ...],
) -> TaskDto:
    deadline = task_deadline(task.target_date, task.state is TaskState.DONE, today)
    return TaskDto(
        id=task.id,
        title=task.title,
        responsible=task.responsible,
        note=task.note,
        target_date=task.target_date,
        state=task.state,
        overdue=deadline.overdue,
        days_left=deadline.days_left,
        checklist=_checklist_dtos(items),
        checklist_progress=checklist_progress(items),
        attachments=attachments,
        version=task.version,
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
    items: list[ChecklistItem],
    attachments: tuple[AttachmentDto, ...],
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
        checklist=_checklist_dtos(items),
        checklist_progress=checklist_progress(items),
        attachments=attachments,
        version=milestone.version,
    )


def require_milestone(schedule: ScheduleRepository, milestone_id: UUID) -> Milestone:
    milestone = schedule.get_milestone(milestone_id)
    if milestone is None:
        raise NotFound()
    return milestone


def require_task(schedule: ScheduleRepository, task_id: UUID) -> Task:
    task = schedule.get_task(task_id)
    if task is None:
        raise NotFound()
    return task


def require_checklist_owner(
    schedule: ScheduleRepository, kind: OwnerKind, owner_id: UUID
) -> Milestone | Task:
    """O marco ou a avulsa vivos que têm o checklist; o id de um tipo não vale no outro."""
    if kind is OwnerKind.MILESTONE:
        return require_milestone(schedule, owner_id)
    return require_task(schedule, owner_id)


def require_checklist_item(schedule: ScheduleRepository, item_id: UUID) -> ChecklistItem:
    """O item vivo cujo dono também está vivo: com o dono excluído, o item é como se não existisse
    (404) até o dono voltar."""
    item = schedule.get_checklist_item(item_id)
    if item is None:
        raise NotFound()
    require_checklist_owner(schedule, item.owner_kind, item.owner_id)
    return item


def require_attachment(schedule: ScheduleRepository, attachment_id: UUID) -> Attachment:
    """O anexo vivo cujo dono também está vivo: com o dono excluído, o anexo é como se não existisse
    (404) até o dono voltar."""
    attachment = schedule.get_attachment(attachment_id)
    if attachment is None:
        raise NotFound()
    require_checklist_owner(schedule, attachment.owner_kind, attachment.owner_id)
    return attachment


def has_open_items(schedule: ScheduleRepository, kind: OwnerKind, owner_id: UUID) -> bool:
    return any(not item.done for item in schedule.live_items_of(kind, owner_id))


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
