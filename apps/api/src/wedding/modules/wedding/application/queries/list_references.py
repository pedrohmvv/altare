from uuid import UUID

from wedding.modules.wedding.application.ports import ReferenceUnitOfWorkFactory
from wedding.modules.wedding.application.reference_map import to_reference_dto
from wedding.modules.wedding.application.scope_dto import ReferenceDto
from wedding.modules.wedding.application.scope_map import require_category
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.clock import Clock


class ListReferences:
    def __init__(self, uow_factory: ReferenceUnitOfWorkFactory, clock: Clock) -> None:
        self._uow_factory = uow_factory
        self._clock = clock

    def execute(self, category_id: UUID, actor: Actor) -> list[ReferenceDto]:
        with self._uow_factory(actor) as uow:
            category = require_category(uow.scope, category_id)
            return [
                to_reference_dto(r, actor, self._clock.now())
                for r in uow.references.list_for(category.id)
            ]
