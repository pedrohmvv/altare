from dataclasses import dataclass
from uuid import UUID

from wedding.modules.wedding.application.ports import ScopeUnitOfWorkFactory
from wedding.modules.wedding.application.scope_dto import ScopeMapDto
from wedding.modules.wedding.application.scope_map import build_scope_map
from wedding.modules.wedding.domain.errors import GroupNotEmpty
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.clock import Clock
from wedding.shared_kernel.errors import NotFound, VersionConflict


@dataclass(frozen=True)
class DeleteScopeGroupCommand:
    group_id: UUID
    version: int


class DeleteScopeGroup:
    def __init__(self, uow_factory: ScopeUnitOfWorkFactory, clock: Clock) -> None:
        self._uow_factory = uow_factory
        self._clock = clock

    def execute(self, command: DeleteScopeGroupCommand, actor: Actor) -> ScopeMapDto:
        """Só sai o grupo do casal e vazio: o do catálogo se oculta e as frentes não ficam órfãs."""
        with self._uow_factory(actor) as uow:
            group = uow.scope.get_group(command.group_id)
            if group is None:
                raise NotFound()
            if group.version != command.version:
                raise VersionConflict()
            group.delete(self._clock.now(), actor.user_id)
            if uow.scope.count_categories(group.id) > 0:
                raise GroupNotEmpty()
            uow.commit()
            return build_scope_map(uow.scope)
