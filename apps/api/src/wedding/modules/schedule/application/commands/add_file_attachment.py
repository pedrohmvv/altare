from dataclasses import dataclass
from uuid import UUID

from wedding.modules.schedule.application.dto import ScheduleDto
from wedding.modules.schedule.application.ports import AttachmentFiles, ScheduleUnitOfWorkFactory
from wedding.modules.schedule.application.schedule_map import (
    ScheduleReader,
    require_checklist_owner,
)
from wedding.modules.schedule.domain.attachments import Attachment
from wedding.modules.schedule.domain.values import OwnerKind
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.errors import NotFound
from wedding.shared_kernel.ids import IdGenerator


@dataclass(frozen=True)
class AddFileAttachmentCommand:
    owner_kind: OwnerKind
    owner_id: UUID
    file_id: UUID
    title: str | None
    comment: str | None


class AddFileAttachment:
    def __init__(
        self,
        uow_factory: ScheduleUnitOfWorkFactory,
        ids: IdGenerator,
        reader: ScheduleReader,
        files: AttachmentFiles,
    ) -> None:
        self._uow_factory = uow_factory
        self._ids = ids
        self._reader = reader
        self._files = files

    def execute(self, command: AddFileAttachmentCommand, actor: Actor) -> ScheduleDto:
        """O arquivo já foi enviado (`POST /files`, com o tipo conferido pela assinatura real). Aqui
        só se confere que ele existe (404) e é PDF ou imagem (422 `attachment_file_not_allowed`), e
        se copia o nome, o tipo e o tamanho para o anexo: o arquivo enviado é imutável, então a
        cópia não envelhece e a leitura não precisa consultar o `files`. O dono precisa estar
        vivo."""
        stored = self._files.find(command.file_id, actor)
        if stored is None:
            raise NotFound()
        with self._uow_factory(actor) as uow:
            owner = require_checklist_owner(uow.schedule, command.owner_kind, command.owner_id)
            uow.schedule.add_attachment(
                Attachment.new_file(
                    id=self._ids.new_id(),
                    owner_kind=command.owner_kind,
                    owner_id=owner.id,
                    profile=actor.profile,
                    file=stored,
                    title=command.title,
                    comment=command.comment,
                )
            )
            uow.commit()
            return self._reader.read(uow.schedule, actor)
