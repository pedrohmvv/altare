from dataclasses import dataclass
from uuid import UUID

from wedding.modules.guests.application.dto import GuestListDto
from wedding.modules.guests.application.fields import GuestFields
from wedding.modules.guests.application.list_map import build_guest_list, require_guest
from wedding.modules.guests.application.new_guest import build_guest
from wedding.modules.guests.application.ports import GuestsUnitOfWorkFactory
from wedding.modules.guests.domain.errors import (
    CompanionAlreadyExists,
    CompanionCannotHaveCompanion,
)
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.ids import IdGenerator


@dataclass(frozen=True)
class AddCompanionCommand:
    holder_id: UUID
    name: str | None


class AddCompanion:
    def __init__(self, uow_factory: GuestsUnitOfWorkFactory, ids: IdGenerator) -> None:
        self._uow_factory = uow_factory
        self._ids = ids

    def execute(self, command: AddCompanionCommand, actor: Actor) -> GuestListDto:
        """O +1 é uma pessoa a confirmar, do mesmo núcleo do titular, uma só por titular, e que não
        leva outro (F-CNV-02, `D-071`). O nome pode vir depois."""
        with self._uow_factory(actor) as uow:
            holder = require_guest(uow.guests, command.holder_id)
            if holder.is_companion:
                raise CompanionCannotHaveCompanion()
            if uow.guests.companion_of(holder.id) is not None:
                raise CompanionAlreadyExists()
            companion = build_guest(
                self._ids.new_id(),
                holder.household_id,
                uow.guests.next_position(holder.household_id),
                GuestFields(name=command.name),
                companion_of_id=holder.id,
            )
            uow.guests.add_guest(companion)
            uow.commit()
            return build_guest_list(uow.guests)
