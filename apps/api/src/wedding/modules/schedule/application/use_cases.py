from collections.abc import Callable
from dataclasses import dataclass

from wedding.modules.schedule.application.commands.change_milestone_state import (
    ChangeMilestoneState,
)
from wedding.modules.schedule.application.commands.update_milestone import UpdateMilestone
from wedding.modules.schedule.application.queries.read_schedule import ReadSchedule


@dataclass(frozen=True)
class ScheduleUseCases:
    read_schedule: ReadSchedule
    update_milestone: UpdateMilestone
    change_milestone_state: ChangeMilestoneState


ScheduleProvider = Callable[[], ScheduleUseCases]
