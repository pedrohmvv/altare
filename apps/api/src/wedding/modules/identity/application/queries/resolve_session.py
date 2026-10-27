from wedding.modules.identity.application.ports import UnitOfWorkFactory
from wedding.modules.identity.domain.rules import session_expired, should_touch
from wedding.modules.identity.domain.value_objects import hash_token
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.clock import Clock


class ResolveSession:
    def __init__(self, uow_factory: UnitOfWorkFactory, clock: Clock) -> None:
        self._uow_factory = uow_factory
        self._clock = clock

    def execute(self, token: str) -> Actor | None:
        """Token do cookie → quem age. Sessão vencida, ou de usuário que sumiu, é apagada."""
        now = self._clock.now()
        with self._uow_factory() as uow:
            session = uow.sessions.get_by_token_hash(hash_token(token))
            if session is None:
                return None
            user = uow.users.get(session.user_id)
            if user is None or session_expired(session, now):
                uow.sessions.delete(session)
                uow.commit()
                return None
            if should_touch(session, now):
                session.last_seen_at = now
                uow.commit()
            return Actor(user_id=user.id, profile=user.profile)
