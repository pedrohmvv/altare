from collections.abc import Callable
from threading import Lock
from uuid import UUID

from wedding.modules.files.application.use_cases import FilesUseCases
from wedding.modules.guests.application.use_cases import GuestsUseCases
from wedding.modules.wedding.application.commands.add_image_reference import AddImageReference
from wedding.modules.wedding.application.commands.add_link_reference import AddLinkReference
from wedding.modules.wedding.application.commands.change_scope_status import ChangeScopeStatus
from wedding.modules.wedding.application.commands.create_scope_category import CreateScopeCategory
from wedding.modules.wedding.application.commands.create_scope_group import CreateScopeGroup
from wedding.modules.wedding.application.commands.delete_scope_category import DeleteScopeCategory
from wedding.modules.wedding.application.commands.delete_scope_group import DeleteScopeGroup
from wedding.modules.wedding.application.commands.remove_reference import RemoveReference
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
from wedding.modules.wedding.application.ports import StoredFile
from wedding.modules.wedding.application.queries.get_baseline import GetBaseline
from wedding.modules.wedding.application.queries.get_scope_map import GetScopeMap
from wedding.modules.wedding.application.queries.get_scope_standings import GetScopeStandings
from wedding.modules.wedding.application.queries.get_wedding_date import GetWeddingDate
from wedding.modules.wedding.application.queries.list_baseline_changes import ListBaselineChanges
from wedding.modules.wedding.application.queries.list_references import ListReferences
from wedding.modules.wedding.application.queries.list_scope_category_history import (
    ListScopeCategoryHistory,
)
from wedding.modules.wedding.application.reference_use_cases import ReferenceUseCases
from wedding.modules.wedding.application.scope_use_cases import ScopeUseCases
from wedding.modules.wedding.application.use_cases import WeddingUseCases
from wedding.modules.wedding.infrastructure.mapping import start_mappers
from wedding.modules.wedding.infrastructure.uow import SqlWeddingUnitOfWork
from wedding.platform.bootstrap.database import Database
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.clock import Clock, SystemClock
from wedding.shared_kernel.errors import NotFound
from wedding.shared_kernel.ids import UuidGenerator


class FilesImageCatalog:
    """Liga o `wedding` ao módulo de arquivos sem um importar o outro: só o bootstrap conhece os
    dois. Diz se um arquivo enviado existe e se é imagem."""

    def __init__(self, files: Callable[[], FilesUseCases]) -> None:
        self._files = files

    def find(self, file_id: UUID, actor: Actor) -> StoredFile | None:
        try:
            info = self._files().get_file_info.execute(file_id, actor)
        except NotFound:
            return None
        return StoredFile(file_id, info.content_type.startswith("image/"))


class GuestsTotalNominal:
    """Liga o `wedding` à lista de convidados sem um importar o outro: só o bootstrap conhece os
    dois. Lê o Total Nominal pelo contrato público do `guests`, na hora, sem copiá-lo."""

    def __init__(self, guests: Callable[[], GuestsUseCases]) -> None:
        self._guests = guests

    def total_nominal(self, actor: Actor) -> int:
        return self._guests().get_guest_headcount.execute(actor).total_nominal.total


class WeddingContainer:
    """Monta os casos de uso do casamento na primeira vez que alguém os pede."""

    def __init__(
        self,
        database: Database,
        files: Callable[[], FilesUseCases],
        guests: Callable[[], GuestsUseCases],
        *,
        clock: Clock | None = None,
    ) -> None:
        self._database = database
        self._files = files
        self._guests = guests
        self._clock = clock or SystemClock()
        self._lock = Lock()
        self._use_cases: WeddingUseCases | None = None
        self._scope_use_cases: ScopeUseCases | None = None
        self._reference_use_cases: ReferenceUseCases | None = None

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

    def reference_use_cases(self) -> ReferenceUseCases:
        with self._lock:
            if self._reference_use_cases is None:
                self._reference_use_cases = self._build_references()
            return self._reference_use_cases

    def _build_references(self) -> ReferenceUseCases:
        start_mappers()
        sessions = self._database.sessions()
        clock = self._clock
        ids = UuidGenerator()

        def uow_factory(actor: Actor) -> SqlWeddingUnitOfWork:
            return SqlWeddingUnitOfWork(sessions, clock, actor)

        return ReferenceUseCases(
            list_references=ListReferences(uow_factory, clock),
            add_link_reference=AddLinkReference(uow_factory, ids, clock),
            add_image_reference=AddImageReference(
                uow_factory, ids, clock, FilesImageCatalog(self._files)
            ),
            remove_reference=RemoveReference(uow_factory, clock),
        )

    def _build_scope(self) -> ScopeUseCases:
        start_mappers()
        sessions = self._database.sessions()
        clock = self._clock
        ids = UuidGenerator()

        def uow_factory(actor: Actor) -> SqlWeddingUnitOfWork:
            return SqlWeddingUnitOfWork(sessions, clock, actor)

        return ScopeUseCases(
            get_scope_map=GetScopeMap(uow_factory),
            get_scope_standings=GetScopeStandings(uow_factory),
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
        guest_count = GuestsTotalNominal(self._guests)

        def uow_factory(actor: Actor) -> SqlWeddingUnitOfWork:
            return SqlWeddingUnitOfWork(sessions, clock, actor)

        return WeddingUseCases(
            get_baseline=GetBaseline(uow_factory, guest_count),
            get_wedding_date=GetWeddingDate(uow_factory),
            update_baseline_field=UpdateBaselineField(uow_factory, UuidGenerator(), guest_count),
            list_baseline_changes=ListBaselineChanges(uow_factory),
        )
