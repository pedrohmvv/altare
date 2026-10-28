from uuid import UUID

from wedding.modules.identity.application.dto import CurrentUser
from wedding.modules.identity.application.ports import UnitOfWorkFactory
from wedding.shared_kernel.errors import NotFound


class GetCurrentUser:
    def __init__(self, uow_factory: UnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    def execute(self, user_id: UUID) -> CurrentUser:
        with self._uow_factory() as uow:
            user = uow.users.get(user_id)
            if user is None:
                raise NotFound()
            return CurrentUser(user.id, user.username, user.profile)
