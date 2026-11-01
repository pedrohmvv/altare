from dataclasses import dataclass
from uuid import UUID

from wedding.modules.guests.application.dto import GuestListDto
from wedding.modules.guests.application.list_map import (
    build_guest_list,
    require_guest,
    require_household,
)
from wedding.modules.guests.application.ports import GuestsUnitOfWorkFactory
from wedding.modules.guests.domain.errors import CompanionMovesWithHolder, LastGuestInHousehold
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.errors import VersionConflict


@dataclass(frozen=True)
class MoveGuestCommand:
    guest_id: UUID
    household_id: UUID
    version: int


class MoveGuest:
    def __init__(self, uow_factory: GuestsUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    def execute(self, command: MoveGuestCommand, actor: Actor) -> GuestListDto:
        """Mover entre núcleos é permitido (F-CNV-01, regra 1). O acompanhante vai junto com o
        titular e não se move sozinho; o núcleo de origem não pode ficar sem pessoas."""
        with self._uow_factory(actor) as uow:
            guest = require_guest(uow.guests, command.guest_id)
            if guest.version != command.version:
                raise VersionConflict()
            if guest.is_companion:
                raise CompanionMovesWithHolder()
            target = require_household(uow.guests, command.household_id)
            if target.id == guest.household_id:
                return build_guest_list(uow.guests)
            source = require_household(uow.guests, guest.household_id)
            moving = [guest]
            companion = uow.guests.companion_of(guest.id)
            if companion is not None:
                moving.append(companion)
            staying = [
                m for m in uow.guests.guests_of(source.id) if m.id not in {x.id for x in moving}
            ]
            if not staying:
                raise LastGuestInHousehold()
            position = uow.guests.next_position(target.id)
            for offset, person in enumerate(moving):
                person.move_to(target.id, position + offset)
            source.touch_members()
            uow.commit()
            return build_guest_list(uow.guests)
