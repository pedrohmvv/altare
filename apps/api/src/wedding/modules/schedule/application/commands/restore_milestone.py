from dataclasses import dataclass
from uuid import UUID

from wedding.modules.schedule.application.dto import LeftOutDirection, LeftOutDto, RestoreDto
from wedding.modules.schedule.application.ports import ScheduleUnitOfWorkFactory
from wedding.modules.schedule.application.schedule_map import ScheduleReader, require_phase
from wedding.modules.schedule.domain.entities import MilestoneDependency
from wedding.modules.schedule.domain.graph import split_restorable
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.errors import NotFound


@dataclass(frozen=True)
class RestoreMilestoneCommand:
    milestone_id: UUID


class RestoreMilestone:
    def __init__(self, uow_factory: ScheduleUnitOfWorkFactory, reader: ScheduleReader) -> None:
        self._uow_factory = uow_factory
        self._reader = reader

    def execute(self, command: RestoreMilestoneCommand, actor: Actor) -> RestoreDto:
        """Desfaz a exclusão: o marco volta ao fim da fase em que estava e traz os vínculos que
        saíram com ele (o mesmo carimbo). Não volta o vínculo cuja outra ponta está excluída nem o
        que hoje fecharia um ciclo; a resposta diz quais ficaram de fora."""
        with self._uow_factory(actor) as uow:
            milestone = uow.schedule.get_milestone(command.milestone_id, include_deleted=True)
            if milestone is None or milestone.deleted_at is None:
                raise NotFound()
            stamp = milestone.deleted_at
            phase = require_phase(uow.schedule, milestone.phase_id)
            milestone.restore(uow.schedule.next_milestone_position(phase.id))

            # Primeiro as dependências do marco, depois quem dependia dele, em ordem fixa.
            together = sorted(
                (
                    link
                    for link in uow.schedule.deleted_links_of(milestone.id)
                    if link.deleted_at == stamp
                ),
                key=lambda link: (
                    link.milestone_id != milestone.id,
                    link.milestone_id,
                    link.depends_on_id,
                ),
            )
            others = {}
            for link in together:
                other_id = _other_end(link, milestone.id)
                other = uow.schedule.get_milestone(other_id, include_deleted=True)
                if other is None:
                    raise RuntimeError(f"Vínculo {link.id} aponta para um marco que não existe")
                others[link.id] = other
            reachable = [link for link in together if others[link.id].deleted_at is None]
            accepted, _ = split_restorable(
                uow.schedule.dependencies(), [link.as_edge() for link in reachable]
            )
            restored = set(accepted)
            left_out = []
            for link in together:
                if link in reachable and link.as_edge() in restored:
                    link.restore()
                    if link.milestone_id != milestone.id:
                        # O dependente ganhou o predecessor de volta: a `version` dele sobe.
                        others[link.id].touch_dependencies()
                else:
                    other = others[link.id]
                    depends_on = link.milestone_id == milestone.id
                    direction = (
                        LeftOutDirection.DEPENDS_ON
                        if depends_on
                        else LeftOutDirection.DEPENDENCY_OF
                    )
                    left_out.append(LeftOutDto(other.id, other.title, direction))
            uow.commit()
            return RestoreDto(self._reader.read(uow.schedule, actor), tuple(left_out))


def _other_end(link: MilestoneDependency, milestone_id: UUID) -> UUID:
    return link.depends_on_id if link.milestone_id == milestone_id else link.milestone_id
