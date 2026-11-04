from dataclasses import dataclass
from uuid import UUID

from wedding.modules.schedule.application.dto import ScheduleDto
from wedding.modules.schedule.application.ports import ScheduleUnitOfWorkFactory
from wedding.modules.schedule.application.schedule_map import ScheduleReader, require_task
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.clock import Clock
from wedding.shared_kernel.errors import VersionConflict


@dataclass(frozen=True)
class DeleteTaskCommand:
    task_id: UUID
    version: int


class DeleteTask:
    def __init__(
        self, uow_factory: ScheduleUnitOfWorkFactory, clock: Clock, reader: ScheduleReader
    ) -> None:
        self._uow_factory = uow_factory
        self._clock = clock
        self._reader = reader

    def execute(self, command: DeleteTaskCommand, actor: Actor) -> ScheduleDto:
        """Exclusão lógica (F-CRN-06). Os itens do checklist não são apagados: ficam escondidos
        com o dono e voltam com ele ao restaurar."""
        with self._uow_factory(actor) as uow:
            task = require_task(uow.schedule, command.task_id)
            if task.version != command.version:
                raise VersionConflict()
            task.delete(self._clock.now(), actor.user_id)
            uow.commit()
            return self._reader.read(uow.schedule, actor)
