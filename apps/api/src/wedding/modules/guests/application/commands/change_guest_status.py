from dataclasses import dataclass
from uuid import UUID

from wedding.modules.guests.application.dto import GuestListDto
from wedding.modules.guests.application.list_map import build_guest_list, require_guest
from wedding.modules.guests.application.ports import GuestsUnitOfWorkFactory
from wedding.modules.guests.domain.entities import GuestStatusChange
from wedding.modules.guests.domain.values import GuestStatus
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.errors import VersionConflict
from wedding.shared_kernel.ids import IdGenerator


@dataclass(frozen=True)
class ChangeGuestStatusCommand:
    guest_id: UUID
    status: GuestStatus
    reason: str | None
    version: int


class ChangeGuestStatus:
    def __init__(self, uow_factory: GuestsUnitOfWorkFactory, ids: IdGenerator) -> None:
        self._uow_factory = uow_factory
        self._ids = ids

    def execute(self, command: ChangeGuestStatusCommand, actor: Actor) -> GuestListDto:
        """Qualquer um dos dois muda o status, de qualquer para qualquer (F-CNV-04); a mudança fica
        com autor, status anterior e, para `Não irá`, o motivo. Repetir o status não grava nada."""
        with self._uow_factory(actor) as uow:
            guest = require_guest(uow.guests, command.guest_id)
            if guest.version != command.version:
                raise VersionConflict()
            before = guest.status
            if guest.change_status(command.status, command.reason):
                uow.guests.add_status_change(
                    GuestStatusChange(
                        id=self._ids.new_id(),
                        guest_id=guest.id,
                        from_status=before,
                        to_status=guest.status,
                        reason=guest.decline_reason,
                        profile=actor.profile,
                    )
                )
                uow.commit()
            return build_guest_list(uow.guests)
