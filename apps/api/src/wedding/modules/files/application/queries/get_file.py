from uuid import UUID

from wedding.modules.files.application.dto import FileContent, to_dto
from wedding.modules.files.application.ports import FileStorage, FilesUnitOfWorkFactory
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.errors import NotFound


class GetFile:
    def __init__(self, uow_factory: FilesUnitOfWorkFactory, storage: FileStorage) -> None:
        self._uow_factory = uow_factory
        self._storage = storage

    def execute(self, file_id: UUID, actor: Actor) -> FileContent:
        """Os dados e o conteúdo em pedaços. O casal vê todos os arquivos um do outro; o que a
        sessão garante é que ninguém de fora os veja."""
        with self._uow_factory(actor) as uow:
            file = uow.files.get(file_id)
            if file is None:
                raise NotFound()
            data = to_dto(file)
        if not self._storage.exists(data.sha256):
            raise NotFound()
        return FileContent(file=data, chunks=self._storage.read(data.sha256))
