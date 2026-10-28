from wedding.modules.wedding.application.dto import BaselineChangeDto
from wedding.modules.wedding.application.ports import WeddingUnitOfWorkFactory
from wedding.shared_kernel.actor import Actor

DEFAULT_LIMIT = 50


class ListBaselineChanges:
    def __init__(self, uow_factory: WeddingUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    def execute(self, actor: Actor, limit: int = DEFAULT_LIMIT) -> list[BaselineChangeDto]:
        with self._uow_factory(actor) as uow:
            return uow.baseline.changes(limit)
