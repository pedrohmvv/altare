from collections.abc import Callable
from threading import Lock
from uuid import UUID

from wedding.modules.schedule.application.commands.change_milestone_state import (
    ChangeMilestoneState,
)
from wedding.modules.schedule.application.commands.create_milestone import CreateMilestone
from wedding.modules.schedule.application.commands.create_phase import CreatePhase
from wedding.modules.schedule.application.commands.delete_milestone import DeleteMilestone
from wedding.modules.schedule.application.commands.rename_phase import RenamePhase
from wedding.modules.schedule.application.commands.reorder_phases import ReorderPhases
from wedding.modules.schedule.application.commands.restore_milestone import RestoreMilestone
from wedding.modules.schedule.application.commands.set_milestone_dependencies import (
    SetMilestoneDependencies,
)
from wedding.modules.schedule.application.commands.update_milestone import UpdateMilestone
from wedding.modules.schedule.application.ports import CategoryInfo, WeddingDate
from wedding.modules.schedule.application.queries.read_schedule import ReadSchedule
from wedding.modules.schedule.application.schedule_map import ScheduleReader
from wedding.modules.schedule.application.use_cases import ScheduleUseCases
from wedding.modules.schedule.domain.values import Standing
from wedding.modules.schedule.infrastructure.mapping import start_mappers
from wedding.modules.schedule.infrastructure.uow import SqlScheduleUnitOfWork
from wedding.modules.wedding.application.public import DateKind, DefinitionStatus, ScopeStatus
from wedding.modules.wedding.application.scope_use_cases import ScopeUseCases
from wedding.modules.wedding.application.use_cases import WeddingUseCases
from wedding.platform.bootstrap.database import Database
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.clock import Clock, SystemClock
from wedding.shared_kernel.ids import UuidGenerator

_STANDING_BY_STATUS = {
    ScopeStatus.ESSENTIAL: Standing.ENTERS,
    ScopeStatus.MAYBE: Standing.MAYBE,
    ScopeStatus.IN_DISCUSSION: Standing.IN_DISCUSSION,
    ScopeStatus.OUT: Standing.OUT,
}


class WeddingScopeCategories:
    """Liga o `schedule` ao Mapa de Escopo sem um importar o outro: só o bootstrap conhece os dois.
    Lê o status e a visibilidade pelo contrato público do `wedding`, na hora, sem copiá-los, e
    dobra a visibilidade no status: categoria oculta ou de grupo oculto conta como `Fica de fora`
    (F-CRN-04, regra 3)."""

    def __init__(self, scope: Callable[[], ScopeUseCases]) -> None:
        self._scope = scope

    def categories(self, actor: Actor) -> dict[UUID, CategoryInfo]:
        return {
            item.id: CategoryInfo(
                item.name,
                _STANDING_BY_STATUS[item.status] if item.visible else Standing.OUT,
                item.visible,
            )
            for item in self._scope().get_scope_standings.execute(actor)
        }


class WeddingDateFromBaseline:
    """Liga o `schedule` à data das Definições Base sem um importar o outro: só vale a data com
    status `Definido` e forma exata (F-CRN-05, Modo Com Data)."""

    def __init__(self, wedding: Callable[[], WeddingUseCases]) -> None:
        self._wedding = wedding

    def wedding_date(self, actor: Actor) -> WeddingDate:
        found = self._wedding().get_wedding_date.execute(actor)
        exact = found.exact if found.kind is DateKind.EXACT else None
        return WeddingDate(defined=found.status is DefinitionStatus.DEFINED, exact=exact)


class ScheduleContainer:
    """Monta os casos de uso do cronograma na primeira vez que alguém os pede."""

    def __init__(
        self,
        database: Database,
        wedding: Callable[[], WeddingUseCases],
        scope: Callable[[], ScopeUseCases],
        *,
        clock: Clock | None = None,
    ) -> None:
        self._database = database
        self._wedding = wedding
        self._scope = scope
        self._clock = clock or SystemClock()
        self._lock = Lock()
        self._use_cases: ScheduleUseCases | None = None

    def use_cases(self) -> ScheduleUseCases:
        with self._lock:
            if self._use_cases is None:
                self._use_cases = self._build()
            return self._use_cases

    def _build(self) -> ScheduleUseCases:
        start_mappers()
        sessions = self._database.sessions()
        clock = self._clock
        categories = WeddingScopeCategories(self._scope)
        reader = ScheduleReader(categories, WeddingDateFromBaseline(self._wedding), clock)
        ids = UuidGenerator()

        def uow_factory(actor: Actor) -> SqlScheduleUnitOfWork:
            return SqlScheduleUnitOfWork(sessions, clock, actor)

        return ScheduleUseCases(
            read_schedule=ReadSchedule(uow_factory, reader),
            update_milestone=UpdateMilestone(uow_factory, reader, categories),
            change_milestone_state=ChangeMilestoneState(uow_factory, ids, reader),
            create_milestone=CreateMilestone(uow_factory, ids, reader, categories),
            delete_milestone=DeleteMilestone(uow_factory, clock, reader),
            restore_milestone=RestoreMilestone(uow_factory, reader),
            set_milestone_dependencies=SetMilestoneDependencies(uow_factory, ids, clock, reader),
            create_phase=CreatePhase(uow_factory, ids, reader),
            rename_phase=RenamePhase(uow_factory, reader),
            reorder_phases=ReorderPhases(uow_factory, reader),
        )
