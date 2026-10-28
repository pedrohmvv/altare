from dataclasses import dataclass

from wedding.modules.identity.application.ports import PasswordHasher, UnitOfWorkFactory
from wedding.modules.identity.domain.value_objects import normalize_username, validate_password
from wedding.shared_kernel.errors import NotFound


@dataclass(frozen=True)
class SetPasswordCommand:
    username: str
    password: str


class SetPassword:
    def __init__(self, uow_factory: UnitOfWorkFactory, hasher: PasswordHasher) -> None:
        self._uow_factory = uow_factory
        self._hasher = hasher

    def execute(self, command: SetPasswordCommand) -> None:
        """Sem recuperação de senha pela tela: quem troca é a CLI, e a troca derruba as sessões."""
        validate_password(command.password)
        with self._uow_factory() as uow:
            user = uow.users.get_by_username(normalize_username(command.username))
            if user is None:
                raise NotFound()
            user.password_hash = self._hasher.hash(command.password)
            uow.sessions.delete_for_user(user.id)
            uow.commit()
