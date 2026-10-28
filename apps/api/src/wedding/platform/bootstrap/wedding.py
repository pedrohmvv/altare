from threading import Lock

from wedding.modules.wedding.application.commands.update_baseline_field import UpdateBaselineField
from wedding.modules.wedding.application.queries.get_baseline import GetBaseline
from wedding.modules.wedding.application.queries.list_baseline_changes import ListBaselineChanges
from wedding.modules.wedding.application.use_cases import WeddingUseCases
from wedding.modules.wedding.infrastructure.mapping import start_mappers
from wedding.modules.wedding.infrastructure.uow import SqlWeddingUnitOfWork
from wedding.platform.bootstrap.database import Database
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.clock import Clock, SystemClock
from wedding.shared_kernel.ids import UuidGenerator


class WeddingContainer:
    """Monta os casos de uso do casamento na primeira vez que alguém os pede."""

    def __init__(self, database: Database, *, clock: Clock | None = None) -> None:
        self._database = database
        self._clock = clock or SystemClock()
        self._lock = Lock()
        self._use_cases: WeddingUseCases | None = None

    def use_cases(self) -> WeddingUseCases:
        with self._lock:
            if self._use_cases is None:
                self._use_cases = self._build()
            return self._use_cases

    def _build(self) -> WeddingUseCases:
        start_mappers()
        sessions = self._database.sessions()
        clock = self._clock

        def uow_factory(actor: Actor) -> SqlWeddingUnitOfWork:
            return SqlWeddingUnitOfWork(sessions, clock, actor)

        return WeddingUseCases(
            get_baseline=GetBaseline(uow_factory),
            update_baseline_field=UpdateBaselineField(uow_factory, UuidGenerator()),
            list_baseline_changes=ListBaselineChanges(uow_factory),
        )
