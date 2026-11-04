from dataclasses import dataclass

from wedding.modules.schedule.application.dto import ScheduleDto
from wedding.modules.schedule.application.ports import ScheduleUnitOfWorkFactory
from wedding.modules.schedule.application.schedule_map import ScheduleReader
from wedding.modules.schedule.domain.entities import Phase
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.ids import IdGenerator


@dataclass(frozen=True)
class CreatePhaseCommand:
    title: str


class CreatePhase:
    def __init__(
        self, uow_factory: ScheduleUnitOfWorkFactory, ids: IdGenerator, reader: ScheduleReader
    ) -> None:
        self._uow_factory = uow_factory
        self._ids = ids
        self._reader = reader

    def execute(self, command: CreatePhaseCommand, actor: Actor) -> ScheduleDto:
        """A fase nova vai para o fim da lista, vazia (F-CRN-01)."""
        with self._uow_factory(actor) as uow:
            phase = Phase(self._ids.new_id(), command.title, uow.schedule.next_phase_position())
            uow.schedule.add_phase(phase)
            uow.commit()
            return self._reader.read(uow.schedule, actor)
