import copy
from datetime import datetime
from types import TracebackType
from uuid import UUID

import pytest
from tests.modules.wedding.conftest import api  # noqa: F401  (o app inteiro, com o casal de exemplo)

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
from wedding.modules.guests.application.commands.update_guest_settings import (
    UpdateGuestSettings,
)
from wedding.modules.guests.application.commands.update_household import UpdateHousehold
from wedding.modules.guests.application.dto import GuestStatusChangeDto
from wedding.modules.guests.application.queries.build_guest_export import BuildGuestExport
from wedding.modules.guests.application.queries.get_guest_headcount import GetGuestHeadcount
from wedding.modules.guests.application.queries.get_guest_list import GetGuestList
from wedding.modules.guests.application.queries.list_guest_status_history import (
    ListGuestStatusHistory,
)
from wedding.modules.guests.application.use_cases import GuestsUseCases
from wedding.modules.guests.domain.entities import Guest, GuestStatusChange, Household
from wedding.modules.guests.domain.settings import GuestSettings
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.clock import Clock
from wedding.shared_kernel.profile import ProfileKind

NOIVO = Actor(user_id=UUID(int=1), profile=ProfileKind.NOIVO)
NOIVA = Actor(user_id=UUID(int=2), profile=ProfileKind.NOIVA)


class Store:
    def __init__(self) -> None:
        self.households: dict[UUID, Household] = {}
        self.guests: dict[UUID, Guest] = {}
        # A semente da migration: uma linha de configurações, vazia.
        self.settings = GuestSettings(id=UUID(int=7001), version=1)

    def snapshot(self) -> dict[object, object]:
        return {
            **{("h", k): copy.deepcopy(v) for k, v in self.households.items()},
            **{("g", k): copy.deepcopy(v) for k, v in self.guests.items()},
            ("s", 0): copy.deepcopy(self.settings),
        }

    def bump_versions(self, before: dict[object, object]) -> None:
        """Como o mapeamento: novo começa em 1; mudado sobe um; igual fica."""
        for kind, items in (("h", self.households), ("g", self.guests)):
            for key, item in items.items():
                original = before.get((kind, key))
                if original is None:
                    item.version = 1
                elif item != original:
                    item.version = original.version + 1  # type: ignore[attr-defined]
        original_settings = before[("s", 0)]
        if self.settings != original_settings:
            self.settings.version = original_settings.version + 1  # type: ignore[attr-defined]


class _Guests:
    """A lista em memória, com as mesmas regras de leitura do SQL: exclusão lógica filtrada, as
    pessoas de um núcleo excluído somem com ele e o nome do núcleo é único entre os vivos."""

    def __init__(self, world: "World", store: Store) -> None:
        self._world = world
        self.store = store
        self.new_changes: list[GuestStatusChange] = []

    def get_household(
        self, household_id: UUID, *, include_deleted: bool = False
    ) -> Household | None:
        household = self.store.households.get(household_id)
        if household is None or (household.deleted_at is not None and not include_deleted):
            return None
        return household

    def list_households(self) -> list[Household]:
        return [h for h in self.store.households.values() if h.deleted_at is None]

    def add_household(self, household: Household) -> None:
        self.store.households[household.id] = household

    def household_name_taken(self, key: str, *, excluding: UUID | None = None) -> bool:
        return any(h.name_key == key and h.id != excluding for h in self.list_households())

    def get_guest(self, guest_id: UUID, *, include_deleted: bool = False) -> Guest | None:
        guest = self.store.guests.get(guest_id)
        if guest is None:
            return None
        if include_deleted:
            return guest
        live_household = self.get_household(guest.household_id) is not None
        return guest if guest.deleted_at is None and live_household else None

    def list_guests(self) -> list[Guest]:
        return [g for g in self.store.guests.values() if self.get_guest(g.id) is not None]

    def guests_of(self, household_id: UUID) -> list[Guest]:
        return [g for g in self.list_guests() if g.household_id == household_id]

    def companion_of(self, holder_id: UUID) -> Guest | None:
        return next((g for g in self.list_guests() if g.companion_of_id == holder_id), None)

    def deleted_companion_of(self, holder_id: UUID) -> Guest | None:
        deleted = [
            g
            for g in self.store.guests.values()
            if g.companion_of_id == holder_id and g.deleted_at is not None
        ]
        return max(deleted, key=lambda g: g.deleted_at or datetime.min, default=None)

    def next_position(self, household_id: UUID) -> int:
        positions = [
            g.position for g in self.store.guests.values() if g.household_id == household_id
        ]
        return max(positions, default=-1) + 1

    def add_guest(self, guest: Guest) -> None:
        self.store.guests[guest.id] = guest

    def get_settings(self) -> GuestSettings:
        return self.store.settings

    def add_status_change(self, change: GuestStatusChange) -> None:
        self.new_changes.append(change)

    def status_history(self, guest_id: UUID) -> list[GuestStatusChangeDto]:
        rows = [c for c in self._world.all_changes(self.new_changes) if c.guest_id == guest_id]
        return [
            GuestStatusChangeDto(
                id=c.id,
                from_status=c.from_status,
                to_status=c.to_status,
                reason=c.reason,
                profile=c.profile,
                changed_at=self._world.stamps.get(c.id, self._world.clock.now()),
            )
            for c in reversed(rows)
        ]


