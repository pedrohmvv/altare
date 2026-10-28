from dataclasses import dataclass
from uuid import UUID

from wedding.modules.wedding.application.ports import ScopeUnitOfWorkFactory
from wedding.modules.wedding.application.scope_dto import ScopeMapDto
from wedding.modules.wedding.application.scope_map import build_scope_map
from wedding.modules.wedding.domain.errors import DuplicateScopeName
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.errors import NotFound, VersionConflict


@dataclass(frozen=True)
class RenameScopeGroupCommand:
    group_id: UUID
    name: str
    version: int


class RenameScopeGroup:
    def __init__(self, uow_factory: ScopeUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    def execute(self, command: RenameScopeGroupCommand, actor: Actor) -> ScopeMapDto:
        with self._uow_factory(actor) as uow:
            group = uow.scope.get_group(command.group_id)
            if group is None:
                raise NotFound()
            if group.version != command.version:
                raise VersionConflict()
            if group.rename(command.name):
                if uow.scope.group_name_taken(group.name_key, excluding=group.id):
                    raise DuplicateScopeName()
                uow.commit()
            return build_scope_map(uow.scope)
