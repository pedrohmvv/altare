import datetime as dt
from uuid import UUID

from pydantic import BaseModel, Field

from wedding.modules.schedule.application.dto import WarningKind
from wedding.modules.schedule.domain.values import BlockerKind, ManualState, MilestoneState
from wedding.shared_kernel.profile import ProfileKind

_VERSION = Field(ge=1, description="A versão do marco que a tela viu; divergir dá 409.")


# Entrada: nenhum campo de autoria nem de perfil de quem age; os dois vêm sempre da sessão.
class MilestoneUpdateIn(BaseModel):
    responsible: ProfileKind
    note: str | None = None
    target_date: dt.date | None = None
    version: int = _VERSION


class MilestoneStateIn(BaseModel):
    state: ManualState | None = Field(
        description="Em andamento ou Concluído; nulo reabre e volta ao estado derivado."
    )
    ignore_block: bool = Field(
        default=False,
        description=(
            "A confirmação de marcar Em andamento ou Concluído (inclusive saindo de Concluído) "
            "um marco que aguarda algo: a categoria ainda em discussão no Mapa de Escopo ou uma "
            "dependência não resolvida. Sem ela, esse pedido responde 422 (milestone_blocked)."
        ),
    )
    version: int = _VERSION


# Saída: nenhum valor padrão, para o contrato declarar todos os campos como obrigatórios.
class MilestoneRefOut(BaseModel):
    id: UUID
    title: str


class DependencyOut(BaseModel):
    id: UUID
    title: str
    resolved: bool


class BlockerOut(BaseModel):
    kind: BlockerKind
    milestone_id: UUID | None
    label: str


class WarningOut(BaseModel):
    kind: WarningKind
    milestone_id: UUID
    title: str


class CategoryLinkOut(BaseModel):
    id: UUID
    name: str | None


class MilestoneOut(BaseModel):
    id: UUID
    title: str
    position: int
    responsible: ProfileKind
    note: str | None
    target_date: dt.date | None
    state: MilestoneState
    optional: bool
    archived: bool
    overdue: bool
    blocked_by: list[BlockerOut]
    depends_on: list[DependencyOut]
    unlocks: list[MilestoneRefOut]
    warnings: list[WarningOut]
    category: CategoryLinkOut | None
    version: int


class PhaseProgressOut(BaseModel):
    done: int
    total: int


class PhaseOut(BaseModel):
    id: UUID
    title: str
    position: int
    progress: PhaseProgressOut
    milestones: list[MilestoneOut]


class ScheduleOut(BaseModel):
    phases: list[PhaseOut]
    has_exact_date: bool
