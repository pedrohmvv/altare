from dataclasses import dataclass
from uuid import UUID

from wedding.modules.guests.application.dto import GuestListDto
from wedding.modules.guests.application.fields import GuestFields
from wedding.modules.guests.application.list_map import build_guest_list, require_guest
from wedding.modules.guests.application.ports import GuestsUnitOfWorkFactory
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.errors import VersionConflict


@dataclass(frozen=True)
class UpdateGuestCommand:
    guest_id: UUID
    version: int
    fields: GuestFields
    decline_reason: str | None


class UpdateGuest:
    def __init__(self, uow_factory: GuestsUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    def execute(self, command: UpdateGuestCommand, actor: Actor) -> GuestListDto:
        fields = command.fields
        with self._uow_factory(actor) as uow:
            guest = require_guest(uow.guests, command.guest_id)
            if guest.version != command.version:
                raise VersionConflict()
            changed = guest.update(
                name=fields.name,
                band=fields.band,
                age=fields.age,
                probability=fields.probability,
                dietary_restriction=fields.dietary_restriction,
                note=fields.note,
                phone=fields.phone,
                email=fields.email,
                decline_reason=command.decline_reason,
            )
            if changed:
                uow.commit()
            return build_guest_list(uow.guests)
