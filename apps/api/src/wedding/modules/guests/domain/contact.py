import re

from wedding.modules.guests.domain.errors import InvalidEmail, InvalidGuestValue, InvalidPhone

MAX_EMAIL = 254

_PHONE_CHARS = frozenset("0123456789 ()-+.")
_EMAIL = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+", re.ASCII)
_POSTAL_CODE = re.compile(r"\d{5}-?\d{3}", re.ASCII)


def normalize_phone(raw: str | None) -> str | None:
    """Guarda só os dígitos nacionais (DDD e número, 10 ou 11), tirando o `+55`, o `55` e o `0` do
    tronco (F-CNV-01). Vazio é `None`; o que não é um telefone brasileiro é recusado."""
    text = (raw or "").strip()
    if not text:
        return None
    if any(char not in _PHONE_CHARS for char in text):
        raise InvalidPhone()
    digits = "".join(char for char in text if char.isdigit())
    digits = digits.removeprefix("0")
    if digits.startswith("55") and len(digits) in (12, 13):
        digits = digits[2:]
    if len(digits) not in (10, 11) or digits[0] == "0" or digits[1] == "0":
        raise InvalidPhone()
    # Celular tem 11 dígitos e começa em 9; fixo tem 10 e começa de 2 a 5 (o 8 dígitos antigo, de
    # 6 a 9, não existe mais).
    third = digits[2]
    if (len(digits) == 11 and third != "9") or (len(digits) == 10 and third not in "2345"):
        raise InvalidPhone()
    return digits


def whatsapp_url(phone: str | None) -> str | None:
    """O link `wa.me` só existe para celular válido (F-CNV-01): fixo não recebe WhatsApp."""
    if phone is None or len(phone) != 11:
        return None
    return f"https://wa.me/55{phone}"


def format_phone(phone: str) -> str:
    split = 7 if len(phone) == 11 else 6
    return f"({phone[:2]}) {phone[2:split]}-{phone[split:]}"


def clean_email(raw: str | None) -> str | None:
    """Só o formato é conferido (F-CNV-01): nada de consultar domínio nem caixa."""
    text = (raw or "").strip()
    if not text:
        return None
    if len(text) > MAX_EMAIL or any(ord(char) < 32 for char in text):
        raise InvalidEmail()
    domain = text.rpartition("@")[2]
    if (
        not _EMAIL.fullmatch(text)
        or domain.startswith(".")
        or domain.endswith(".")
        or ".." in domain
    ):
        raise InvalidEmail()
    return text


def clean_postal_code(raw: str | None) -> str | None:
    """O CEP só é validado no formato, 8 dígitos com ou sem hífen (F-CNV-01)."""
    text = (raw or "").strip()
    if not text:
        return None
    if not _POSTAL_CODE.fullmatch(text):
        raise InvalidGuestValue()
    return text.replace("-", "")


def format_postal_code(postal_code: str) -> str:
    return f"{postal_code[:5]}-{postal_code[5:]}"
