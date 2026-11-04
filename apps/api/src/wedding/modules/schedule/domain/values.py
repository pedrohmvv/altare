from datetime import date
from enum import StrEnum

from wedding.modules.schedule.domain.errors import (
    ChecklistTextRequired,
    InvalidScheduleValue,
    MilestoneTitleRequired,
    PhaseTitleRequired,
    TaskTitleRequired,
)

MAX_NOTE = 500
MAX_TITLE = 120
MAX_PHASE_TITLE = 60
MIN_YEAR = 2000
MAX_YEAR = 2100
MAX_CHECKLIST_TEXT = 200
MAX_CHECKLIST_ITEMS = 50


class ManualState(StrEnum):
    """O que o casal marca à mão (F-CRN-03). Sem marca, o estado é derivado."""

    IN_PROGRESS = "Em andamento"
    DONE = "Concluído"


class TaskState(StrEnum):
    """O estado da tarefa avulsa (F-CRN-06): todo estado vale a qualquer momento, e reabrir é voltar
    a `A fazer`. Note o feminino de `Concluída`, diferente do `Concluído` do marco."""

    TODO = "A fazer"
    IN_PROGRESS = "Em andamento"
    DONE = "Concluída"


class OwnerKind(StrEnum):
    """Quem pode ter checklist (F-CRN-07, regra 1); o valor é o segmento da rota."""

    MILESTONE = "milestones"
    TASK = "tasks"


class MilestoneState(StrEnum):
    """O estado que a tela mostra: o manual quando há, senão o derivado (F-CRN-03)."""

    BLOCKED = "Bloqueado"
    UNLOCKED = "Destravado"
    IN_PROGRESS = "Em andamento"
    DONE = "Concluído"


class Standing(StrEnum):
    """Como a categoria ligada ao marco está no Mapa de Escopo, já com a visibilidade dobrada: a
    categoria oculta, de grupo oculto ou excluída conta como `Fica de fora` (F-CRN-04, regra 3)."""

    ENTERS = "Entra"
    MAYBE = "Talvez"
    IN_DISCUSSION = "Em discussão"
    OUT = "Fica de fora"


class BlockerKind(StrEnum):
    CATEGORY_UNCLASSIFIED = "category"
    MILESTONE = "milestone"


def clean_note(note: str | None) -> str | None:
    """Apara o texto; em branco vira ausência. Passar do limite é erro, não corte silencioso."""
    cleaned = (note or "").strip()
    if len(cleaned) > MAX_NOTE:
        raise InvalidScheduleValue()
    return cleaned or None


def clean_target_date(target: date | None) -> date | None:
    if target is not None and not MIN_YEAR <= target.year <= MAX_YEAR:
        raise InvalidScheduleValue()
    return target


def clean_milestone_title(title: str) -> str:
    cleaned = title.strip()
    if not cleaned:
        raise MilestoneTitleRequired()
    if len(cleaned) > MAX_TITLE:
        raise InvalidScheduleValue()
    return cleaned


def clean_phase_title(title: str) -> str:
    cleaned = title.strip()
    if not cleaned:
        raise PhaseTitleRequired()
    if len(cleaned) > MAX_PHASE_TITLE:
        raise InvalidScheduleValue()
    return cleaned


def clean_task_title(title: str) -> str:
    cleaned = title.strip()
    if not cleaned:
        raise TaskTitleRequired()
    if len(cleaned) > MAX_TITLE:
        raise InvalidScheduleValue()
    return cleaned


def clean_checklist_text(text: str) -> str:
    cleaned = text.strip()
    if not cleaned:
        raise ChecklistTextRequired()
    if len(cleaned) > MAX_CHECKLIST_TEXT:
        raise InvalidScheduleValue()
    return cleaned
