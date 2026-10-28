from dataclasses import dataclass
from uuid import UUID

from wedding.modules.guests.application.dto import GuestListDto
from wedding.modules.guests.application.fields import GuestFields
from wedding.modules.guests.application.list_map import build_guest_list, require_household
from wedding.modules.guests.application.new_guest import build_guest
from wedding.modules.guests.application.ports import GuestsUnitOfWorkFactory
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.ids import IdGenerator


@dataclass(frozen=True)
class AddGuestCommand:
    household_id: UUID
    guest: GuestFields


class AddGuest:
    def __init__(self, uow_factory: GuestsUnitOfWorkFactory, ids: IdGenerator) -> None:
        self._uow_factory = uow_factory
        self._ids = ids

    def execute(self, command: AddGuestCommand, actor: Actor) -> GuestListDto:
        """Acrescenta uma pessoa ao fim do núcleo (o cadastro rápido, F-CNV-01, regra 3)."""
        with self._uow_factory(actor) as uow:
            household = require_household(uow.guests, command.household_id)
            guest = build_guest(
                self._ids.new_id(),
                household.id,
                uow.guests.next_position(household.id),
                command.guest,
            )
            uow.guests.add_guest(guest)
            uow.commit()
            return build_guest_list(uow.guests)
