from wedding.modules.identity.application.ports import UnitOfWorkFactory
from wedding.modules.identity.domain.value_objects import hash_token


class Logout:
    def __init__(self, uow_factory: UnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    def execute(self, token: str | None) -> None:
        """Idempotente: sair sem sessão, ou com uma que já não existe, não é erro."""
        if token is None:
            return
        with self._uow_factory() as uow:
            session = uow.sessions.get_by_token_hash(hash_token(token))
            if session is not None:
                uow.sessions.delete(session)
                uow.commit()
