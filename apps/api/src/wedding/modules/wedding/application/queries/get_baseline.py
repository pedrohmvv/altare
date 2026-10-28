from wedding.modules.wedding.application.dto import BaselineDto, to_baseline_dto
from wedding.modules.wedding.application.ports import WeddingUnitOfWorkFactory
from wedding.shared_kernel.actor import Actor


class GetBaseline:
    def __init__(self, uow_factory: WeddingUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    def execute(self, actor: Actor) -> BaselineDto:
        with self._uow_factory(actor) as uow:
            return to_baseline_dto(uow.baseline.all())
