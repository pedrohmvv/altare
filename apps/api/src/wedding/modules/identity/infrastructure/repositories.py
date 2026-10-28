from uuid import UUID

from sqlalchemy import ColumnElement, delete, select
from sqlalchemy.orm import Session

from wedding.modules.identity.domain.entities import User, UserSession
from wedding.modules.identity.infrastructure.tables import user_sessions, users
from wedding.shared_kernel.profile import ProfileKind


class SqlUserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, user: User) -> None:
        self._session.add(user)

    def get(self, user_id: UUID) -> User | None:
        return self._live_user(users.c.id == user_id)

    def get_by_username(self, username: str) -> User | None:
        return self._live_user(users.c.username == username)

    def get_by_profile(self, profile: ProfileKind) -> User | None:
        return self._live_user(users.c.profile == profile)

    def _live_user(self, condition: ColumnElement[bool]) -> User | None:
        """Todo usuário é lido com a exclusão lógica filtrada (architecture.md §10)."""
        query = select(User).where(users.c.deleted_at.is_(None), condition)
        return self._session.execute(query).scalar_one_or_none()


class SqlSessionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, session: UserSession) -> None:
        self._session.add(session)

    def get_by_token_hash(self, token_hash: str) -> UserSession | None:
        query = select(UserSession).where(user_sessions.c.token_hash == token_hash)
        return self._session.execute(query).scalar_one_or_none()

    def list_all(self) -> list[UserSession]:
        return list(self._session.execute(select(UserSession)).scalars())

    def delete(self, session: UserSession) -> None:
        self._session.delete(session)

    def delete_for_user(self, user_id: UUID) -> None:
        self._session.execute(delete(user_sessions).where(user_sessions.c.user_id == user_id))
