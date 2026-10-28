from dataclasses import dataclass
from uuid import UUID

from wedding.modules.guests.application.dto import GuestListDto
from wedding.modules.guests.application.list_map import build_guest_list
from wedding.modules.guests.application.ports import GuestsUnitOfWorkFactory
from wedding.modules.guests.domain.errors import CompanionAlreadyExists
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.errors import NotFound


@dataclass(frozen=True)
class RestoreGuestCommand:
    guest_id: UUID


class RestoreGuest:
    def __init__(self, uow_factory: GuestsUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    def execute(self, command: RestoreGuestCommand, actor: Actor) -> GuestListDto:
        """Desfaz a exclusão. Restaurar o titular traz de volta o acompanhante excluído junto com
        ele; um acompanhante só volta se o titular está na lista e ainda sem outro +1."""
        with self._uow_factory(actor) as uow:
            guest = uow.guests.get_guest(command.guest_id, include_deleted=True)
            if guest is None or guest.deleted_at is None:
                raise NotFound()
            if uow.guests.get_household(guest.household_id) is None:
                raise NotFound()
            if guest.companion_of_id is not None:
                holder = uow.guests.get_guest(guest.companion_of_id)
                if holder is None:
                    raise NotFound()
                if uow.guests.companion_of(holder.id) is not None:
                    raise CompanionAlreadyExists()
            deleted_at = guest.deleted_at
            guest.restore()
            companion = uow.guests.deleted_companion_of(guest.id)
            if companion is not None and companion.deleted_at == deleted_at:
                companion.restore()
            uow.commit()
            return build_guest_list(uow.guests)
