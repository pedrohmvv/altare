from dataclasses import dataclass
from uuid import UUID

from wedding.modules.wedding.application.ports import ReferenceUnitOfWorkFactory
from wedding.modules.wedding.application.reference_map import to_reference_dto
from wedding.modules.wedding.application.scope_dto import ReferenceDto
from wedding.modules.wedding.application.scope_map import require_category
from wedding.modules.wedding.domain.reference import ScopeReference
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.clock import Clock
from wedding.shared_kernel.ids import IdGenerator


@dataclass(frozen=True)
class AddLinkReferenceCommand:
    category_id: UUID
    url: str
    title: str | None
    comment: str | None


class AddLinkReference:
    def __init__(
        self, uow_factory: ReferenceUnitOfWorkFactory, ids: IdGenerator, clock: Clock
    ) -> None:
        self._uow_factory = uow_factory
        self._ids = ids
        self._clock = clock

    def execute(self, command: AddLinkReferenceCommand, actor: Actor) -> list[ReferenceDto]:
        """Guarda o endereço como foi colado, depois de validado. Nada é buscado na página."""
        with self._uow_factory(actor) as uow:
            category = require_category(uow.scope, command.category_id)
            uow.references.add(
                ScopeReference.new_link(
                    id=self._ids.new_id(),
                    category_id=category.id,
                    profile=actor.profile,
                    url=command.url,
                    title=command.title,
                    comment=command.comment,
                )
            )
            uow.commit()
            return [
                to_reference_dto(r, actor, self._clock.now())
                for r in uow.references.list_for(category.id)
            ]
