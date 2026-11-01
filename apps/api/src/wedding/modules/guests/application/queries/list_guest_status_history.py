from uuid import UUID

from wedding.modules.guests.application.dto import GuestStatusChangeDto
from wedding.modules.guests.application.list_map import require_guest
from wedding.modules.guests.application.ports import GuestsUnitOfWorkFactory
from wedding.shared_kernel.actor import Actor


class ListGuestStatusHistory:
    def __init__(self, uow_factory: GuestsUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    def execute(self, guest_id: UUID, actor: Actor) -> list[GuestStatusChangeDto]:
        with self._uow_factory(actor) as uow:
            require_guest(uow.guests, guest_id)
            return uow.guests.status_history(guest_id)
