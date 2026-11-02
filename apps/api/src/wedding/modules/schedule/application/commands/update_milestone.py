from dataclasses import dataclass
from datetime import date
from uuid import UUID

from wedding.modules.schedule.application.dto import ScheduleDto
from wedding.modules.schedule.application.ports import ScheduleUnitOfWorkFactory
from wedding.modules.schedule.application.schedule_map import ScheduleReader, require_milestone
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.errors import VersionConflict
from wedding.shared_kernel.profile import ProfileKind


@dataclass(frozen=True)
class UpdateMilestoneCommand:
    milestone_id: UUID
    responsible: ProfileKind
    note: str | None
    target_date: date | None
    version: int


class UpdateMilestone:
    def __init__(self, uow_factory: ScheduleUnitOfWorkFactory, reader: ScheduleReader) -> None:
        self._uow_factory = uow_factory
        self._reader = reader

    def execute(self, command: UpdateMilestoneCommand, actor: Actor) -> ScheduleDto:
        """Qualquer um dos dois edita responsável, nota e prazo-alvo (F-CRN-01, regra 2). A
        `version` enviada precisa ser a que a tela viu; repetir os mesmos valores não grava nada
        e devolve o cronograma como está."""
        with self._uow_factory(actor) as uow:
            milestone = require_milestone(uow.schedule, command.milestone_id)
            if milestone.version != command.version:
                raise VersionConflict()
            if milestone.edit(command.responsible, command.note, command.target_date):
                uow.commit()
            return self._reader.read(uow.schedule, actor)
