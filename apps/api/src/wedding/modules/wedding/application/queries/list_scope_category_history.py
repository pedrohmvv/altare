from uuid import UUID

from wedding.modules.wedding.application.ports import ScopeUnitOfWorkFactory
from wedding.modules.wedding.application.scope_dto import StatusChangeDto
from wedding.modules.wedding.application.scope_map import require_category
from wedding.shared_kernel.actor import Actor


class ListScopeCategoryHistory:
    def __init__(self, uow_factory: ScopeUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    def execute(self, category_id: UUID, actor: Actor) -> list[StatusChangeDto]:
        with self._uow_factory(actor) as uow:
            require_category(uow.scope, category_id)
            return uow.scope.status_history(category_id)
