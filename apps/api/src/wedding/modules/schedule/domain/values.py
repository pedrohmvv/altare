from datetime import date
from enum import StrEnum

from wedding.modules.schedule.domain.errors import InvalidScheduleValue

MAX_NOTE = 500
MIN_YEAR = 2000
MAX_YEAR = 2100


class ManualState(StrEnum):
    """O que o casal marca à mão (F-CRN-03). Sem marca, o estado é derivado."""

    IN_PROGRESS = "Em andamento"
    DONE = "Concluído"


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
