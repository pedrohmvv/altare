from dataclasses import dataclass
from uuid import UUID

from wedding.modules.wedding.application.ports import ScopeUnitOfWorkFactory
from wedding.modules.wedding.application.scope_dto import ScopeMapDto
from wedding.modules.wedding.application.scope_map import build_scope_map, require_category
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.clock import Clock
from wedding.shared_kernel.errors import VersionConflict


@dataclass(frozen=True)
class DeleteScopeCategoryCommand:
    category_id: UUID
    version: int


class DeleteScopeCategory:
    def __init__(self, uow_factory: ScopeUnitOfWorkFactory, clock: Clock) -> None:
        self._uow_factory = uow_factory
        self._clock = clock

    def execute(self, command: DeleteScopeCategoryCommand, actor: Actor) -> ScopeMapDto:
        """Exclusão lógica, só da frente do casal; as do catálogo só se ocultam. O histórico e as
        avaliações ficam guardados."""
        with self._uow_factory(actor) as uow:
            category = require_category(uow.scope, command.category_id)
            if category.version != command.version:
                raise VersionConflict()
            category.delete(self._clock.now(), actor.user_id)
            uow.commit()
            return build_scope_map(uow.scope)
