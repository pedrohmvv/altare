from dataclasses import dataclass
from uuid import UUID

from wedding.modules.schedule.application.dto import ScheduleDto
from wedding.modules.schedule.application.ports import ScheduleUnitOfWorkFactory
from wedding.modules.schedule.application.schedule_map import ScheduleReader, require_attachment
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.clock import Clock


@dataclass(frozen=True)
class RemoveAttachmentCommand:
    attachment_id: UUID


class RemoveAttachment:
    def __init__(
        self, uow_factory: ScheduleUnitOfWorkFactory, clock: Clock, reader: ScheduleReader
    ) -> None:
        self._uow_factory = uow_factory
        self._clock = clock
        self._reader = reader

    def execute(self, command: RemoveAttachmentCommand, actor: Actor) -> ScheduleDto:
        """Remoção lógica, só do autor (F-CRN-08, regra 3): a linha fica guardada e não há como
        restaurar pela tela. Com o dono excluído o anexo não é alcançável (404), e o dono não é
        tocado."""
        with self._uow_factory(actor) as uow:
            attachment = require_attachment(uow.schedule, command.attachment_id)
            attachment.remove(actor.profile, actor.user_id, self._clock.now())
            uow.commit()
            return self._reader.read(uow.schedule, actor)
