from collections.abc import Callable
from dataclasses import dataclass

from wedding.modules.schedule.application.commands.change_milestone_state import (
    ChangeMilestoneState,
)
from wedding.modules.schedule.application.commands.create_milestone import CreateMilestone
from wedding.modules.schedule.application.commands.create_phase import CreatePhase
from wedding.modules.schedule.application.commands.delete_milestone import DeleteMilestone
from wedding.modules.schedule.application.commands.rename_phase import RenamePhase
from wedding.modules.schedule.application.commands.reorder_phases import ReorderPhases
from wedding.modules.schedule.application.commands.restore_milestone import RestoreMilestone
from wedding.modules.schedule.application.commands.set_milestone_dependencies import (
    SetMilestoneDependencies,
)
from wedding.modules.schedule.application.commands.update_milestone import UpdateMilestone
from wedding.modules.schedule.application.commands.update_milestone_window import (
    UpdateMilestoneWindow,
)
from wedding.modules.schedule.application.queries.preview_date_change import PreviewDateChange
from wedding.modules.schedule.application.queries.read_schedule import ReadSchedule


@dataclass(frozen=True)
class ScheduleUseCases:
    read_schedule: ReadSchedule
    update_milestone: UpdateMilestone
    update_milestone_window: UpdateMilestoneWindow
    preview_date_change: PreviewDateChange
    change_milestone_state: ChangeMilestoneState
    create_milestone: CreateMilestone
    delete_milestone: DeleteMilestone
    restore_milestone: RestoreMilestone
    set_milestone_dependencies: SetMilestoneDependencies
    create_phase: CreatePhase
    rename_phase: RenamePhase
    reorder_phases: ReorderPhases


ScheduleProvider = Callable[[], ScheduleUseCases]
