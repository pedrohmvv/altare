from wedding.modules.wedding.application.ports import ScopeUnitOfWorkFactory
from wedding.modules.wedding.application.scope_dto import ScopeMapDto
from wedding.modules.wedding.application.scope_map import build_scope_map
from wedding.shared_kernel.actor import Actor


class GetScopeMap:
    def __init__(self, uow_factory: ScopeUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    def execute(self, actor: Actor) -> ScopeMapDto:
        with self._uow_factory(actor) as uow:
            return build_scope_map(uow.scope)
