from pathlib import Path
from threading import Lock

from wedding.modules.files.application.commands.upload_file import UploadFile
from wedding.modules.files.application.queries.get_file import GetFile
from wedding.modules.files.application.queries.get_file_info import GetFileInfo
from wedding.modules.files.application.use_cases import FilesUseCases
from wedding.modules.files.infrastructure.mapping import start_mappers
from wedding.modules.files.infrastructure.uow import SqlFilesUnitOfWork
from wedding.platform.bootstrap.database import Database
from wedding.platform.config import Settings
from wedding.platform.storage.local import LocalFileStorage
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.clock import Clock, SystemClock
from wedding.shared_kernel.ids import UuidGenerator


class FilesContainer:
    """Monta os casos de uso de arquivos na primeira vez que alguém os pede."""

    def __init__(
        self, settings: Settings, database: Database, *, clock: Clock | None = None
    ) -> None:
        self._settings = settings
        self._database = database
        self._clock = clock or SystemClock()
        self._lock = Lock()
        self._use_cases: FilesUseCases | None = None

    def use_cases(self) -> FilesUseCases:
        with self._lock:
            if self._use_cases is None:
                self._use_cases = self._build()
            return self._use_cases

    def _build(self) -> FilesUseCases:
        start_mappers()
        sessions = self._database.sessions()
        clock = self._clock
        storage = LocalFileStorage(Path(self._settings.files_dir))

        def uow_factory(actor: Actor) -> SqlFilesUnitOfWork:
            return SqlFilesUnitOfWork(sessions, clock, actor)

        return FilesUseCases(
            upload_file=UploadFile(uow_factory, storage, UuidGenerator()),
            get_file=GetFile(uow_factory, storage),
            get_file_info=GetFileInfo(uow_factory),
        )
