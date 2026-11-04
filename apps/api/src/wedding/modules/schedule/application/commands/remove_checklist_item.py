from dataclasses import dataclass
from uuid import UUID

from wedding.modules.schedule.application.dto import ScheduleDto
from wedding.modules.schedule.application.ports import ScheduleUnitOfWorkFactory
from wedding.modules.schedule.application.schedule_map import (
    ScheduleReader,
    require_checklist_item,
)
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.clock import Clock
from wedding.shared_kernel.errors import VersionConflict


@dataclass(frozen=True)
class RemoveChecklistItemCommand:
    item_id: UUID
    version: int


class RemoveChecklistItem:
    def __init__(
        self, uow_factory: ScheduleUnitOfWorkFactory, clock: Clock, reader: ScheduleReader
    ) -> None:
        self._uow_factory = uow_factory
        self._clock = clock
        self._reader = reader

    def execute(self, command: RemoveChecklistItemCommand, actor: Actor) -> ScheduleDto:
        """Exclusão lógica do item, sem restaurar (F-CRN-07): o dono não é tocado e as posições dos
        outros itens não mudam (a próxima reordenação as deixa densas)."""
        with self._uow_factory(actor) as uow:
            item = require_checklist_item(uow.schedule, command.item_id)
            if item.version != command.version:
                raise VersionConflict()
            item.delete(self._clock.now(), actor.user_id)
            uow.commit()
            return self._reader.read(uow.schedule, actor)
