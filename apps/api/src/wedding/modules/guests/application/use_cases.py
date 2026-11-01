from collections.abc import Callable
from dataclasses import dataclass

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
from wedding.modules.guests.application.queries.build_guest_export import BuildGuestExport
from wedding.modules.guests.application.queries.get_guest_headcount import GetGuestHeadcount
from wedding.modules.guests.application.queries.get_guest_list import GetGuestList
from wedding.modules.guests.application.queries.list_guest_status_history import (
    ListGuestStatusHistory,
)


@dataclass(frozen=True)
class GuestsUseCases:
    get_guest_list: GetGuestList
    get_guest_headcount: GetGuestHeadcount
    build_guest_export: BuildGuestExport
    list_guest_status_history: ListGuestStatusHistory
    create_household: CreateHousehold
    update_household: UpdateHousehold
    delete_household: DeleteHousehold
    restore_household: RestoreHousehold
    add_guest: AddGuest
    add_companion: AddCompanion
    update_guest: UpdateGuest
    change_guest_status: ChangeGuestStatus
    move_guest: MoveGuest
    delete_guest: DeleteGuest
    restore_guest: RestoreGuest
    update_guest_settings: UpdateGuestSettings
    record_household_invite: RecordHouseholdInvite
    clear_household_invite: ClearHouseholdInvite


GuestsProvider = Callable[[], GuestsUseCases]
