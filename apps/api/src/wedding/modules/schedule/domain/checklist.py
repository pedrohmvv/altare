from collections.abc import Iterable
from dataclasses import dataclass

from wedding.modules.schedule.domain.entities import ChecklistItem


@dataclass(frozen=True)
class ChecklistProgress:
    """ "2 de 5" (F-CRN-07, regra 3)."""

    done: int
    total: int


def checklist_progress(items: Iterable[ChecklistItem]) -> ChecklistProgress:
    live = list(items)
    return ChecklistProgress(done=sum(item.done for item in live), total=len(live))
