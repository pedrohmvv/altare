from threading import Lock

from wedding.modules.guests.application.commands.add_companion import AddCompanion
from wedding.modules.guests.application.commands.add_guest import AddGuest
from wedding.modules.guests.application.commands.change_guest_status import ChangeGuestStatus
from wedding.modules.guests.application.commands.clear_household_invite import ClearHouseholdInvite
from wedding.modules.guests.application.commands.create_household import CreateHousehold
from wedding.modules.guests.application.commands.delete_guest import DeleteGuest
from wedding.modules.guests.application.commands.delete_household import DeleteHousehold
from wedding.modules.guests.application.commands.move_guest import MoveGuest
from wedding.modules.guests.application.commands.record_household_invite import (
    RecordHouseholdInvite,
)
from wedding.modules.guests.application.commands.restore_guest import RestoreGuest
from wedding.modules.guests.application.commands.restore_household import RestoreHousehold
from wedding.modules.guests.application.commands.update_guest import UpdateGuest
from wedding.modules.guests.application.commands.update_guest_settings import UpdateGuestSettings
from wedding.modules.guests.application.commands.update_household import UpdateHousehold
from wedding.modules.guests.application.queries.get_guest_headcount import GetGuestHeadcount
from wedding.modules.guests.application.queries.get_guest_list import GetGuestList
from wedding.modules.guests.application.queries.list_guest_status_history import (
    ListGuestStatusHistory,
)
from wedding.modules.guests.application.use_cases import GuestsUseCases
from wedding.modules.guests.infrastructure.mapping import start_mappers
from wedding.modules.guests.infrastructure.uow import SqlGuestsUnitOfWork
from wedding.platform.bootstrap.database import Database
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.clock import Clock, SystemClock
from wedding.shared_kernel.ids import UuidGenerator


class GuestsContainer:
    """Monta os casos de uso da lista de convidados na primeira vez que alguém os pede."""

    def __init__(self, database: Database, *, clock: Clock | None = None) -> None:
        self._database = database
        self._clock = clock or SystemClock()
        self._lock = Lock()
        self._use_cases: GuestsUseCases | None = None

    def use_cases(self) -> GuestsUseCases:
        with self._lock:
            if self._use_cases is None:
                self._use_cases = self._build()
            return self._use_cases

    def _build(self) -> GuestsUseCases:
        start_mappers()
        sessions = self._database.sessions()
        clock = self._clock
        ids = UuidGenerator()

        def uow_factory(actor: Actor) -> SqlGuestsUnitOfWork:
            return SqlGuestsUnitOfWork(sessions, clock, actor)

        return GuestsUseCases(
            get_guest_list=GetGuestList(uow_factory),
            get_guest_headcount=GetGuestHeadcount(uow_factory),
            list_guest_status_history=ListGuestStatusHistory(uow_factory),
            create_household=CreateHousehold(uow_factory, ids),
            update_household=UpdateHousehold(uow_factory),
            delete_household=DeleteHousehold(uow_factory, clock),
            restore_household=RestoreHousehold(uow_factory),
            add_guest=AddGuest(uow_factory, ids),
            add_companion=AddCompanion(uow_factory, ids),
            update_guest=UpdateGuest(uow_factory),
            change_guest_status=ChangeGuestStatus(uow_factory, ids),
            move_guest=MoveGuest(uow_factory),
            delete_guest=DeleteGuest(uow_factory, clock),
            restore_guest=RestoreGuest(uow_factory),
            update_guest_settings=UpdateGuestSettings(uow_factory),
            record_household_invite=RecordHouseholdInvite(uow_factory, ids, clock),
            clear_household_invite=ClearHouseholdInvite(uow_factory),
        )
