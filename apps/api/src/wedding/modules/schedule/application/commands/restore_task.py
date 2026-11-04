from dataclasses import dataclass
from uuid import UUID

from wedding.modules.schedule.application.dto import ScheduleDto
from wedding.modules.schedule.application.ports import ScheduleUnitOfWorkFactory
from wedding.modules.schedule.application.schedule_map import ScheduleReader
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.errors import NotFound


@dataclass(frozen=True)
class RestoreTaskCommand:
    task_id: UUID


class RestoreTask:
    def __init__(self, uow_factory: ScheduleUnitOfWorkFactory, reader: ScheduleReader) -> None:
        self._uow_factory = uow_factory
        self._reader = reader

    def execute(self, command: RestoreTaskCommand, actor: Actor) -> ScheduleDto:
        """Desfaz a exclusão: a avulsa volta como estava, com o estado e os itens do checklist.
        Sem vínculos a recompor, não há o que deixar de fora."""
        with self._uow_factory(actor) as uow:
            task = uow.schedule.get_task(command.task_id, include_deleted=True)
            if task is None or task.deleted_at is None:
                raise NotFound()
            task.restore()
            uow.commit()
            return self._reader.read(uow.schedule, actor)
