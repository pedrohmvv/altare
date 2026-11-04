from dataclasses import dataclass
from uuid import UUID

from wedding.modules.schedule.application.dto import ScheduleDto
from wedding.modules.schedule.application.ports import ScheduleUnitOfWorkFactory
from wedding.modules.schedule.application.schedule_map import (
    ScheduleReader,
    require_checklist_owner,
)
from wedding.modules.schedule.domain.attachments import Attachment
from wedding.modules.schedule.domain.values import OwnerKind
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.ids import IdGenerator


@dataclass(frozen=True)
class AddLinkAttachmentCommand:
    owner_kind: OwnerKind
    owner_id: UUID
    url: str
    title: str | None
    comment: str | None


class AddLinkAttachment:
    def __init__(
        self, uow_factory: ScheduleUnitOfWorkFactory, ids: IdGenerator, reader: ScheduleReader
    ) -> None:
        self._uow_factory = uow_factory
        self._ids = ids
        self._reader = reader

    def execute(self, command: AddLinkAttachmentCommand, actor: Actor) -> ScheduleDto:
        """Guarda o endereço como foi colado, depois de validado; nada é buscado na página. O dono é
        um marco ou uma avulsa vivos (404 se não existe ou foi excluído). O autor é o perfil da
        sessão. Sem limite de anexos por item, e o dono não é tocado: o estado e a `version` dele
        ficam como estavam."""
        with self._uow_factory(actor) as uow:
            owner = require_checklist_owner(uow.schedule, command.owner_kind, command.owner_id)
            uow.schedule.add_attachment(
                Attachment.new_link(
                    id=self._ids.new_id(),
                    owner_kind=command.owner_kind,
                    owner_id=owner.id,
                    profile=actor.profile,
                    url=command.url,
                    title=command.title,
                    comment=command.comment,
                )
            )
            uow.commit()
            return self._reader.read(uow.schedule, actor)
