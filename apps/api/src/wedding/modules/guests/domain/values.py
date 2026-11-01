from enum import StrEnum

from wedding.modules.guests.domain.errors import GuestNameRequired, InvalidGuestValue

MAX_NAME = 80
MAX_NOTE = 500
MAX_DIETARY = 120
MAX_REASON = 300
MAX_STREET = 120
MAX_NUMBER = 20
MAX_SHORT = 60
MAX_CHILD_AGE = 17

_STATES = frozenset(
    [
        "AC",
        "AL",
        "AP",
        "AM",
        "BA",
        "CE",
        "DF",
        "ES",
        "GO",
        "MA",
        "MT",
        "MS",
        "MG",
        "PA",
        "PB",
        "PR",
        "PE",
        "PI",
        "RJ",
        "RN",
        "RS",
        "RO",
        "RR",
        "SC",
        "SP",
        "SE",
        "TO",
    ]
)


class Side(StrEnum):
    NOIVO = "Noivo"
    NOIVA = "Noiva"
    COMUM = "Comum"


class AgeBand(StrEnum):
    ADULT = "Adulto"
    PAYING_CHILD = "Criança pagante"
    EXEMPT_CHILD = "Criança isenta"


class Probability(StrEnum):
    CERTAIN = "Certeza"
    PROBABLE = "Provável"
    PHASE_2 = "Fase 2"


class GuestStatus(StrEnum):
    DRAFT = "Rascunho"
    INVITED = "Convidado"
    CONFIRMED = "Confirmado"
    DECLINED = "Não irá"


def _collapse(text: str) -> str:
    return " ".join(text.split())


def name_key(name: str) -> str:
    """A chave de unicidade do nome do núcleo: sem diferenciar maiúsculas nem espaços repetidos
    (F-CNV-01). Acentos continuam diferentes, como no Mapa de Escopo (`D-068`)."""
    return _collapse(name).casefold()


def clean_household_name(name: str) -> str:
    collapsed = _collapse(name)
    if not collapsed or len(collapsed) > MAX_NAME:
        raise InvalidGuestValue()
    return collapsed


def clean_guest_name(name: str | None, *, required: bool) -> str | None:
    """O nome é obrigatório, exceto no acompanhante a confirmar (F-CNV-02)."""
    collapsed = _collapse(name or "")
    if len(collapsed) > MAX_NAME:
        raise InvalidGuestValue()
    if not collapsed:
        if required:
            raise GuestNameRequired()
        return None
    return collapsed


def clean_text(text: str | None, limit: int) -> str | None:
    cleaned = (text or "").strip()
    if len(cleaned) > limit:
        raise InvalidGuestValue()
    return cleaned or None


def clean_state(raw: str | None) -> str | None:
    state = (raw or "").strip().upper()
    if not state:
        return None
    if state not in _STATES:
        raise InvalidGuestValue()
    return state


def clean_age(age: int | None, band: AgeBand) -> int | None:
    """A idade só vale para criança e é só um dado: nunca decide a faixa (F-CNV-03, regra 1)."""
    if age is None:
        return None
    if isinstance(age, bool) or not isinstance(age, int) or band is AgeBand.ADULT:
        raise InvalidGuestValue()
    if not 0 <= age <= MAX_CHILD_AGE:
        raise InvalidGuestValue()
    return age
