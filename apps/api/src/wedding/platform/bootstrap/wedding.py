from threading import Lock

from wedding.modules.wedding.application.commands.change_scope_status import ChangeScopeStatus
from wedding.modules.wedding.application.commands.create_scope_category import CreateScopeCategory
from wedding.modules.wedding.application.commands.create_scope_group import CreateScopeGroup
from wedding.modules.wedding.application.commands.delete_scope_category import DeleteScopeCategory
from wedding.modules.wedding.application.commands.delete_scope_group import DeleteScopeGroup
from wedding.modules.wedding.application.commands.rename_scope_group import RenameScopeGroup
from wedding.modules.wedding.application.commands.set_my_evaluation import SetMyEvaluation
from wedding.modules.wedding.application.commands.set_scope_category_visibility import (
    SetScopeCategoryVisibility,
)
from wedding.modules.wedding.application.commands.set_scope_group_visibility import (
    SetScopeGroupVisibility,
)
from wedding.modules.wedding.application.commands.update_baseline_field import UpdateBaselineField
from wedding.modules.wedding.application.commands.update_scope_category import UpdateScopeCategory
from wedding.modules.wedding.application.queries.get_baseline import GetBaseline
from wedding.modules.wedding.application.queries.get_scope_map import GetScopeMap
from wedding.modules.wedding.application.queries.list_baseline_changes import ListBaselineChanges
from wedding.modules.wedding.application.queries.list_scope_category_history import (
    ListScopeCategoryHistory,
)
from wedding.modules.wedding.application.scope_use_cases import ScopeUseCases
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
        self._scope_use_cases: ScopeUseCases | None = None

    def use_cases(self) -> WeddingUseCases:
        with self._lock:
            if self._use_cases is None:
                self._use_cases = self._build()
            return self._use_cases

    def scope_use_cases(self) -> ScopeUseCases:
        with self._lock:
            if self._scope_use_cases is None:
                self._scope_use_cases = self._build_scope()
            return self._scope_use_cases

    def _build_scope(self) -> ScopeUseCases:
        start_mappers()
        sessions = self._database.sessions()
        clock = self._clock
        ids = UuidGenerator()

        def uow_factory(actor: Actor) -> SqlWeddingUnitOfWork:
            return SqlWeddingUnitOfWork(sessions, clock, actor)

        return ScopeUseCases(
            get_scope_map=GetScopeMap(uow_factory),
            list_scope_category_history=ListScopeCategoryHistory(uow_factory),
            create_scope_group=CreateScopeGroup(uow_factory, ids),
            rename_scope_group=RenameScopeGroup(uow_factory),
            set_scope_group_visibility=SetScopeGroupVisibility(uow_factory, clock),
            delete_scope_group=DeleteScopeGroup(uow_factory, clock),
            create_scope_category=CreateScopeCategory(uow_factory, ids),
            update_scope_category=UpdateScopeCategory(uow_factory),
            set_scope_category_visibility=SetScopeCategoryVisibility(uow_factory, clock),
            delete_scope_category=DeleteScopeCategory(uow_factory, clock),
            change_scope_status=ChangeScopeStatus(uow_factory, ids),
            set_my_evaluation=SetMyEvaluation(uow_factory),
        )

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
