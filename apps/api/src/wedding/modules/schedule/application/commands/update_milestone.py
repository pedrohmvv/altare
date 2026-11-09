from dataclasses import dataclass
from datetime import date
from uuid import UUID

from wedding.modules.schedule.application.dto import ScheduleDto
from wedding.modules.schedule.application.ports import CategoryReader, ScheduleUnitOfWorkFactory
from wedding.modules.schedule.application.schedule_map import (
    ScheduleReader,
    require_linkable_category,
    require_milestone,
    require_phase,
)
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.errors import VersionConflict
from wedding.shared_kernel.profile import ProfileKind


@dataclass(frozen=True)
class UpdateMilestoneCommand:
    milestone_id: UUID
    title: str
    phase_id: UUID
    responsible: ProfileKind
    category_id: UUID | None
    note: str | None
    target_date: date | None
    version: int


class UpdateMilestone:
    def __init__(
        self,
        uow_factory: ScheduleUnitOfWorkFactory,
        reader: ScheduleReader,
        categories: CategoryReader,
    ) -> None:
        self._uow_factory = uow_factory
        self._reader = reader
        self._categories = categories

    def execute(self, command: UpdateMilestoneCommand, actor: Actor) -> ScheduleDto:
        """Qualquer um dos dois edita título, fase, categoria, responsável, nota e prazo-alvo
        (F-CRN-01, regra 2). Mudar de fase leva o marco para o fim da nova, sem mexer nas
        dependências; trocar a categoria muda o efeito derivado (F-CRN-04), nunca o estado
        marcado; o marco arquivado também se edita. A `version` enviada precisa ser a que a tela
        viu; repetir os mesmos valores não grava nada."""
        with self._uow_factory(actor) as uow:
            milestone = require_milestone(uow.schedule, command.milestone_id)
            if milestone.version != command.version:
                raise VersionConflict()
            phase = require_phase(uow.schedule, command.phase_id)
            require_linkable_category(
                self._categories.categories(actor), command.category_id, milestone.category_id
            )
            changed = [
                milestone.rename(command.title),
                milestone.link_category(command.category_id),
                milestone.edit(command.responsible, command.note, command.target_date),
            ]
            if phase.id != milestone.phase_id:
                position = uow.schedule.next_milestone_position(phase.id)
                changed.append(milestone.move_to(phase.id, position))
            if any(changed):
                uow.commit()
            return self._reader.read(uow.schedule, actor)
