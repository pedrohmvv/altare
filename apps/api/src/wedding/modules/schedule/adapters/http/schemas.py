import datetime as dt
from uuid import UUID

from pydantic import BaseModel, Field

from wedding.modules.schedule.application.dto import LeftOutDirection, WarningKind
from wedding.modules.schedule.domain.values import BlockerKind, ManualState, MilestoneState
from wedding.shared_kernel.profile import ProfileKind

_VERSION = Field(ge=1, description="A versão do marco que a tela viu; divergir dá 409.")


# Entrada: nenhum campo de autoria nem de perfil de quem age; os dois vêm sempre da sessão.
class MilestoneCreateIn(BaseModel):
    title: str
    phase_id: UUID
    responsible: ProfileKind = ProfileKind.AMBOS
    category_id: UUID | None = Field(
        default=None, description="Uma categoria do Mapa de Escopo, pelo id; nenhuma se nulo."
    )
    depends_on: list[UUID] = Field(
        default_factory=list, description="Marcos vivos de que o novo depende; vale como conjunto."
    )


class MilestoneUpdateIn(BaseModel):
    """A substituição inteira dos campos editáveis: todos são obrigatórios, e o que pode ficar vazio
    vai como nulo, para omitir um campo nunca apagar um dado em silêncio. Mudar `phase_id` leva o
    marco para o fim da nova fase."""

    title: str
    phase_id: UUID
    responsible: ProfileKind
    category_id: UUID | None = Field(description="Nulo desliga a ligação com o Mapa de Escopo.")
    note: str | None = Field(description="Nulo ou em branco apaga a nota.")
    target_date: dt.date | None = Field(description="Nulo apaga o prazo-alvo manual.")
    version: int = _VERSION


class MilestoneDependenciesIn(BaseModel):
    depends_on: list[UUID] = Field(
        description="O conjunto inteiro de predecessores; substitui o atual. Repetido vale uma vez."
    )
    version: int = _VERSION


class PhaseCreateIn(BaseModel):
    title: str


class PhaseRenameIn(BaseModel):
    title: str
    version: int = Field(ge=1, description="A versão da fase que a tela viu; divergir dá 409.")


class PhaseOrderIn(BaseModel):
    ids: list[UUID] = Field(
        description="Exatamente as fases vivas, sem repetir e sem faltar, na nova ordem."
    )


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


class CategoryOptionOut(BaseModel):
    id: UUID
    name: str


class LeftOutOut(BaseModel):
    milestone_id: UUID
    title: str
    direction: LeftOutDirection


class PhaseProgressOut(BaseModel):
    done: int
    total: int


class PhaseOut(BaseModel):
    id: UUID
    title: str
    position: int
    progress: PhaseProgressOut
    milestones: list[MilestoneOut]
    version: int


class ScheduleOut(BaseModel):
    phases: list[PhaseOut]
    category_options: list[CategoryOptionOut]
    has_exact_date: bool


class RestoreOut(BaseModel):
    schedule: ScheduleOut
    left_out: list[LeftOutOut]


class CreatedMilestoneOut(BaseModel):
    schedule: ScheduleOut
    milestone_id: UUID
