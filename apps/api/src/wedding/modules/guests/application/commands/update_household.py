from dataclasses import dataclass
from uuid import UUID

from wedding.modules.guests.application.dto import GuestListDto
from wedding.modules.guests.application.fields import HouseholdFields
from wedding.modules.guests.application.list_map import build_guest_list, require_household
from wedding.modules.guests.application.ports import GuestsUnitOfWorkFactory
from wedding.modules.guests.domain.errors import DuplicateHouseholdName
from wedding.modules.guests.domain.values import name_key
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.errors import VersionConflict


@dataclass(frozen=True)
class UpdateHouseholdCommand:
    household_id: UUID
    version: int
    fields: HouseholdFields


class UpdateHousehold:
    def __init__(self, uow_factory: GuestsUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    def execute(self, command: UpdateHouseholdCommand, actor: Actor) -> GuestListDto:
        fields = command.fields
        with self._uow_factory(actor) as uow:
            household = require_household(uow.guests, command.household_id)
            if household.version != command.version:
                raise VersionConflict()
            changed = household.update(
                name=fields.name,
                side=fields.side,
                street=fields.street,
                number=fields.number,
                complement=fields.complement,
                district=fields.district,
                city=fields.city,
                state=fields.state,
                postal_code=fields.postal_code,
                note=fields.note,
            )
            if changed:
                if uow.guests.household_name_taken(name_key(fields.name), excluding=household.id):
                    raise DuplicateHouseholdName()
                uow.commit()
            return build_guest_list(uow.guests)
