from dataclasses import dataclass
from datetime import date
from uuid import UUID

from wedding.modules.guests.application.dates import today_in_brazil
from wedding.modules.guests.application.export_rows import ExportRow, build_export_rows
from wedding.modules.guests.application.list_map import build_guest_list
from wedding.modules.guests.application.ports import GuestsUnitOfWorkFactory
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.clock import Clock
from wedding.shared_kernel.errors import NotFound


@dataclass(frozen=True)
class GuestExport:
    rows: list[ExportRow]
    day: date


class BuildGuestExport:
    def __init__(self, uow_factory: GuestsUnitOfWorkFactory, clock: Clock) -> None:
        self._uow_factory = uow_factory
        self._clock = clock

    def execute(self, guest_ids: list[UUID] | None, actor: Actor) -> GuestExport:
        """As linhas da exportação (F-CNV-08): as pessoas pedidas, que são as que estão na tela, ou
        todas. Uma pessoa que já não está na lista (excluída enquanto a tela estava aberta) é
        recusada, para a contagem que a tela anunciou nunca divergir do arquivo."""
        with self._uow_factory(actor) as uow:
            listing = build_guest_list(uow.guests)
            if guest_ids is not None:
                known = {guest.id for household in listing.households for guest in household.guests}
                if not set(guest_ids) <= known:
                    raise NotFound()
            return GuestExport(build_export_rows(listing, guest_ids), today_in_brazil(self._clock))
