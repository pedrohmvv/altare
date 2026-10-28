import hashlib
from dataclasses import dataclass

from wedding.modules.files.application.dto import FileAssetDto, to_dto
from wedding.modules.files.application.ports import FileStorage, FilesUnitOfWorkFactory
from wedding.modules.files.domain.entities import FileAsset
from wedding.modules.files.domain.rules import inspect_upload, sanitize_filename
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.ids import IdGenerator


@dataclass(frozen=True)
class UploadFileCommand:
    name: str | None
    content: bytes


class UploadFile:
    def __init__(
        self, uow_factory: FilesUnitOfWorkFactory, storage: FileStorage, ids: IdGenerator
    ) -> None:
        self._uow_factory = uow_factory
        self._storage = storage
        self._ids = ids

    def execute(self, command: UploadFileCommand, actor: Actor) -> FileAssetDto:
        kind = inspect_upload(command.content)
        sha256 = hashlib.sha256(command.content).hexdigest()
        # O conteúdo vai ao disco antes do registro: se o banco falhar depois, sobra um arquivo
        # órfão, que é inofensivo e reaproveitado num novo envio; o contrário deixaria um registro
        # sem arquivo.
        self._storage.put(sha256, command.content)
        file = FileAsset(
            id=self._ids.new_id(),
            original_name=sanitize_filename(command.name),
            kind=kind,
            size_bytes=len(command.content),
            sha256=sha256,
        )
        with self._uow_factory(actor) as uow:
            uow.files.add(file)
            uow.commit()
        return to_dto(file)
