from dataclasses import dataclass
from uuid import UUID

from wedding.modules.schedule.application.dto import ScheduleDto
from wedding.modules.schedule.application.ports import ScheduleUnitOfWorkFactory
from wedding.modules.schedule.application.schedule_map import (
    ScheduleReader,
    has_open_items,
    require_task,
)
from wedding.modules.schedule.domain.errors import ChecklistOpenItems
from wedding.modules.schedule.domain.values import OwnerKind, TaskState
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.errors import VersionConflict


@dataclass(frozen=True)
class ChangeTaskStateCommand:
    task_id: UUID
    state: TaskState
    ignore_open_items: bool
    version: int


class ChangeTaskState:
    def __init__(self, uow_factory: ScheduleUnitOfWorkFactory, reader: ScheduleReader) -> None:
        self._uow_factory = uow_factory
        self._reader = reader

    def execute(self, command: ChangeTaskStateCommand, actor: Actor) -> ScheduleDto:
        """Os três estados valem a qualquer momento, nos dois sentidos (reabrir é voltar a
        `A fazer`). Ordem: a `version` (409), repetir o estado (não grava nada nem checa nada) e, ao
        concluir com itens do checklist em aberto, a confirmação `ignore_open_items` (422
        `checklist_open_items`); com outro destino ela é ignorada. Concluir não altera os itens."""
        with self._uow_factory(actor) as uow:
            task = require_task(uow.schedule, command.task_id)
            if task.version != command.version:
                raise VersionConflict()
            if command.state is task.state:
                return self._reader.read(uow.schedule, actor)
            if (
                command.state is TaskState.DONE
                and not command.ignore_open_items
                and has_open_items(uow.schedule, OwnerKind.TASK, task.id)
            ):
                raise ChecklistOpenItems()
            task.set_state(command.state)
            uow.commit()
            return self._reader.read(uow.schedule, actor)
