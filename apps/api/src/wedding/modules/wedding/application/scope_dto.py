from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from wedding.modules.wedding.domain.scope_rules import Alignment, Progress, Totals
from wedding.modules.wedding.domain.scope_values import Origin, Priority, ScopeStatus
from wedding.shared_kernel.profile import ProfileKind


@dataclass(frozen=True)
class EvaluationDto:
    priority: Priority | None
    note: str | None
    version: int


@dataclass(frozen=True)
class CategoryDto:
    id: UUID
    group_id: UUID
    name: str
    position: int
    origin: Origin
    hidden: bool
    visible: bool
    status: ScopeStatus
    estimate_cents: int | None
    discard_reason: str | None
    noivo: EvaluationDto
    noiva: EvaluationDto
    alignment: Alignment
    can_delete: bool
    version: int


@dataclass(frozen=True)
class GroupDto:
    id: UUID
    name: str
    position: int
    origin: Origin
    hidden: bool
    can_delete: bool
    version: int
    categories: tuple[CategoryDto, ...]


@dataclass(frozen=True)
class ScopeMapDto:
    groups: tuple[GroupDto, ...]
    progress: Progress
    totals: Totals


@dataclass(frozen=True)
class StatusChangeDto:
    id: UUID
    from_status: ScopeStatus
    to_status: ScopeStatus
    reason: str | None
    profile: ProfileKind
    changed_at: datetime
