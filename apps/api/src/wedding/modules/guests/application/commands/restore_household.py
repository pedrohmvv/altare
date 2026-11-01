from dataclasses import dataclass
from uuid import UUID

from wedding.modules.guests.application.dto import GuestListDto
from wedding.modules.guests.application.list_map import build_guest_list
from wedding.modules.guests.application.ports import GuestsUnitOfWorkFactory
from wedding.modules.guests.domain.errors import DuplicateHouseholdName
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.errors import NotFound


@dataclass(frozen=True)
class RestoreHouseholdCommand:
    household_id: UUID


class RestoreHousehold:
    def __init__(self, uow_factory: GuestsUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    def execute(self, command: RestoreHouseholdCommand, actor: Actor) -> GuestListDto:
        with self._uow_factory(actor) as uow:
            household = uow.guests.get_household(command.household_id, include_deleted=True)
            if household is None or household.deleted_at is None:
                raise NotFound()
            if uow.guests.household_name_taken(household.name_key):
                raise DuplicateHouseholdName()
            household.restore()
            uow.commit()
            return build_guest_list(uow.guests)
