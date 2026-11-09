from dataclasses import dataclass
from uuid import UUID

from wedding.modules.schedule.application.dto import ScheduleDto
from wedding.modules.schedule.application.ports import ScheduleUnitOfWorkFactory
from wedding.modules.schedule.application.schedule_map import ScheduleReader, require_milestone
from wedding.modules.schedule.domain.entities import MilestoneDependency
from wedding.modules.schedule.domain.errors import DependencyCycle, SelfDependency
from wedding.modules.schedule.domain.graph import find_cycle
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.clock import Clock
from wedding.shared_kernel.errors import NotFound, VersionConflict
from wedding.shared_kernel.ids import IdGenerator


@dataclass(frozen=True)
class SetMilestoneDependenciesCommand:
    milestone_id: UUID
    depends_on: tuple[UUID, ...]
    version: int


class SetMilestoneDependencies:
    def __init__(
        self,
        uow_factory: ScheduleUnitOfWorkFactory,
        ids: IdGenerator,
        clock: Clock,
        reader: ScheduleReader,
    ) -> None:
        self._uow_factory = uow_factory
        self._ids = ids
        self._clock = clock
        self._reader = reader

    def execute(self, command: SetMilestoneDependenciesCommand, actor: Actor) -> ScheduleDto:
        """Troca o conjunto de predecessores do marco (F-CRN-03, regra 2). Recusa a dependência do
        marco nele mesmo, o predecessor que não existe e a que fecharia um ciclo (com o caminho).
        Uma lista repetida vale como conjunto, e repetir o conjunto atual não grava nada. A
        `version` do marco é conferida e sobe junto com a revisão das dependências."""
        with self._uow_factory(actor) as uow:
            milestone = require_milestone(uow.schedule, command.milestone_id)
            if milestone.version != command.version:
                raise VersionConflict()
            wanted = list(dict.fromkeys(command.depends_on))
            if milestone.id in wanted:
                raise SelfDependency()
            titles = {item.id: item.title for item in uow.schedule.list_milestones()}
            if not set(wanted) <= titles.keys():
                raise NotFound()
            cycle = find_cycle(uow.schedule.dependencies(), milestone.id, wanted)
            if cycle is not None:
                raise DependencyCycle([(step, titles[step]) for step in cycle])

            current = [
                link
                for link in uow.schedule.live_links_of(milestone.id)
                if link.milestone_id == milestone.id
            ]
            if {link.depends_on_id for link in current} == set(wanted):
                return self._reader.read(uow.schedule, actor)
            now = self._clock.now()
            for link in current:
                if link.depends_on_id not in wanted:
                    link.delete(now, actor.user_id)
            kept = {link.depends_on_id for link in current if link.depends_on_id in wanted}
            for predecessor in wanted:
                if predecessor not in kept:
                    uow.schedule.add_link(
                        MilestoneDependency(self._ids.new_id(), milestone.id, predecessor)
                    )
            milestone.touch_dependencies()
            uow.commit()
            return self._reader.read(uow.schedule, actor)
