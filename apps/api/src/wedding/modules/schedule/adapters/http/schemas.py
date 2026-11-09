import datetime as dt
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from wedding.modules.schedule.application.dto import DateMode, LeftOutDirection, WarningKind
from wedding.modules.schedule.domain.attachments import AttachmentKind
from wedding.modules.schedule.domain.values import (
    BlockerKind,
    ManualState,
    MilestoneState,
    TaskState,
)
from wedding.modules.schedule.domain.windows import WindowUnit
from wedding.shared_kernel.profile import ProfileKind

LoginProfile = Literal[ProfileKind.NOIVO, ProfileKind.NOIVA]
_VERSION = Field(ge=1, description="A versão do marco que a tela viu; divergir dá 409.")
_IGNORE_OPEN_ITEMS = Field(
    default=False,
    description=(
        "A confirmação de concluir com itens do checklist em aberto. Só vale ao ir para "
        "Concluído (marco) ou Concluída (avulsa); com outro destino é ignorada. Sem ela, esse "
        "pedido responde 422 (checklist_open_items). Concluir não altera os itens."
    ),
)


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


class MilestoneWindowIn(BaseModel):
    """A janela inteira, na unidade dada: do início ao fim, quantas unidades antes da data do
    casamento. Vale em qualquer modo e para o marco que ainda não tinha janela; o início não vem
    depois do fim, `0` e `0` é o dia do casamento e o teto é 120 meses ou 520 semanas."""

    start_before: int
    end_before: int
    unit: WindowUnit
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
    ignore_open_items: bool = _IGNORE_OPEN_ITEMS
    version: int = _VERSION


class TaskCreateIn(BaseModel):
    """A avulsa nasce `A fazer`. O responsável é opcional: sem ele, é o perfil de quem está na
    sessão (`Noivo` ou `Noiva`, nunca `Ambos` por padrão); `Ambos` só se for pedido."""

    title: str
    responsible: ProfileKind | None = Field(
        default=None, description="Sem ele, vale o perfil da sessão; Ambos só se vier explícito."
    )
    note: str | None = None
    target_date: dt.date | None = Field(default=None, description="Entre os anos 2000 e 2100.")


class TaskUpdateIn(BaseModel):
    """A substituição inteira dos campos editáveis: todos são obrigatórios, e o que pode ficar vazio
    vai como nulo, para omitir um campo nunca apagar um dado em silêncio."""

    title: str
    responsible: ProfileKind
    note: str | None = Field(description="Nulo ou em branco apaga a nota.")
    target_date: dt.date | None = Field(description="Nulo apaga o prazo.")
    version: int = Field(ge=1, description="A versão da avulsa que a tela viu; divergir dá 409.")


class TaskStateIn(BaseModel):
    state: TaskState = Field(
        description="Qualquer estado vale a qualquer momento; reabrir é A fazer."
    )
    ignore_open_items: bool = _IGNORE_OPEN_ITEMS
    version: int = Field(ge=1, description="A versão da avulsa que a tela viu; divergir dá 409.")


class ChecklistItemCreateIn(BaseModel):
    text: str = Field(description="O texto do item, de 1 a 200 caracteres.")


class ChecklistItemUpdateIn(BaseModel):
    """A substituição inteira do item: marcar, desmarcar e editar o texto são o mesmo pedido."""

    text: str
    done: bool
    version: int = Field(ge=1, description="A versão do item que a tela viu; divergir dá 409.")


class ChecklistOrderIn(BaseModel):
    ids: list[UUID] = Field(
        description="Exatamente os itens vivos do dono, sem repetir e sem faltar, na nova ordem."
    )


class AttachmentLinkIn(BaseModel):
    """Um link. Sem campo de autoria: quem anexou é o perfil da sessão, e um `by` ou `profile` que
    venha no corpo é ignorado."""

    url: str = Field(description="Um endereço http ou https completo; até 2000 caracteres.")
    title: str | None = Field(default=None, description="Opcional, até 120 caracteres.")
    comment: str | None = Field(default=None, description="Opcional, até 500 caracteres.")


class AttachmentFileIn(BaseModel):
    """Um arquivo já enviado por `POST /files` (PDF ou imagem; o envio valida o tipo, o tamanho e a
    assinatura). Sem campo de autoria, como o link."""

    file_id: UUID
    title: str | None = Field(default=None, description="Opcional, até 120 caracteres.")
    comment: str | None = Field(default=None, description="Opcional, até 500 caracteres.")


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


class MilestoneWindowOut(BaseModel):
    start_before: int
    end_before: int
    unit: WindowUnit
    is_suggestion: bool = Field(description="Há janela e ninguém a editou: a sugestão genérica.")


class ChecklistItemOut(BaseModel):
    id: UUID
    text: str
    done: bool
    position: int = Field(description="Ordem no checklist, a partir de zero; pode ter buracos.")
    version: int = Field(description="A versão do item, própria: não é a do marco nem a da avulsa.")


