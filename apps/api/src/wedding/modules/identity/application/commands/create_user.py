from dataclasses import dataclass

from wedding.modules.identity.application.dto import CurrentUser
from wedding.modules.identity.application.ports import PasswordHasher, UnitOfWorkFactory
from wedding.modules.identity.domain.entities import User
from wedding.modules.identity.domain.errors import DuplicateUsername, ProfileTaken
from wedding.modules.identity.domain.value_objects import (
    normalize_username,
    validate_password,
    validate_username,
)
from wedding.shared_kernel.ids import IdGenerator
from wedding.shared_kernel.profile import ProfileKind


@dataclass(frozen=True)
class CreateUserCommand:
    username: str
    profile: ProfileKind
    password: str


class CreateUser:
    def __init__(
        self, uow_factory: UnitOfWorkFactory, hasher: PasswordHasher, ids: IdGenerator
    ) -> None:
        self._uow_factory = uow_factory
        self._hasher = hasher
        self._ids = ids

    def execute(self, command: CreateUserCommand) -> CurrentUser:
        username = normalize_username(command.username)
        validate_username(username)
        validate_password(command.password)

        with self._uow_factory() as uow:
            if uow.users.get_by_username(username) is not None:
                raise DuplicateUsername()
            if uow.users.get_by_profile(command.profile) is not None:
                raise ProfileTaken()
            user = User(
                id=self._ids.new_id(),
                username=username,
                profile=command.profile,
                password_hash=self._hasher.hash(command.password),
            )
            uow.users.add(user)
            uow.commit()
            return CurrentUser(user.id, user.username, user.profile)
