from collections.abc import Callable
from threading import Lock
from uuid import UUID

from wedding.modules.schedule.application.commands.change_milestone_state import (
    ChangeMilestoneState,
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
                item.name, _STANDING_BY_STATUS[item.status] if item.visible else Standing.OUT
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
        reader = ScheduleReader(
            WeddingScopeCategories(self._scope), WeddingDateFromBaseline(self._wedding), clock
        )

        def uow_factory(actor: Actor) -> SqlScheduleUnitOfWork:
            return SqlScheduleUnitOfWork(sessions, clock, actor)

        return ScheduleUseCases(
            read_schedule=ReadSchedule(uow_factory, reader),
            update_milestone=UpdateMilestone(uow_factory, reader),
            change_milestone_state=ChangeMilestoneState(uow_factory, UuidGenerator(), reader),
        )
