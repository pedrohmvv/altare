from dataclasses import dataclass
from uuid import UUID

from wedding.modules.wedding.application.ports import ScopeUnitOfWorkFactory
from wedding.modules.wedding.application.scope_dto import ScopeMapDto
from wedding.modules.wedding.application.scope_map import build_scope_map
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.clock import Clock
from wedding.shared_kernel.errors import NotFound, VersionConflict


@dataclass(frozen=True)
class SetScopeGroupVisibilityCommand:
    group_id: UUID
    hidden: bool
    version: int


class SetScopeGroupVisibility:
    def __init__(self, uow_factory: ScopeUnitOfWorkFactory, clock: Clock) -> None:
        self._uow_factory = uow_factory
        self._clock = clock

    def execute(self, command: SetScopeGroupVisibilityCommand, actor: Actor) -> ScopeMapDto:
        """Ocultar tira o grupo e as frentes dele das telas sem mudar nenhuma delas (derivado)."""
        with self._uow_factory(actor) as uow:
            group = uow.scope.get_group(command.group_id)
            if group is None:
                raise NotFound()
            if group.version != command.version:
                raise VersionConflict()
            if group.set_hidden(command.hidden, self._clock.now()):
                uow.commit()
            return build_scope_map(uow.scope)
