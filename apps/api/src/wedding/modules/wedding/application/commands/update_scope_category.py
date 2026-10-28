from dataclasses import dataclass
from uuid import UUID

from wedding.modules.wedding.application.ports import ScopeUnitOfWorkFactory
from wedding.modules.wedding.application.scope_dto import ScopeMapDto
from wedding.modules.wedding.application.scope_map import build_scope_map, require_category
from wedding.modules.wedding.domain.errors import DuplicateScopeName
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.errors import NotFound, VersionConflict


@dataclass(frozen=True)
class UpdateScopeCategoryCommand:
    category_id: UUID
    name: str
    group_id: UUID
    estimate_cents: int | None
    version: int


class UpdateScopeCategory:
    def __init__(self, uow_factory: ScopeUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    def execute(self, command: UpdateScopeCategoryCommand, actor: Actor) -> ScopeMapDto:
        """Nome, grupo e estimativa de uma vez, numa só versão. A estimativa fica na categoria e o
        orçamento a lê no Bloco 2.1, sem cópia (F-PLN-05)."""
        with self._uow_factory(actor) as uow:
            category = require_category(uow.scope, command.category_id)
            if category.version != command.version:
                raise VersionConflict()
            if uow.scope.get_group(command.group_id) is None:
                raise NotFound()
            if category.update(command.name, command.group_id, command.estimate_cents):
                if uow.scope.category_name_taken(category.name_key, excluding=category.id):
                    raise DuplicateScopeName()
                uow.commit()
            return build_scope_map(uow.scope)
