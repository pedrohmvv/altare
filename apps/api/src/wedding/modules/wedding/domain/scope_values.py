from enum import StrEnum

from wedding.modules.wedding.domain.errors import InvalidScopeValue

MAX_NAME = 60
MAX_REASON = 300
MAX_NOTE = 500
MAX_ESTIMATE_CENTS = 10**12


class ScopeStatus(StrEnum):
    IN_DISCUSSION = "Em discussão"
    ESSENTIAL = "Entra (Essencial)"
    MAYBE = "Talvez (Se couber)"
    OUT = "Fica de fora"


class Priority(StrEnum):
    WANT_A_LOT = "Quero muito"
    IF_FITS = "Se couber"
    DISPENSE = "Dispenso"


class Origin(StrEnum):
    CATALOG = "catalogo"
    COUPLE = "casal"


def _collapse(text: str) -> str:
    return " ".join(text.split())


def name_key(name: str) -> str:
    """A chave de unicidade do nome: sem diferenciar maiúsculas nem espaços repetidos (F-PLN-02,
    regra 3). Acentos continuam diferentes, como a regra pede."""
    return _collapse(name).casefold()


def clean_name(name: str) -> str:
    collapsed = _collapse(name)
    if not collapsed or len(collapsed) > MAX_NAME:
        raise InvalidScopeValue()
    return collapsed


def clean_estimate(cents: int | None) -> int | None:
    """Vazio é `None`, nunca zero (F-PLN-05): uma estimativa é um valor positivo."""
    if cents is None:
        return None
    if isinstance(cents, bool) or not isinstance(cents, int):
        raise InvalidScopeValue()
    if not 0 < cents <= MAX_ESTIMATE_CENTS:
        raise InvalidScopeValue()
    return cents


def _clean_text(text: str | None, limit: int) -> str | None:
    cleaned = (text or "").strip()
    if len(cleaned) > limit:
        raise InvalidScopeValue()
    return cleaned or None


def clean_reason(reason: str | None) -> str | None:
    return _clean_text(reason, MAX_REASON)


def clean_note(note: str | None) -> str | None:
    return _clean_text(note, MAX_NOTE)
