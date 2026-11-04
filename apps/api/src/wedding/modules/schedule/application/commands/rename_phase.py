from dataclasses import dataclass
from uuid import UUID

from wedding.modules.schedule.application.dto import ScheduleDto
from wedding.modules.schedule.application.ports import ScheduleUnitOfWorkFactory
from wedding.modules.schedule.application.schedule_map import ScheduleReader, require_phase
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.errors import VersionConflict


@dataclass(frozen=True)
class RenamePhaseCommand:
    phase_id: UUID
    title: str
    version: int


class RenamePhase:
    def __init__(self, uow_factory: ScheduleUnitOfWorkFactory, reader: ScheduleReader) -> None:
        self._uow_factory = uow_factory
        self._reader = reader

    def execute(self, command: RenamePhaseCommand, actor: Actor) -> ScheduleDto:
        """Renomear não toca nos marcos da fase (F-CRN-01). Repetir o título não grava nada."""
        with self._uow_factory(actor) as uow:
            phase = require_phase(uow.schedule, command.phase_id)
            if phase.version != command.version:
                raise VersionConflict()
            if phase.rename(command.title):
                uow.commit()
            return self._reader.read(uow.schedule, actor)
