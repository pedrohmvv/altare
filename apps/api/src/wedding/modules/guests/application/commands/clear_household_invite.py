from dataclasses import dataclass
from uuid import UUID

from wedding.modules.guests.application.dto import GuestListDto
from wedding.modules.guests.application.list_map import build_guest_list, require_household
from wedding.modules.guests.application.ports import GuestsUnitOfWorkFactory
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.errors import VersionConflict


@dataclass(frozen=True)
class ClearHouseholdInviteCommand:
    household_id: UUID
    version: int


class ClearHouseholdInvite:
    def __init__(self, uow_factory: GuestsUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    def execute(self, command: ClearHouseholdInviteCommand, actor: Actor) -> GuestListDto:
        """Limpar o envio não reverte o status de ninguém (F-CNV-05, regra 3)."""
        with self._uow_factory(actor) as uow:
            household = require_household(uow.guests, command.household_id)
            if household.version != command.version:
                raise VersionConflict()
            if household.clear_invite():
                uow.commit()
            return build_guest_list(uow.guests)
