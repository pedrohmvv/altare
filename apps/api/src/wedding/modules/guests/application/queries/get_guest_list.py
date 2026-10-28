from wedding.modules.guests.application.dto import GuestListDto
from wedding.modules.guests.application.list_map import build_guest_list
from wedding.modules.guests.application.ports import GuestsUnitOfWorkFactory
from wedding.shared_kernel.actor import Actor


class GetGuestList:
    def __init__(self, uow_factory: GuestsUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    def execute(self, actor: Actor) -> GuestListDto:
        with self._uow_factory(actor) as uow:
            return build_guest_list(uow.guests)
