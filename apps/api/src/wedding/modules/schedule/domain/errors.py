from collections.abc import Sequence
from uuid import UUID

from wedding.shared_kernel.errors import DomainRuleViolated


class InvalidScheduleValue(DomainRuleViolated):
    default_code = "invalid_schedule_value"


class MilestoneBlocked(DomainRuleViolated):
    default_code = "milestone_blocked"


class MilestoneTitleRequired(DomainRuleViolated):
    default_code = "milestone_title_required"


class PhaseTitleRequired(DomainRuleViolated):
    default_code = "phase_title_required"


class InvalidPhaseOrder(DomainRuleViolated):
    default_code = "invalid_phase_order"


class SelfDependency(DomainRuleViolated):
    default_code = "self_dependency"


class CategoryNotAvailable(DomainRuleViolated):
    default_code = "category_not_available"


class DependencyCycle(DomainRuleViolated):
    """Fechar a dependência criaria um ciclo (F-CRN-03, regra 2). Leva o caminho, do marco de volta
    a ele mesmo, para a tela mostrar e a pessoa saber qual dependência remover."""

    default_code = "dependency_cycle"
    detail_params_keys = frozenset({"path"})

    def __init__(self, path: Sequence[tuple[UUID, str]]) -> None:
        super().__init__(
            data={"path": [{"id": step_id, "title": title} for step_id, title in path]},
            detail_params={"path": " → ".join(title for _, title in path)},
        )


class InvalidMilestoneWindow(DomainRuleViolated):
    default_code = "invalid_window"


class InvalidPreviewDate(DomainRuleViolated):
    default_code = "invalid_preview_date"
