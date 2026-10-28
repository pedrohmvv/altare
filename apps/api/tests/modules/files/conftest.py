import copy
from collections.abc import Iterator
from types import TracebackType
from uuid import UUID

import pytest

from wedding.modules.files.application.use_cases import FilesUseCases
from wedding.modules.files.domain.entities import FileAsset
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.profile import ProfileKind

PDF = b"%PDF-1.7\n%conteudo de exemplo"


class _Files:
    def __init__(self, files: dict[UUID, FileAsset]) -> None:
        self._files = files

    def add(self, file: FileAsset) -> None:
        self._files[file.id] = file

    def get(self, file_id: UUID) -> FileAsset | None:
        return self._files.get(file_id)


class _UnitOfWork:
    """Transação de mentira: trabalha numa cópia e só a publica no commit."""

    def __init__(self, world: "World", actor: Actor) -> None:
        self._world = world
        world.actors.append(actor)
        self._files = copy.deepcopy(world.files)
        self.files = _Files(self._files)

    def __enter__(self) -> "_UnitOfWork":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None

    def commit(self) -> None:
        self._world.files = self._files

    def rollback(self) -> None:
        return None


class _Storage:
    def __init__(self) -> None:
        self.blobs: dict[str, bytes] = {}
        self.puts = 0

    def put(self, key: str, data: bytes) -> None:
        self.puts += 1
        self.blobs.setdefault(key, data)

    def exists(self, key: str) -> bool:
        return key in self.blobs

    def read(self, key: str) -> Iterator[bytes]:
        if key not in self.blobs:
            raise FileNotFoundError(key)
        data = self.blobs[key]
        for start in range(0, len(data), 7):
            yield data[start : start + 7]


class _Ids:
    def __init__(self) -> None:
        self._next = 0

    def new_id(self) -> UUID:
        self._next += 1
        return UUID(int=self._next)


class World:
    def __init__(self) -> None:
        self.files: dict[UUID, FileAsset] = {}
        self.actors: list[Actor] = []
        self.storage = _Storage()
        self.ids = _Ids()
        self.actor = Actor(user_id=UUID(int=999), profile=ProfileKind.NOIVA)

    def uow_factory(self, actor: Actor) -> _UnitOfWork:
        return _UnitOfWork(self, actor)

    def use_cases(self) -> FilesUseCases:
        from wedding.modules.files.application.commands.upload_file import UploadFile
        from wedding.modules.files.application.queries.get_file import GetFile

        return FilesUseCases(
            upload_file=UploadFile(self.uow_factory, self.storage, self.ids),
            get_file=GetFile(self.uow_factory, self.storage),
        )


@pytest.fixture
def world() -> World:
    return World()
