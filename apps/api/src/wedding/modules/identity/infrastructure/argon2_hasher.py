from contextlib import suppress

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

_UNKNOWN_USER_PASSWORD = "senha-que-nenhum-usuario-tem"


class Argon2PasswordHasher:
    """Argon2id com os parâmetros padrão da biblioteca (RFC 9106)."""

    def __init__(self) -> None:
        self._argon2 = PasswordHasher()
        # Calculado já na criação, para a primeira tentativa com usuário inexistente não ser a
        # única mais lenta.
        self._unknown_user_hash = self._argon2.hash(_UNKNOWN_USER_PASSWORD)

    def hash(self, password: str) -> str:
        return self._argon2.hash(password)

    def verify(self, password_hash: str, password: str) -> bool:
        try:
            return self._argon2.verify(password_hash, password)
        except (VerificationError, InvalidHashError):
            return False

    def needs_rehash(self, password_hash: str) -> bool:
        return self._argon2.check_needs_rehash(password_hash)

    def verify_unknown_user(self, password: str) -> None:
        with suppress(VerificationError, InvalidHashError):
            self._argon2.verify(self._unknown_user_hash, password)
