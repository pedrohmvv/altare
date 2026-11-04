from dataclasses import dataclass
from uuid import UUID

from wedding.modules.schedule.application.dto import ScheduleDto
from wedding.modules.schedule.application.ports import ScheduleUnitOfWorkFactory
from wedding.modules.schedule.application.schedule_map import ScheduleReader, require_milestone
from wedding.modules.schedule.domain.windows import WindowUnit
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.errors import VersionConflict


@dataclass(frozen=True)
class UpdateMilestoneWindowCommand:
    milestone_id: UUID
    start_before: int
    end_before: int
    unit: WindowUnit
    version: int


class UpdateMilestoneWindow:
    def __init__(self, uow_factory: ScheduleUnitOfWorkFactory, reader: ScheduleReader) -> None:
        self._uow_factory = uow_factory
        self._reader = reader

    def execute(self, command: UpdateMilestoneWindowCommand, actor: Actor) -> ScheduleDto:
        """O casal edita a janela de um marco (F-CRN-05, regra 5): início, fim e unidade, em
        qualquer modo, em marco arquivado e em marco que não tinha janela (C01 a C05, ou criado
        pelo casal). A janela editada deixa de ser a sugestão genérica, mesmo com os mesmos
        deslocamentos; repetir uma janela já editada não grava nada. Não mexe no prazo manual: o
        prazo efetivo se recalcula na leitura. A `version` do marco precisa ser a que a tela viu."""
        with self._uow_factory(actor) as uow:
            milestone = require_milestone(uow.schedule, command.milestone_id)
            if milestone.version != command.version:
                raise VersionConflict()
            if milestone.set_window(command.start_before, command.end_before, command.unit):
                uow.commit()
            return self._reader.read(uow.schedule, actor)
