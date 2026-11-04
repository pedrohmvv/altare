from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum
from uuid import UUID

from wedding.modules.schedule.domain.attachments import AttachmentKind
from wedding.modules.schedule.domain.checklist import ChecklistProgress
from wedding.modules.schedule.domain.derivation import PhaseProgress
from wedding.modules.schedule.domain.values import BlockerKind, MilestoneState, TaskState
from wedding.modules.schedule.domain.windows import WindowUnit
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
class MilestoneWindowDto:
    """A janela do marco em deslocamentos antes da data do casamento, sempre presente quando há
    janela (mesmo no Modo Sem Data). `is_suggestion`: ninguém a editou, a "sugestão genérica"."""

    start_before: int
    end_before: int
    unit: WindowUnit
    is_suggestion: bool


@dataclass(frozen=True)
class ChecklistItemDto:
    """Um item vivo do checklist de um marco ou de uma avulsa (F-CRN-07), com `version` própria."""

    id: UUID
    text: str
    done: bool
    position: int
    version: int


@dataclass(frozen=True)
class AttachmentFileDto:
    """O arquivo de um anexo, com o nome, o tipo e o tamanho copiados ao anexar."""

    id: UUID
    name: str
    content_type: str
    size_bytes: int


@dataclass(frozen=True)
class AttachmentDto:
    """Um anexo vivo de um marco ou de uma avulsa (F-CRN-08): link (`url` e o `domain` derivado) ou
    arquivo. `can_remove` é derivado do perfil da sessão: só o autor remove."""

    id: UUID
    kind: AttachmentKind
    title: str | None
    comment: str | None
    url: str | None
    domain: str | None
    file: AttachmentFileDto | None
    profile: ProfileKind
    added_at: datetime
    can_remove: bool


@dataclass(frozen=True)
class MilestoneDto:
    id: UUID
    title: str
    position: int
    responsible: ProfileKind
    note: str | None
    # Só o prazo digitado à mão. O prazo que vale é `effective_target`.
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
    window: MilestoneWindowDto | None
    # Modo Com Data: as datas da janela; nulas no Modo Sem Data ou sem janela (F-CRN-05).
    window_start: date | None
    window_end: date | None
    # O prazo manual, senão o fim da janela calculada; nulo se nenhum dos dois existe.
    effective_target: date | None
    # Dias de hoje (Brasília) ao prazo efetivo: negativo é passado, 0 é hoje. Nulo se o marco está
    # concluído, arquivado ou sem prazo efetivo.
    days_left: int | None
    # Os itens vivos na ordem do checklist e o "N de M" (F-CRN-07); não mexem no estado do marco.
    checklist: tuple[ChecklistItemDto, ...]
    checklist_progress: ChecklistProgress
    # Os anexos vivos, na ordem em que foram anexados; não mexem no estado nem na `version`.
    attachments: tuple[AttachmentDto, ...]
    version: int


@dataclass(frozen=True)
class TaskDto:
    """Uma tarefa avulsa (F-CRN-06). Fora das fases e fora da derivação dos marcos: nunca bloqueia
    nem é liberada por ninguém."""

    id: UUID
    title: str
    responsible: ProfileKind
    note: str | None
    target_date: date | None
    state: TaskState
    # Prazo vencido e não concluída, com o dia de hoje em Brasília.
    overdue: bool
    # Dias de hoje ao prazo (negativo é passado, 0 é hoje); nulo se concluída ou sem prazo.
    days_left: int | None
    checklist: tuple[ChecklistItemDto, ...]
    checklist_progress: ChecklistProgress
    attachments: tuple[AttachmentDto, ...]
    version: int


@dataclass(frozen=True)
class PhaseDto:
    id: UUID
    title: str
    position: int
    progress: PhaseProgress
    milestones: tuple[MilestoneDto, ...]
    version: int


@dataclass(frozen=True)
class CategoryOptionDto:
    """Uma categoria do Mapa que o casal pode ligar a um marco, com o nome de hoje."""

    id: UUID
    name: str


class LeftOutDirection(StrEnum):
    """O sentido do vínculo que não voltou ao restaurar um marco, a partir do marco restaurado."""

    DEPENDS_ON = "depends_on"
    DEPENDENCY_OF = "dependency_of"


@dataclass(frozen=True)
class LeftOutDto:
    """Um vínculo que não voltou ao restaurar: o outro marco (id e título) e o sentido."""

    milestone_id: UUID
    title: str
    direction: LeftOutDirection


@dataclass(frozen=True)
class ScheduleDto:
    phases: tuple[PhaseDto, ...]
    # As avulsas vivas, fora das fases, na ordem da lista (concluídas e sem prazo por último).
    tasks: tuple[TaskDto, ...]
    # As categorias não ocultas na ordem do Mapa, mais as ocultas que algum marco já tem ligadas.
    category_options: tuple[CategoryOptionDto, ...]
    # Modo Com Data: a data do casamento é `Definida` e exata (F-CRN-05).
    has_exact_date: bool


@dataclass(frozen=True)
class RestoreDto:
    schedule: ScheduleDto
    left_out: tuple[LeftOutDto, ...]


@dataclass(frozen=True)
class CreatedMilestoneDto:
    """O cronograma já com o marco novo e o id dele, para a tela abrir o painel do marco."""

    schedule: ScheduleDto
    milestone_id: UUID


class DateMode(StrEnum):
    NO_DATE = "sem_data"
    WITH_DATE = "com_data"


@dataclass(frozen=True)
class DateRangeDto:
    start: date
    end: date


@dataclass(frozen=True)
class DateChangeDto:
    """Um marco cujas datas calculadas mudam se a data do casamento mudar; `None` é "sem datas
    calculadas" (o Modo Sem Data)."""

    id: UUID
    title: str
    window_before: DateRangeDto | None
    window_after: DateRangeDto | None
    target_before: date | None
    target_after: date | None


@dataclass(frozen=True)
class DatePreviewDto:
    """O que mudaria no cronograma se a data do casamento fosse outra (F-CRN-05, regra 4). Só conta
    marcos ativos e não concluídos; nada é gravado."""

    mode_before: DateMode
    mode_after: DateMode
    changes: tuple[DateChangeDto, ...]
    # Marcos com janela e prazo manual: o prazo não muda, mas a janela calculada acompanha a data.
    manual_kept: int
    newly_overdue: int
