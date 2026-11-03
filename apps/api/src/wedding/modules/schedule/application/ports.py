from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from types import TracebackType
from typing import Protocol, Self
from uuid import UUID

from wedding.modules.schedule.domain.entities import (
    Dependency,
    Milestone,
    MilestoneChange,
    Phase,
)
from wedding.modules.schedule.domain.values import Standing
from wedding.shared_kernel.actor import Actor


class ScheduleRepository(Protocol):
    """Fases, marcos, dependências e histórico. Tudo o que lê já filtra a exclusão lógica."""

    def list_phases(self) -> list[Phase]: ...

    def list_milestones(self) -> list[Milestone]: ...

    def get_milestone(self, milestone_id: UUID) -> Milestone | None: ...

    def dependencies(self) -> list[Dependency]:
        """Só os vínculos vivos entre marcos vivos."""
        ...

    def add_change(self, change: MilestoneChange) -> None: ...


class ScheduleUnitOfWork(Protocol):
    @property
    def schedule(self) -> ScheduleRepository: ...

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
ScheduleUnitOfWorkFactory = Callable[[Actor], ScheduleUnitOfWork]


@dataclass(frozen=True)
class CategoryInfo:
    """Uma categoria do Mapa de Escopo como o cronograma a vê: o nome de hoje e a situação, com
    a visibilidade já dobrada (oculta, de grupo oculto ou excluída é `Fica de fora`)."""

    name: str
    standing: Standing


class CategoryReader(Protocol):
    """Porta para o Mapa de Escopo: o `schedule` não importa o módulo `wedding`; o `bootstrap`
    liga os dois pelo contrato público (`D-068`, `D-069`, `D-073`). Uma categoria que não vem na
    resposta foi excluída."""

    def categories(self, actor: Actor) -> dict[UUID, CategoryInfo]: ...


@dataclass(frozen=True)
class WeddingDate:
    """A data do casamento como o cronograma a usa: só vale com status `Definido` e forma exata."""

    defined: bool
    exact: date | None

    @property
    def is_exact_and_defined(self) -> bool:
        return self.defined and self.exact is not None


class WeddingDateReader(Protocol):
    """Porta para as Definições Base: a data do casamento, lida na hora e nunca copiada."""

    def wedding_date(self, actor: Actor) -> WeddingDate: ...
