from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from wedding.modules.guests.application.dto import GuestStatusChangeDto
from wedding.modules.guests.domain.entities import Guest, GuestStatusChange, Household
from wedding.modules.guests.domain.settings import GuestSettings
from wedding.modules.guests.infrastructure.tables import (
    guest_households,
    guest_status_changes,
    guests,
)


class SqlGuestRepository:
    """Lê com a exclusão lógica filtrada (architecture.md §10). As pessoas de um núcleo excluído
    também saem: ele só volta restaurado."""

    def __init__(self, session: Session) -> None:
        self._session = session

    # --- núcleos

    def get_household(
        self, household_id: UUID, *, include_deleted: bool = False
    ) -> Household | None:
        query = select(Household).where(guest_households.c.id == household_id)
        if not include_deleted:
            query = query.where(guest_households.c.deleted_at.is_(None))
        return self._session.execute(query).scalar_one_or_none()

    def list_households(self) -> list[Household]:
        query = select(Household).where(guest_households.c.deleted_at.is_(None))
        return list(self._session.execute(query).scalars())

    def add_household(self, household: Household) -> None:
        self._session.add(household)

    def household_name_taken(self, key: str, *, excluding: UUID | None = None) -> bool:
        # Sem autoflush: a checagem roda depois de o caso de uso mexer na entidade, e o índice único
        # não pode estourar aqui como erro de banco antes de virar "nome já usado".
        query = select(func.count()).where(
            guest_households.c.name_key == key, guest_households.c.deleted_at.is_(None)
        )
        if excluding is not None:
            query = query.where(guest_households.c.id != excluding)
        with self._session.no_autoflush:
            return int(self._session.execute(query).scalar_one()) > 0

    # --- pessoas

    def _live_in_live_household(self):  # type: ignore[no-untyped-def]
        live_households = select(guest_households.c.id).where(
            guest_households.c.deleted_at.is_(None)
        )
        return (guests.c.deleted_at.is_(None), guests.c.household_id.in_(live_households))

    def get_guest(self, guest_id: UUID, *, include_deleted: bool = False) -> Guest | None:
        query = select(Guest).where(guests.c.id == guest_id)
        if not include_deleted:
            query = query.where(*self._live_in_live_household())
        return self._session.execute(query).scalar_one_or_none()

    def list_guests(self) -> list[Guest]:
        query = select(Guest).where(*self._live_in_live_household()).order_by(guests.c.position)
        return list(self._session.execute(query).scalars())

    def guests_of(self, household_id: UUID) -> list[Guest]:
        query = (
            select(Guest)
            .where(guests.c.household_id == household_id, guests.c.deleted_at.is_(None))
            .order_by(guests.c.position)
        )
        return list(self._session.execute(query).scalars())

    def companion_of(self, holder_id: UUID) -> Guest | None:
        query = select(Guest).where(
            guests.c.companion_of_id == holder_id, guests.c.deleted_at.is_(None)
        )
        return self._session.execute(query).scalar_one_or_none()

    def deleted_companion_of(self, holder_id: UUID) -> Guest | None:
        query = (
            select(Guest)
            .where(guests.c.companion_of_id == holder_id, guests.c.deleted_at.is_not(None))
            .order_by(guests.c.deleted_at.desc())
            .limit(1)
        )
        return self._session.execute(query).scalar_one_or_none()

    def next_position(self, household_id: UUID) -> int:
        # Conta também as excluídas: uma restaurada não pode empatar com a que ocupou o lugar dela.
        query = select(func.coalesce(func.max(guests.c.position), -1) + 1).where(
            guests.c.household_id == household_id
        )
        return int(self._session.execute(query).scalar_one())

    def add_guest(self, guest: Guest) -> None:
        self._session.add(guest)

    # --- configurações

    def get_settings(self) -> GuestSettings:
        """A linha única de pesos e limites, criada pela migration: faltar é banco mal migrado."""
        return self._session.execute(select(GuestSettings)).scalar_one()

    # --- histórico

    def add_status_change(self, change: GuestStatusChange) -> None:
        self._session.add(change)

    def status_history(self, guest_id: UUID) -> list[GuestStatusChangeDto]:
        table = guest_status_changes
        query = (
            select(
                table.c.id,
                table.c.from_status,
                table.c.to_status,
                table.c.reason,
                table.c.profile,
                table.c.created_at,
            )
            .where(table.c.guest_id == guest_id)
            .order_by(table.c.created_at.desc(), table.c.id.desc())
        )
        return [
            GuestStatusChangeDto(
                id=row.id,
                from_status=row.from_status,
                to_status=row.to_status,
                reason=row.reason,
                profile=row.profile,
                changed_at=row.created_at,
            )
            for row in self._session.execute(query)
        ]
