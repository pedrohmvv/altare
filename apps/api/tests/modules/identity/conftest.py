import copy
from datetime import datetime, timedelta
from uuid import UUID

import pytest

from wedding.modules.identity.domain.entities import User, UserSession
from wedding.modules.identity.domain.value_objects import hash_token
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.profile import ProfileKind

SENHA = "senha-exemplo-12345"


class _Store:
    def __init__(self) -> None:
        self.users: dict[UUID, User] = {}
        self.sessions: dict[UUID, UserSession] = {}
        self.commits = 0
        self.actors: list[Actor] = []


class _Users:
    def __init__(self, users: dict[UUID, User]) -> None:
        self._users = users

    def add(self, user: User) -> None:
        self._users[user.id] = user

    def get(self, user_id: UUID) -> User | None:
        return self._users.get(user_id)

    def get_by_username(self, username: str) -> User | None:
        return next((u for u in self._users.values() if u.username == username), None)

    def get_by_profile(self, profile: ProfileKind) -> User | None:
        return next((u for u in self._users.values() if u.profile is profile), None)


class _Sessions:
    def __init__(self, sessions: dict[UUID, UserSession]) -> None:
        self._sessions = sessions

    def add(self, session: UserSession) -> None:
        self._sessions[session.id] = session

    def get_by_token_hash(self, token_hash: str) -> UserSession | None:
        return next((s for s in self._sessions.values() if s.token_hash == token_hash), None)

    def list_all(self) -> list[UserSession]:
        return list(self._sessions.values())

    def delete(self, session: UserSession) -> None:
        self._sessions.pop(session.id, None)

    def delete_for_user(self, user_id: UUID) -> None:
        for s in [s for s in self._sessions.values() if s.user_id == user_id]:
            del self._sessions[s.id]


class _UnitOfWork:
    """Transação de mentira: trabalha numa cópia e só a publica no commit."""

    def __init__(self, store: _Store) -> None:
        self._store = store
        self._users = copy.deepcopy(store.users)
        self._sessions = copy.deepcopy(store.sessions)
        self.users = _Users(self._users)
        self.sessions = _Sessions(self._sessions)

    def __enter__(self) -> "_UnitOfWork":
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def commit(self) -> None:
        self._store.users = self._users
        self._store.sessions = self._sessions
        self._store.commits += 1

    def rollback(self) -> None:
        return None

    def act_as(self, actor: Actor) -> None:
        self._store.actors.append(actor)


class _Hasher:
    def __init__(self) -> None:
        self.stale: set[str] = set()
        self.verify_calls = 0
        self.unknown_user_calls = 0

    def hash(self, password: str) -> str:
        return f"hash::{password}"

    def verify(self, password_hash: str, password: str) -> bool:
        self.verify_calls += 1
        return password_hash == f"hash::{password}"

    def needs_rehash(self, password_hash: str) -> bool:
        return password_hash in self.stale

    def verify_unknown_user(self, password: str) -> None:
        self.unknown_user_calls += 1


class _Attempts:
    def __init__(self) -> None:
        self.data: dict[str, list[datetime]] = {}

    def failures(self, key: str, since: datetime) -> list[datetime]:
        return [at for at in self.data.get(key, []) if at >= since]

    def add_failure(self, key: str, at: datetime) -> None:
        self.data.setdefault(key, []).append(at)

    def clear(self, key: str) -> None:
        self.data.pop(key, None)


class _Ids:
    def __init__(self) -> None:
        self._next = 0

    def new_id(self) -> UUID:
        self._next += 1
        return UUID(int=self._next)


class World:
    """Tudo o que os casos de uso de identidade precisam, em memória."""

    def __init__(self, clock) -> None:
        self.clock = clock
        self.password = SENHA
        self.store = _Store()
        self.hasher = _Hasher()
        self.attempts = _Attempts()
        self.ids = _Ids()

    def uow_factory(self) -> _UnitOfWork:
        return _UnitOfWork(self.store)

    def add_user(
        self, username: str = "exemplo.noivo", profile: ProfileKind = ProfileKind.NOIVO
    ) -> User:
        user = User(
            id=self.ids.new_id(),
            username=username,
            profile=profile,
            password_hash=self.hasher.hash(SENHA),
        )
        self.store.users[user.id] = user
        return user

    def add_session(
        self,
        user: User,
        token: str = "token-exemplo",
        created_ago: timedelta = timedelta(0),
        seen_ago: timedelta = timedelta(0),
    ) -> UserSession:
        now = self.clock.now()
        session = UserSession(
            id=self.ids.new_id(),
            user_id=user.id,
            token_hash=hash_token(token),
            created_at=now - created_ago,
            last_seen_at=now - seen_ago,
        )
        self.store.sessions[session.id] = session
        return session


@pytest.fixture
def world(clock) -> World:
    return World(clock)
