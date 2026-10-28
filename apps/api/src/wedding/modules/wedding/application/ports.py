from collections.abc import Callable
from types import TracebackType
from typing import Protocol, Self

from wedding.modules.wedding.application.dto import BaselineChangeDto
from wedding.modules.wedding.domain.entities import BaselineChange, BaselineField
from wedding.modules.wedding.domain.value_objects import BaselineKey
from wedding.shared_kernel.actor import Actor


class BaselineRepository(Protocol):
    def get(self, key: BaselineKey) -> BaselineField | None: ...

    def all(self) -> list[BaselineField]: ...

    def add_change(self, change: BaselineChange) -> None: ...

    def changes(self, limit: int) -> list[BaselineChangeDto]:
        """As alterações mais recentes primeiro (consulta: devolve DTO, não entidade)."""
        ...


class WeddingUnitOfWork(Protocol):
    @property
    def baseline(self) -> BaselineRepository: ...

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
WeddingUnitOfWorkFactory = Callable[[Actor], WeddingUnitOfWork]
