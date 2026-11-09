from dataclasses import dataclass
from uuid import UUID

from wedding.modules.schedule.application.dto import ScheduleDto
from wedding.modules.schedule.application.ports import ScheduleUnitOfWorkFactory
from wedding.modules.schedule.application.schedule_map import (
    ScheduleReader,
    require_checklist_item,
)
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.errors import VersionConflict


@dataclass(frozen=True)
class UpdateChecklistItemCommand:
    item_id: UUID
    text: str
    done: bool
    version: int


class UpdateChecklistItem:
    def __init__(self, uow_factory: ScheduleUnitOfWorkFactory, reader: ScheduleReader) -> None:
        self._uow_factory = uow_factory
        self._reader = reader

    def execute(self, command: UpdateChecklistItemCommand, actor: Actor) -> ScheduleDto:
        """Marcar, desmarcar e editar o texto são a mesma substituição inteira (F-CRN-07). Usa a
        `version` do item, que sobe só com mudança real, e nunca toca o dono."""
        with self._uow_factory(actor) as uow:
            item = require_checklist_item(uow.schedule, command.item_id)
            if item.version != command.version:
                raise VersionConflict()
            if item.edit(command.text, command.done):
                uow.commit()
            return self._reader.read(uow.schedule, actor)