class _UnitOfWork:
    """Transação de mentira: trabalha numa cópia e só a publica no commit, subindo a `version`
    do que mudou, como o mapeamento faz."""

    def __init__(self, world: "World", actor: Actor) -> None:
        self._world = world
        world.actors.append(actor)
        self._before = world.store.snapshot()
        self._store = copy.deepcopy(world.store)
        self.guests = _Guests(world, self._store)

    def __enter__(self) -> "_UnitOfWork":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None

    def commit(self) -> None:
        self._store.bump_versions(self._before)
        self._world.store = self._store
        for change in self.guests.new_changes:
            self._world.stamps[change.id] = self._world.clock.now()
        self._world.changes.extend(self.guests.new_changes)
        self.guests.new_changes = []
        self._before = self._store.snapshot()

    def rollback(self) -> None:
        return None


class _Ids:
    def __init__(self) -> None:
        self._next = 100

    def new_id(self) -> UUID:
        self._next += 1
        return UUID(int=self._next)


class World:
    def __init__(self, clock: Clock) -> None:
        self.clock = clock
        self.actors: list[Actor] = []
        self.ids = _Ids()
        self.store = Store()
        self.changes: list[GuestStatusChange] = []
        self.stamps: dict[UUID, datetime] = {}

    def all_changes(self, pending: list[GuestStatusChange]) -> list[GuestStatusChange]:
        return [*self.changes, *pending]

    def uow_factory(self, actor: Actor) -> _UnitOfWork:
        return _UnitOfWork(self, actor)

    def use_cases(self) -> GuestsUseCases:
        factory = self.uow_factory
        return GuestsUseCases(
            get_guest_list=GetGuestList(factory),
            get_guest_headcount=GetGuestHeadcount(factory),
            build_guest_export=BuildGuestExport(factory, self.clock),
            list_guest_status_history=ListGuestStatusHistory(factory),
            create_household=CreateHousehold(factory, self.ids),
            update_household=UpdateHousehold(factory),
            delete_household=DeleteHousehold(factory, self.clock),
            restore_household=RestoreHousehold(factory),
            add_guest=AddGuest(factory, self.ids),
            add_companion=AddCompanion(factory, self.ids),
            update_guest=UpdateGuest(factory),
            change_guest_status=ChangeGuestStatus(factory, self.ids),
            move_guest=MoveGuest(factory),
            delete_guest=DeleteGuest(factory, self.clock),
            restore_guest=RestoreGuest(factory),
            update_guest_settings=UpdateGuestSettings(factory),
            record_household_invite=RecordHouseholdInvite(factory, self.ids, self.clock),
            clear_household_invite=ClearHouseholdInvite(factory),
        )


@pytest.fixture
def world(clock) -> World:
    return World(clock)
