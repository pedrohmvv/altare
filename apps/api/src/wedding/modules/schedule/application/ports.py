from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from types import TracebackType
from typing import Protocol, Self
from uuid import UUID

from wedding.modules.schedule.domain.entities import (
    ChecklistItem,
    Dependency,
    Milestone,
    MilestoneChange,
    MilestoneDependency,
    Phase,
    Task,
)
from wedding.modules.schedule.domain.values import OwnerKind, Standing
from wedding.shared_kernel.actor import Actor


class ScheduleRepository(Protocol):
    """Fases, marcos, dependências, histórico, avulsas e checklist. Tudo o que lê já filtra a
    exclusão lógica."""

    def list_phases(self) -> list[Phase]: ...

    def get_phase(self, phase_id: UUID) -> Phase | None: ...

    def add_phase(self, phase: Phase) -> None: ...

    def next_phase_position(self) -> int:
        """O fim da lista de fases."""
        ...

    def list_milestones(self) -> list[Milestone]: ...

    def get_milestone(
        self, milestone_id: UUID, *, include_deleted: bool = False
    ) -> Milestone | None: ...

    def add_milestone(self, milestone: Milestone) -> None: ...

    def next_milestone_position(self, phase_id: UUID) -> int:
        """O fim da fase, entre os marcos vivos."""
        ...

    def dependencies(self) -> list[Dependency]:
        """Só os vínculos vivos entre marcos vivos."""
        ...

    def live_links_of(self, milestone_id: UUID) -> list[MilestoneDependency]:
        """Os vínculos vivos em que o marco aparece, nos dois sentidos."""
        ...

    def deleted_links_of(self, milestone_id: UUID) -> list[MilestoneDependency]:
        """Os vínculos desativados em que o marco aparece, nos dois sentidos, com o carimbo de cada
        um (quem decide quais voltam é o caso de uso)."""
        ...

    def add_link(self, link: MilestoneDependency) -> None: ...

    def add_change(self, change: MilestoneChange) -> None: ...

    def list_tasks(self) -> list[Task]: ...

    def get_task(self, task_id: UUID, *, include_deleted: bool = False) -> Task | None: ...

    def add_task(self, task: Task) -> None: ...

    def list_checklist_items(self) -> list[ChecklistItem]:
        """Os itens vivos de todos os donos, numa só consulta. Quem os agrupa descarta os de dono
        excluído: excluir o dono não apaga os itens (restaurar os traz de volta)."""
        ...

    def live_items_of(self, kind: OwnerKind, owner_id: UUID) -> list[ChecklistItem]:
        """Os itens vivos do dono, na ordem do checklist (posição e id)."""
        ...

    def get_checklist_item(self, item_id: UUID) -> ChecklistItem | None:
        """O item vivo, qualquer que seja o dono; conferir se o dono está vivo é do caso de uso."""
        ...

    def add_checklist_item(self, item: ChecklistItem) -> None: ...


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
    # Não oculta e de grupo não oculto: só estas o casal pode ligar a um marco (F-CRN-04).
    visible: bool


class CategoryReader(Protocol):
    """Porta para o Mapa de Escopo: o `schedule` não importa o módulo `wedding`; o `bootstrap`
    liga os dois pelo contrato público (`D-068`, `D-069`, `D-073`). Uma categoria que não vem na
    resposta foi excluída. A ordem da resposta é a do Mapa (grupo e depois categoria)."""

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
