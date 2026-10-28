import hashlib
import re

from wedding.modules.identity.domain.errors import InvalidUsername, WeakPassword

_USERNAME = re.compile(r"[a-z0-9._-]{3,32}")
PASSWORD_MIN_LENGTH = 12
PASSWORD_MAX_LENGTH = 128


def normalize_username(raw: str) -> str:
    return raw.strip().lower()


def validate_username(username: str) -> None:
    """Valida o usuário já normalizado: de 3 a 32 caracteres entre `a-z`, `0-9`, `.`, `_` e `-`."""
    if _USERNAME.fullmatch(username) is None:
        raise InvalidUsername()


def validate_password(password: str) -> None:
    """De 12 a 128 caracteres, sem regra de composição; o teto evita abuso do Argon2."""
    if not PASSWORD_MIN_LENGTH <= len(password) <= PASSWORD_MAX_LENGTH:
        raise WeakPassword()


def hash_token(token: str) -> str:
    """O banco guarda só o SHA-256 do token: um vazamento do banco não entrega sessões."""
    return hashlib.sha256(token.encode()).hexdigest()
