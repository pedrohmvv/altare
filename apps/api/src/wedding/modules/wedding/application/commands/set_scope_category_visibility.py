from dataclasses import dataclass
from uuid import UUID

from wedding.modules.wedding.application.ports import ScopeUnitOfWorkFactory
from wedding.modules.wedding.application.scope_dto import ScopeMapDto
from wedding.modules.wedding.application.scope_map import build_scope_map, require_category
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.clock import Clock
from wedding.shared_kernel.errors import VersionConflict


@dataclass(frozen=True)
class SetScopeCategoryVisibilityCommand:
    category_id: UUID
    hidden: bool
    version: int


class SetScopeCategoryVisibility:
    def __init__(self, uow_factory: ScopeUnitOfWorkFactory, clock: Clock) -> None:
        self._uow_factory = uow_factory
        self._clock = clock

    def execute(self, command: SetScopeCategoryVisibilityCommand, actor: Actor) -> ScopeMapDto:
        with self._uow_factory(actor) as uow:
            category = require_category(uow.scope, command.category_id)
            if category.version != command.version:
                raise VersionConflict()
            if category.set_hidden(command.hidden, self._clock.now()):
                uow.commit()
            return build_scope_map(uow.scope)
