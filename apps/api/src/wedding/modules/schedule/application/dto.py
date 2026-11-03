from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from uuid import UUID

from wedding.modules.schedule.domain.derivation import PhaseProgress
from wedding.modules.schedule.domain.values import BlockerKind, MilestoneState
from wedding.shared_kernel.profile import ProfileKind

# O texto que a tela mostra quando a categoria ligada ainda está `Em discussão` (F-CRN-04).
CATEGORY_UNCLASSIFIED_LABEL = "Aguardando classificar a categoria no Mapa de Escopo"


class WarningKind(StrEnum):
    DEPENDS_ON_UNRESOLVED = "depends_on_unresolved"


@dataclass(frozen=True)
class MilestoneRefDto:
    id: UUID
    title: str


@dataclass(frozen=True)
class DependencyDto:
    id: UUID
    title: str
    resolved: bool


@dataclass(frozen=True)
class BlockerDto:
    """Um motivo do bloqueio: o marco que falta (`milestone_id` e `label` com o nome dele) ou a
    categoria ainda `Em discussão` (`label` é a frase pronta, sem `milestone_id`)."""

    kind: BlockerKind
    milestone_id: UUID | None
    label: str


@dataclass(frozen=True)
class WarningDto:
    kind: WarningKind
    milestone_id: UUID
    title: str


@dataclass(frozen=True)
class CategoryLinkDto:
    """A categoria ligada, com o nome de hoje; `name` é nulo se a categoria foi excluída."""

    id: UUID
    name: str | None


@dataclass(frozen=True)
class MilestoneDto:
    id: UUID
    title: str
    position: int
    responsible: ProfileKind
    note: str | None
    target_date: date | None
    state: MilestoneState
    optional: bool
    archived: bool
    overdue: bool
    blocked_by: tuple[BlockerDto, ...]
    depends_on: tuple[DependencyDto, ...]
    unlocks: tuple[MilestoneRefDto, ...]
    warnings: tuple[WarningDto, ...]
    category: CategoryLinkDto | None
    version: int


@dataclass(frozen=True)
class PhaseDto:
    id: UUID
    title: str
    position: int
    progress: PhaseProgress
    milestones: tuple[MilestoneDto, ...]


@dataclass(frozen=True)
class ScheduleDto:
    phases: tuple[PhaseDto, ...]
    # Modo Com Data: a data do casamento é `Definida` e exata. O cálculo das janelas é de outro PR.
    has_exact_date: bool
