from dataclasses import dataclass
from uuid import UUID

from wedding.modules.schedule.application.dto import CreatedMilestoneDto
from wedding.modules.schedule.application.ports import CategoryReader, ScheduleUnitOfWorkFactory
from wedding.modules.schedule.application.schedule_map import (
    ScheduleReader,
    require_linkable_category,
    require_milestone,
    require_phase,
)
from wedding.modules.schedule.domain.entities import Milestone, MilestoneDependency
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.ids import IdGenerator
from wedding.shared_kernel.profile import ProfileKind


@dataclass(frozen=True)
class CreateMilestoneCommand:
    title: str
    phase_id: UUID
    responsible: ProfileKind
    category_id: UUID | None
    depends_on: tuple[UUID, ...]


class CreateMilestone:
    def __init__(
        self,
        uow_factory: ScheduleUnitOfWorkFactory,
        ids: IdGenerator,
        reader: ScheduleReader,
        categories: CategoryReader,
    ) -> None:
        self._uow_factory = uow_factory
        self._ids = ids
        self._reader = reader
        self._categories = categories

    def execute(self, command: CreateMilestoneCommand, actor: Actor) -> CreatedMilestoneDto:
        """Cria um marco no fim da fase, sem estado marcado nem prazo (F-CRN-01). A categoria é do
        Mapa e não pode estar oculta; os predecessores são marcos vivos, e uma lista repetida vale
        como conjunto. Um marco novo não tem dependentes, então nenhuma dependência fecha ciclo.
        Devolve o cronograma e o id do marco criado."""
        with self._uow_factory(actor) as uow:
            phase = require_phase(uow.schedule, command.phase_id)
            require_linkable_category(self._categories.categories(actor), command.category_id)
            predecessors = [
                require_milestone(uow.schedule, predecessor).id
                for predecessor in dict.fromkeys(command.depends_on)
            ]
            milestone = Milestone(
                id=self._ids.new_id(),
                phase_id=phase.id,
                title=command.title,
                position=uow.schedule.next_milestone_position(phase.id),
                responsible=command.responsible,
                category_id=command.category_id,
            )
            uow.schedule.add_milestone(milestone)
            for predecessor in predecessors:
                uow.schedule.add_link(
                    MilestoneDependency(self._ids.new_id(), milestone.id, predecessor)
                )
            uow.commit()
            return CreatedMilestoneDto(self._reader.read(uow.schedule, actor), milestone.id)
