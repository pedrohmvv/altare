from wedding.modules.schedule.adapters.http.schemas import (
    AttachmentFileOut,
    AttachmentOut,
    BlockerOut,
    CategoryLinkOut,
    CategoryOptionOut,
    ChecklistItemOut,
    ChecklistProgressOut,
    CreatedMilestoneOut,
    DateChangeOut,
    DatePreviewOut,
    DateRangeOut,
    DependencyOut,
    LeftOutOut,
    MilestoneOut,
    MilestoneRefOut,
    MilestoneWindowOut,
    PhaseOut,
    PhaseProgressOut,
    RestoreOut,
    ScheduleOut,
    TaskOut,
    WarningOut,
)
from wedding.modules.schedule.application.dto import (
    AttachmentDto,
    ChecklistItemDto,
    CreatedMilestoneDto,
    DatePreviewDto,
    DateRangeDto,
    MilestoneDto,
    PhaseDto,
    RestoreDto,
    ScheduleDto,
    TaskDto,
)
from wedding.modules.schedule.domain.checklist import ChecklistProgress


def _to_checklist_out(items: tuple[ChecklistItemDto, ...]) -> list[ChecklistItemOut]:
    return [
        ChecklistItemOut(
            id=item.id, text=item.text, done=item.done, position=item.position, version=item.version
        )
        for item in items
    ]


def _to_attachments_out(attachments: tuple[AttachmentDto, ...]) -> list[AttachmentOut]:
    return [
        AttachmentOut.model_validate(
            {
                "id": item.id,
                "kind": item.kind,
                "title": item.title,
                "comment": item.comment,
                "url": item.url,
                "domain": item.domain,
                "file": AttachmentFileOut(
                    id=item.file.id,
                    name=item.file.name,
                    content_type=item.file.content_type,
                    size_bytes=item.file.size_bytes,
                )
                if item.file
                else None,
                "by": item.profile,
                "at": item.added_at,
                "can_remove": item.can_remove,
            }
        )
        for item in attachments
    ]


def _to_progress_out(progress: ChecklistProgress) -> ChecklistProgressOut:
    return ChecklistProgressOut(done=progress.done, total=progress.total)


def _to_task_out(task: TaskDto) -> TaskOut:
    return TaskOut(
        id=task.id,
        title=task.title,
        responsible=task.responsible,
        note=task.note,
        target_date=task.target_date,
        state=task.state,
        overdue=task.overdue,
        days_left=task.days_left,
        checklist=_to_checklist_out(task.checklist),
        checklist_progress=_to_progress_out(task.checklist_progress),
        attachments=_to_attachments_out(task.attachments),
        version=task.version,
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
        window=(
            MilestoneWindowOut(
                start_before=milestone.window.start_before,
                end_before=milestone.window.end_before,
                unit=milestone.window.unit,
                is_suggestion=milestone.window.is_suggestion,
            )
            if milestone.window
            else None
        ),
        window_start=milestone.window_start,
        window_end=milestone.window_end,
        effective_target=milestone.effective_target,
        days_left=milestone.days_left,
        checklist=_to_checklist_out(milestone.checklist),
        checklist_progress=_to_progress_out(milestone.checklist_progress),
        attachments=_to_attachments_out(milestone.attachments),
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
        tasks=[_to_task_out(task) for task in schedule.tasks],
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


def _to_range_out(window: DateRangeDto | None) -> DateRangeOut | None:
    return DateRangeOut(start=window.start, end=window.end) if window else None


def to_date_preview_out(preview: DatePreviewDto) -> DatePreviewOut:
    return DatePreviewOut(
        mode_before=preview.mode_before,
        mode_after=preview.mode_after,
        changes=[
            DateChangeOut(
                id=change.id,
                title=change.title,
                window_before=_to_range_out(change.window_before),
                window_after=_to_range_out(change.window_after),
                target_before=change.target_before,
                target_after=change.target_after,
            )
            for change in preview.changes
        ],
        manual_kept=preview.manual_kept,
        newly_overdue=preview.newly_overdue,
    )
