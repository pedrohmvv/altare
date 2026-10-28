from collections.abc import Callable, Iterator
from types import TracebackType
from typing import Protocol, Self
from uuid import UUID

from wedding.modules.files.domain.entities import FileAsset
from wedding.shared_kernel.actor import Actor


class FileRepository(Protocol):
    def add(self, file: FileAsset) -> None: ...

    def get(self, file_id: UUID) -> FileAsset | None: ...


class FilesUnitOfWork(Protocol):
    @property
    def files(self) -> FileRepository: ...

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...


# Quem envia ou lê é sempre alguém na sessão: o ator vai para o histórico do registro.
FilesUnitOfWorkFactory = Callable[[Actor], FilesUnitOfWork]


class FileStorage(Protocol):
    """Onde o conteúdo mora, endereçado pelo SHA-256 (stack.md §3). Disco hoje, S3 depois."""

    def put(self, key: str, data: bytes) -> None: ...

    def exists(self, key: str) -> bool: ...

    def read(self, key: str) -> Iterator[bytes]: ...
