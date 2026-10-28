from collections.abc import Callable
from datetime import datetime
from types import TracebackType
from typing import Protocol, Self
from uuid import UUID

from wedding.modules.identity.domain.entities import User, UserSession
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.profile import ProfileKind


class UserRepository(Protocol):
    def add(self, user: User) -> None: ...

    def get(self, user_id: UUID) -> User | None: ...

    def get_by_username(self, username: str) -> User | None: ...

    def get_by_profile(self, profile: ProfileKind) -> User | None: ...


class SessionRepository(Protocol):
    def add(self, session: UserSession) -> None: ...

    def get_by_token_hash(self, token_hash: str) -> UserSession | None: ...

    def list_all(self) -> list[UserSession]: ...

    def delete(self, session: UserSession) -> None: ...

    def delete_for_user(self, user_id: UUID) -> None: ...


class IdentityUnitOfWork(Protocol):
    @property
    def users(self) -> UserRepository: ...

    @property
    def sessions(self) -> SessionRepository: ...

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...

    def act_as(self, actor: Actor) -> None: ...


# Uma UnitOfWork nova por execução: a instância guarda a sessão do banco, e os casos de uso
# atendem várias requisições ao mesmo tempo.
UnitOfWorkFactory = Callable[[], IdentityUnitOfWork]


class PasswordHasher(Protocol):
    def hash(self, password: str) -> str: ...

    def verify(self, password_hash: str, password: str) -> bool: ...

    def needs_rehash(self, password_hash: str) -> bool: ...

    def verify_unknown_user(self, password: str) -> None:
        """Gasta o mesmo trabalho de uma verificação real, para o usuário inexistente não se
        distinguir pelo tempo de resposta."""
        ...


class LoginAttempts(Protocol):
    def failures(self, key: str, since: datetime) -> list[datetime]: ...

    def add_failure(self, key: str, at: datetime) -> None: ...

    def clear(self, key: str) -> None: ...
