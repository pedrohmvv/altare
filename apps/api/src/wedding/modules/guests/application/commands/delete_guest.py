from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from wedding.modules.guests.application.dto import GuestListDto
from wedding.modules.guests.application.list_map import (
    build_guest_list,
    require_guest,
    require_household,
)
from wedding.modules.guests.application.ports import GuestsUnitOfWorkFactory
from wedding.modules.guests.domain.errors import CompanionChoiceRequired, LastGuestInHousehold
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.clock import Clock
from wedding.shared_kernel.errors import VersionConflict


class CompanionChoice(StrEnum):
    """O que fazer com o acompanhante ao excluir o titular (F-CNV-02, regra 4)."""

    DELETE = "delete"
    KEEP = "keep"


@dataclass(frozen=True)
class DeleteGuestCommand:
    guest_id: UUID
    version: int
    companion: CompanionChoice | None


class DeleteGuest:
    def __init__(self, uow_factory: GuestsUnitOfWorkFactory, clock: Clock) -> None:
        self._uow_factory = uow_factory
        self._clock = clock

    def execute(self, command: DeleteGuestCommand, actor: Actor) -> GuestListDto:
        """Exclusão lógica. Excluir o titular exige dizer o que fazer com o acompanhante: sair
        junto ou ficar como convidado comum, o que pede nome. O núcleo não fica sem pessoas."""
        with self._uow_factory(actor) as uow:
            guest = require_guest(uow.guests, command.guest_id)
            if guest.version != command.version:
                raise VersionConflict()
            removed = [guest]
            companion = None if guest.is_companion else uow.guests.companion_of(guest.id)
            if companion is not None:
                if command.companion is None:
                    raise CompanionChoiceRequired()
                if command.companion is CompanionChoice.DELETE:
                    removed.append(companion)
                else:
                    companion.unlink_companion()
            household = require_household(uow.guests, guest.household_id)
            gone = {person.id for person in removed}
            if not [m for m in uow.guests.guests_of(household.id) if m.id not in gone]:
                raise LastGuestInHousehold()
            now = self._clock.now()
            for person in removed:
                person.delete(now, actor.user_id)
            household.touch_members()
            uow.commit()
            return build_guest_list(uow.guests)
