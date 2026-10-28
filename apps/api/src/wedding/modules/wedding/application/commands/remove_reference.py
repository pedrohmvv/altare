from dataclasses import dataclass
from uuid import UUID

from wedding.modules.wedding.application.ports import ReferenceUnitOfWorkFactory
from wedding.modules.wedding.application.reference_map import to_reference_dto
from wedding.modules.wedding.application.scope_dto import ReferenceDto
from wedding.modules.wedding.application.scope_map import require_category
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.clock import Clock
from wedding.shared_kernel.errors import NotFound


@dataclass(frozen=True)
class RemoveReferenceCommand:
    category_id: UUID
    reference_id: UUID


class RemoveReference:
    def __init__(self, uow_factory: ReferenceUnitOfWorkFactory, clock: Clock) -> None:
        self._uow_factory = uow_factory
        self._clock = clock

    def execute(self, command: RemoveReferenceCommand, actor: Actor) -> list[ReferenceDto]:
        """Remoção lógica, só do autor (F-PLN-06, regra 2): a linha fica guardada."""
        with self._uow_factory(actor) as uow:
            category = require_category(uow.scope, command.category_id)
            reference = uow.references.get(command.reference_id)
            if reference is None or reference.category_id != category.id:
                raise NotFound()
            reference.remove(actor.profile, actor.user_id, self._clock.now())
            uow.commit()
            return [
                to_reference_dto(r, actor, self._clock.now())
                for r in uow.references.list_for(category.id)
            ]
