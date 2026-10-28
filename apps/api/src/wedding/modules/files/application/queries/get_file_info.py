from uuid import UUID

from wedding.modules.files.application.dto import FileAssetDto, to_dto
from wedding.modules.files.application.ports import FilesUnitOfWorkFactory
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.errors import NotFound


class GetFileInfo:
    """Os dados de um arquivo, sem abrir o conteúdo. É o que outro módulo precisa para apontar para
    ele (por exemplo, conferir que uma referência é uma imagem) sem conhecer o armazenamento."""

    def __init__(self, uow_factory: FilesUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    def execute(self, file_id: UUID, actor: Actor) -> FileAssetDto:
        with self._uow_factory(actor) as uow:
            file = uow.files.get(file_id)
            if file is None:
                raise NotFound()
            return to_dto(file)
