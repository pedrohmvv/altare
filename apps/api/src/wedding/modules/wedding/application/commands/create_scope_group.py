from dataclasses import dataclass

from wedding.modules.wedding.application.ports import ScopeUnitOfWorkFactory
from wedding.modules.wedding.application.scope_dto import ScopeMapDto
from wedding.modules.wedding.application.scope_map import build_scope_map
from wedding.modules.wedding.domain.errors import DuplicateScopeName
from wedding.modules.wedding.domain.scope_entities import ScopeGroup
from wedding.modules.wedding.domain.scope_values import Origin
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.ids import IdGenerator


@dataclass(frozen=True)
class CreateScopeGroupCommand:
    name: str


class CreateScopeGroup:
    def __init__(self, uow_factory: ScopeUnitOfWorkFactory, ids: IdGenerator) -> None:
        self._uow_factory = uow_factory
        self._ids = ids

    def execute(self, command: CreateScopeGroupCommand, actor: Actor) -> ScopeMapDto:
        with self._uow_factory(actor) as uow:
            group = ScopeGroup(
                id=self._ids.new_id(),
                name=command.name,
                position=uow.scope.next_group_position(),
                origin=Origin.COUPLE,
            )
            if uow.scope.group_name_taken(group.name_key):
                raise DuplicateScopeName()
            uow.scope.add_group(group)
            uow.commit()
            return build_scope_map(uow.scope)
