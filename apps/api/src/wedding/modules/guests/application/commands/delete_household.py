from dataclasses import dataclass
from uuid import UUID

from wedding.modules.guests.application.dto import GuestListDto
from wedding.modules.guests.application.list_map import build_guest_list, require_household
from wedding.modules.guests.application.ports import GuestsUnitOfWorkFactory
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.clock import Clock
from wedding.shared_kernel.errors import VersionConflict


@dataclass(frozen=True)
class DeleteHouseholdCommand:
    household_id: UUID
    version: int


class DeleteHousehold:
    def __init__(self, uow_factory: GuestsUnitOfWorkFactory, clock: Clock) -> None:
        self._uow_factory = uow_factory
        self._clock = clock

    def execute(self, command: DeleteHouseholdCommand, actor: Actor) -> GuestListDto:
        """Exclusão lógica (F-CNV-01, regra 2): o núcleo e as pessoas saem da lista e dos
        contadores, e tudo continua guardado para restaurar."""
        with self._uow_factory(actor) as uow:
            household = require_household(uow.guests, command.household_id)
            if household.version != command.version:
                raise VersionConflict()
            household.delete(self._clock.now(), actor.user_id)
            uow.commit()
            return build_guest_list(uow.guests)
