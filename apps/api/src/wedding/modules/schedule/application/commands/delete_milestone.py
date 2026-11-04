from dataclasses import dataclass
from uuid import UUID

from wedding.modules.schedule.application.dto import ScheduleDto
from wedding.modules.schedule.application.ports import ScheduleUnitOfWorkFactory
from wedding.modules.schedule.application.schedule_map import ScheduleReader, require_milestone
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.clock import Clock
from wedding.shared_kernel.errors import VersionConflict


@dataclass(frozen=True)
class DeleteMilestoneCommand:
    milestone_id: UUID
    version: int


class DeleteMilestone:
    def __init__(
        self, uow_factory: ScheduleUnitOfWorkFactory, clock: Clock, reader: ScheduleReader
    ) -> None:
        self._uow_factory = uow_factory
        self._clock = clock
        self._reader = reader

    def execute(self, command: DeleteMilestoneCommand, actor: Actor) -> ScheduleDto:
        """Exclusão lógica (F-CRN-01, regra 1). Os vínculos em que o marco aparece, nos dois
        sentidos, são desativados com o mesmo carimbo dele, o que permite restaurá-los juntos; os
        dependentes mantêm as demais dependências, o estado deles se recalcula na leitura e a
        `version` deles sobe, porque o conjunto de predecessores mudou. O histórico fica."""
        with self._uow_factory(actor) as uow:
            milestone = require_milestone(uow.schedule, command.milestone_id)
            if milestone.version != command.version:
                raise VersionConflict()
            now = self._clock.now()
            milestone.delete(now, actor.user_id)
            for link in uow.schedule.live_links_of(milestone.id):
                link.delete(now, actor.user_id)
                if link.milestone_id != milestone.id:
                    # O dependente perdeu um predecessor: quem editava as dependências dele com a
                    # version de antes recebe o conflito.
                    dependent = require_milestone(uow.schedule, link.milestone_id)
                    dependent.touch_dependencies()
            uow.commit()
            return self._reader.read(uow.schedule, actor)
