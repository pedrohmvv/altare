from collections.abc import Callable
from types import TracebackType
from typing import Protocol, Self
from uuid import UUID

from wedding.modules.guests.application.dto import GuestStatusChangeDto
from wedding.modules.guests.domain.entities import Guest, GuestStatusChange, Household
from wedding.modules.guests.domain.settings import GuestSettings
from wedding.shared_kernel.actor import Actor


class GuestRepository(Protocol):
    """Núcleos, pessoas e histórico. Tudo o que lê já filtra a exclusão lógica; as pessoas de um
    núcleo excluído também saem (ele só volta restaurado)."""

    def get_household(
        self, household_id: UUID, *, include_deleted: bool = False
    ) -> Household | None: ...

    def list_households(self) -> list[Household]: ...

    def add_household(self, household: Household) -> None: ...

    def household_name_taken(self, key: str, *, excluding: UUID | None = None) -> bool: ...

    def get_guest(self, guest_id: UUID, *, include_deleted: bool = False) -> Guest | None: ...

    def list_guests(self) -> list[Guest]: ...

    def guests_of(self, household_id: UUID) -> list[Guest]: ...

    def companion_of(self, holder_id: UUID) -> Guest | None: ...

    def deleted_companion_of(self, holder_id: UUID) -> Guest | None:
        """O acompanhante excluído mais recentemente (para restaurar junto com o titular)."""
        ...

    def next_position(self, household_id: UUID) -> int: ...

    def get_settings(self) -> GuestSettings:
        """A linha única de pesos e limites; criada pela migration, faltar é banco mal migrado."""
        ...

    def add_guest(self, guest: Guest) -> None: ...

    def add_status_change(self, change: GuestStatusChange) -> None: ...

    def status_history(self, guest_id: UUID) -> list[GuestStatusChangeDto]:
        """Do mais recente ao mais antigo (consulta: devolve DTO, não entidade)."""
        ...


class GuestsUnitOfWork(Protocol):
    @property
    def guests(self) -> GuestRepository: ...

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...


# Quem lê ou altera é sempre alguém na sessão: o ator vai para o histórico do registro.
GuestsUnitOfWorkFactory = Callable[[Actor], GuestsUnitOfWork]
