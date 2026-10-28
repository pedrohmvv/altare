from dataclasses import dataclass
from datetime import date
from uuid import UUID

from wedding.modules.guests.application.dates import today_in_brazil
from wedding.modules.guests.application.dto import GuestListDto
from wedding.modules.guests.application.list_map import build_guest_list, require_household
from wedding.modules.guests.application.ports import GuestsUnitOfWorkFactory
from wedding.modules.guests.domain.entities import GuestStatusChange
from wedding.modules.guests.domain.values import GuestStatus, InviteChannel
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.clock import Clock
from wedding.shared_kernel.errors import VersionConflict
from wedding.shared_kernel.ids import IdGenerator


@dataclass(frozen=True)
class RecordHouseholdInviteCommand:
    household_id: UUID
    version: int
    sent_on: date
    channel: InviteChannel
    move_drafts: bool


class RecordHouseholdInvite:
    def __init__(
        self, uow_factory: GuestsUnitOfWorkFactory, ids: IdGenerator, clock: Clock
    ) -> None:
        self._uow_factory = uow_factory
        self._ids = ids
        self._clock = clock

    def execute(self, command: RecordHouseholdInviteCommand, actor: Actor) -> GuestListDto:
        """Registra o envio do convite do núcleo (F-CNV-05). Mover os rascunhos para `Convidado` é
        uma oferta que a tela faz e o casal aceita: só com `move_drafts` as pessoas em `Rascunho`
        mudam, e cada mudança fica no histórico. Quem está em outro status nunca é tocado."""
        with self._uow_factory(actor) as uow:
            household = require_household(uow.guests, command.household_id)
            if household.version != command.version:
                raise VersionConflict()
            changed = household.record_invite(
                command.sent_on, command.channel, today=today_in_brazil(self._clock)
            )
            if command.move_drafts:
                for guest in uow.guests.guests_of(household.id):
                    if guest.status is GuestStatus.DRAFT and guest.change_status(
                        GuestStatus.INVITED, None
                    ):
                        uow.guests.add_status_change(
                            GuestStatusChange(
                                id=self._ids.new_id(),
                                guest_id=guest.id,
                                from_status=GuestStatus.DRAFT,
                                to_status=GuestStatus.INVITED,
                                reason=None,
                                profile=actor.profile,
                            )
                        )
                        changed = True
            if changed:
                uow.commit()
            return build_guest_list(uow.guests)
