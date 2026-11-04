from dataclasses import dataclass
from uuid import UUID

from wedding.modules.schedule.application.dto import ScheduleDto
from wedding.modules.schedule.application.ports import ScheduleUnitOfWorkFactory
from wedding.modules.schedule.application.schedule_map import ScheduleReader
from wedding.modules.schedule.domain.errors import InvalidPhaseOrder
from wedding.shared_kernel.actor import Actor


@dataclass(frozen=True)
class ReorderPhasesCommand:
    ids: tuple[UUID, ...]


class ReorderPhases:
    def __init__(self, uow_factory: ScheduleUnitOfWorkFactory, reader: ScheduleReader) -> None:
        self._uow_factory = uow_factory
        self._reader = reader

    def execute(self, command: ReorderPhasesCommand, actor: Actor) -> ScheduleDto:
        """A lista precisa ser exatamente as fases vivas, sem repetir e sem faltar; a posição de
        cada fase vira o índice dela (a partir de zero) e só sobe a `version` de quem mudou."""
        with self._uow_factory(actor) as uow:
            phases = {phase.id: phase for phase in uow.schedule.list_phases()}
            if len(command.ids) != len(set(command.ids)) or set(command.ids) != phases.keys():
                raise InvalidPhaseOrder()
            for position, phase_id in enumerate(command.ids):
                phases[phase_id].position = position
            uow.commit()
            return self._reader.read(uow.schedule, actor)
