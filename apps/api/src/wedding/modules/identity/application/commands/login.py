import secrets
from dataclasses import dataclass
from datetime import datetime

from wedding.modules.identity.application.dto import CurrentUser, LoginResult
from wedding.modules.identity.application.ports import (
    IdentityUnitOfWork,
    LoginAttempts,
    PasswordHasher,
    UnitOfWorkFactory,
)
from wedding.modules.identity.domain.entities import User, UserSession
from wedding.modules.identity.domain.errors import InvalidCredentials
from wedding.modules.identity.domain.rules import LOGIN_WINDOW, login_retry_after, session_expired
from wedding.modules.identity.domain.value_objects import hash_token, normalize_username
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.clock import Clock
from wedding.shared_kernel.errors import TooManyAttempts
from wedding.shared_kernel.ids import IdGenerator


@dataclass(frozen=True)
class LoginCommand:
    username: str
    password: str
    ip: str
    previous_token: str | None


class Login:
    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        hasher: PasswordHasher,
        attempts: LoginAttempts,
        clock: Clock,
        ids: IdGenerator,
    ) -> None:
        self._uow_factory = uow_factory
        self._hasher = hasher
        self._attempts = attempts
        self._clock = clock
        self._ids = ids

    def execute(self, command: LoginCommand) -> LoginResult:
        now = self._clock.now()
        username = normalize_username(command.username)
        key = f"{username}|{command.ip}"
        self._refuse_while_blocked(key, now)

        with self._uow_factory() as uow:
            user = uow.users.get_by_username(username)
            if not self._credentials_match(user, command.password):
                self._attempts.add_failure(key, now)
                raise InvalidCredentials()
            assert user is not None
            self._attempts.clear(key)

            self._rehash_if_outdated(uow, user, command.password)
            self._drop_old_sessions(uow, command.previous_token, now)
            token = secrets.token_urlsafe(32)
            uow.sessions.add(
                UserSession(
                    id=self._ids.new_id(),
                    user_id=user.id,
                    token_hash=hash_token(token),
                    created_at=now,
                    last_seen_at=now,
                )
            )
            uow.commit()
            return LoginResult(token, CurrentUser(user.id, user.username, user.profile))

    def _refuse_while_blocked(self, key: str, now: datetime) -> None:
        recent = self._attempts.failures(key, since=now - LOGIN_WINDOW)
        retry_after = login_retry_after(recent, now)
        if retry_after is not None:
            raise TooManyAttempts(retry_after)

    def _credentials_match(self, user: User | None, password: str) -> bool:
        if user is None:
            self._hasher.verify_unknown_user(password)
            return False
        return self._hasher.verify(user.password_hash, password)

    def _rehash_if_outdated(self, uow: IdentityUnitOfWork, user: User, password: str) -> None:
        if self._hasher.needs_rehash(user.password_hash):
            uow.act_as(Actor(user_id=user.id, profile=user.profile))
            user.password_hash = self._hasher.hash(password)

    def _drop_old_sessions(
        self, uow: IdentityUnitOfWork, previous_token: str | None, now: datetime
    ) -> None:
        """Troca de usuário no mesmo computador: o login encerra a sessão do cookie que chegou
        (anti-fixação) e varre as vencidas de todos."""
        if previous_token is not None:
            previous = uow.sessions.get_by_token_hash(hash_token(previous_token))
            if previous is not None:
                uow.sessions.delete(previous)
        for session in uow.sessions.list_all():
            if session_expired(session, now):
                uow.sessions.delete(session)