class ChecklistProgressOut(BaseModel):
    done: int
    total: int


class AttachmentFileOut(BaseModel):
    id: UUID = Field(description="O id do arquivo, para baixar por `GET /files/{id}`.")
    name: str = Field(description="O nome do arquivo ao anexar (cópia).")
    content_type: str = Field(description="O tipo do arquivo ao anexar (cópia): PDF ou imagem.")
    size_bytes: int = Field(description="O tamanho em bytes ao anexar (cópia).")


class AttachmentOut(BaseModel):
    id: UUID
    kind: AttachmentKind
    title: str | None
    comment: str | None
    url: str | None = Field(description="O endereço do link; nulo se o anexo é um arquivo.")
    domain: str | None = Field(
        description=(
            "O domínio visível do link, derivado do endereço (sem `www.`); nunca lido da página."
        )
    )
    file: AttachmentFileOut | None = Field(description="O arquivo; nulo se o anexo é um link.")
    by: LoginProfile = Field(description="Quem anexou: o perfil da sessão, nunca do corpo.")
    at: dt.datetime = Field(description="O instante em que foi anexado.")
    can_remove: bool = Field(description="Derivado do perfil de quem lê: só o autor remove.")


class MilestoneOut(BaseModel):
    id: UUID
    title: str
    position: int
    responsible: ProfileKind
    note: str | None
    target_date: dt.date | None = Field(
        description=(
            "Só o prazo-alvo digitado à mão; nulo se não há. Nunca é o fim da janela calculada: "
            "esse vem em `effective_target`."
        )
    )
    state: MilestoneState
    optional: bool
    archived: bool
    overdue: bool
    blocked_by: list[BlockerOut]
    depends_on: list[DependencyOut]
    unlocks: list[MilestoneRefOut]
    warnings: list[WarningOut]
    category: CategoryLinkOut | None
    window: MilestoneWindowOut | None = Field(
        description="Os deslocamentos da janela, sempre que há janela; nulo se o marco não tem."
    )
    window_start: dt.date | None = Field(
        description="Início calculado da janela; só no Modo Com Data e com janela."
    )
    window_end: dt.date | None = Field(
        description="Fim calculado da janela; só no Modo Com Data e com janela."
    )
    effective_target: dt.date | None = Field(
        description="O prazo que vale: o manual (`target_date`) ou, sem ele, o fim da janela."
    )
    days_left: int | None = Field(
        description=(
            "Dias de hoje (Brasília) ao prazo efetivo; negativo é passado e 0 é hoje. Nulo se o "
            "marco está concluído, arquivado ou sem prazo efetivo."
        )
    )
    checklist: list[ChecklistItemOut] = Field(
        description="Os itens vivos do checklist, na ordem; não mudam o estado do marco."
    )
    checklist_progress: ChecklistProgressOut = Field(description='O "N de M" do checklist.')
    attachments: list[AttachmentOut] = Field(
        description=(
            "Os anexos vivos, na ordem em que foram anexados; não mudam o estado nem a `version`."
        )
    )
    version: int


class TaskOut(BaseModel):
    id: UUID
    title: str
    responsible: ProfileKind
    note: str | None
    target_date: dt.date | None
    state: TaskState
    overdue: bool = Field(description="Prazo vencido e não concluída; o dia é o de Brasília.")
    days_left: int | None = Field(
        description=(
            "Dias de hoje (Brasília) ao prazo; negativo é passado e 0 é hoje. Nulo se a avulsa "
            "está concluída ou sem prazo."
        )
    )
    checklist: list[ChecklistItemOut]
    checklist_progress: ChecklistProgressOut
    attachments: list[AttachmentOut]
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
    tasks: list[TaskOut] = Field(
        description=(
            "As avulsas vivas, fora das fases: concluídas e sem prazo por último, depois pelo "
            "prazo, pelo título e pelo id."
        )
    )
    category_options: list[CategoryOptionOut]
    has_exact_date: bool


class RestoreOut(BaseModel):
    schedule: ScheduleOut
    left_out: list[LeftOutOut]


class CreatedMilestoneOut(BaseModel):
    schedule: ScheduleOut
    milestone_id: UUID


class DateRangeOut(BaseModel):
    start: dt.date
    end: dt.date


class DateChangeOut(BaseModel):
    id: UUID
    title: str
    window_before: DateRangeOut | None
    window_after: DateRangeOut | None
    target_before: dt.date | None
    target_after: dt.date | None


class DatePreviewOut(BaseModel):
    mode_before: DateMode
    mode_after: DateMode
    changes: list[DateChangeOut] = Field(
        description=(
            "Marcos ativos e não concluídos, com janela e sem prazo manual, cujas datas "
            "calculadas mudam."
        )
    )
    manual_kept: int = Field(
        description="Marcos ativos e não concluídos com janela e prazo manual: o prazo não muda."
    )
    newly_overdue: int = Field(
        description="Marcos que passariam a Atrasado com a data hipotética e não estavam."
    )
