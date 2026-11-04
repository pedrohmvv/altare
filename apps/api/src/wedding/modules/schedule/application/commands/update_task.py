from dataclasses import dataclass
from datetime import date
from uuid import UUID

from wedding.modules.schedule.application.dto import ScheduleDto
from wedding.modules.schedule.application.ports import ScheduleUnitOfWorkFactory
from wedding.modules.schedule.application.schedule_map import ScheduleReader, require_task
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.errors import VersionConflict
from wedding.shared_kernel.profile import ProfileKind


@dataclass(frozen=True)
class UpdateTaskCommand:
    task_id: UUID
    title: str
    responsible: ProfileKind
    note: str | None
    target_date: date | None
    version: int


class UpdateTask:
    def __init__(self, uow_factory: ScheduleUnitOfWorkFactory, reader: ScheduleReader) -> None:
        self._uow_factory = uow_factory
        self._reader = reader

    def execute(self, command: UpdateTaskCommand, actor: Actor) -> ScheduleDto:
        """Substituição inteira de título, responsável, nota e prazo (F-CRN-06). A `version` é a que
        a tela viu; repetir os mesmos valores não grava nada."""
        with self._uow_factory(actor) as uow:
            task = require_task(uow.schedule, command.task_id)
            if task.version != command.version:
                raise VersionConflict()
            if task.edit(command.title, command.responsible, command.note, command.target_date):
                uow.commit()
            return self._reader.read(uow.schedule, actor)
