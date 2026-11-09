from collections.abc import Callable
from dataclasses import dataclass

from wedding.modules.wedding.application.commands.update_baseline_field import UpdateBaselineField
from wedding.modules.wedding.application.queries.get_baseline import GetBaseline
from wedding.modules.wedding.application.queries.get_wedding_date import GetWeddingDate
from wedding.modules.wedding.application.queries.list_baseline_changes import ListBaselineChanges


@dataclass(frozen=True)
class WeddingUseCases:
    get_baseline: GetBaseline
    get_wedding_date: GetWeddingDate
    update_baseline_field: UpdateBaselineField
    list_baseline_changes: ListBaselineChanges


WeddingProvider = Callable[[], WeddingUseCases]
