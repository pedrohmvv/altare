from wedding.modules.schedule.adapters.http.schemas import (
    BlockerOut,
    CategoryLinkOut,
    CategoryOptionOut,
    CreatedMilestoneOut,
    DependencyOut,
    LeftOutOut,
    MilestoneOut,
    MilestoneRefOut,
    PhaseOut,
    PhaseProgressOut,
    RestoreOut,
    ScheduleOut,
    WarningOut,
)
from wedding.modules.schedule.application.dto import (
    CreatedMilestoneDto,
    MilestoneDto,
    PhaseDto,
    RestoreDto,
    ScheduleDto,
)


def _to_milestone_out(milestone: MilestoneDto) -> MilestoneOut:
    return MilestoneOut(
        id=milestone.id,
        title=milestone.title,
        position=milestone.position,
        responsible=milestone.responsible,
        note=milestone.note,
        target_date=milestone.target_date,
        state=milestone.state,
        optional=milestone.optional,
        archived=milestone.archived,
        overdue=milestone.overdue,
        blocked_by=[
            BlockerOut(kind=b.kind, milestone_id=b.milestone_id, label=b.label)
            for b in milestone.blocked_by
        ],
        depends_on=[
            DependencyOut(id=d.id, title=d.title, resolved=d.resolved) for d in milestone.depends_on
        ],
        unlocks=[MilestoneRefOut(id=u.id, title=u.title) for u in milestone.unlocks],
        warnings=[
            WarningOut(kind=w.kind, milestone_id=w.milestone_id, title=w.title)
            for w in milestone.warnings
        ],
        category=(
            CategoryLinkOut(id=milestone.category.id, name=milestone.category.name)
            if milestone.category
            else None
        ),
        version=milestone.version,
    )


def _to_phase_out(phase: PhaseDto) -> PhaseOut:
    return PhaseOut(
        id=phase.id,
        title=phase.title,
        position=phase.position,
        progress=PhaseProgressOut(done=phase.progress.done, total=phase.progress.total),
        milestones=[_to_milestone_out(m) for m in phase.milestones],
        version=phase.version,
    )


def to_schedule_out(schedule: ScheduleDto) -> ScheduleOut:
    return ScheduleOut(
        phases=[_to_phase_out(phase) for phase in schedule.phases],
        category_options=[
            CategoryOptionOut(id=option.id, name=option.name)
            for option in schedule.category_options
        ],
        has_exact_date=schedule.has_exact_date,
    )


def to_restore_out(restored: RestoreDto) -> RestoreOut:
    return RestoreOut(
        schedule=to_schedule_out(restored.schedule),
        left_out=[
            LeftOutOut(milestone_id=item.milestone_id, title=item.title, direction=item.direction)
            for item in restored.left_out
        ],
    )


def to_created_milestone_out(created: CreatedMilestoneDto) -> CreatedMilestoneOut:
    return CreatedMilestoneOut(
        schedule=to_schedule_out(created.schedule), milestone_id=created.milestone_id
    )
