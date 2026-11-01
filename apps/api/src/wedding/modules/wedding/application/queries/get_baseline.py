from wedding.modules.wedding.application.dto import BaselineDto, to_baseline_dto
from wedding.modules.wedding.application.ports import GuestCountReader, WeddingUnitOfWorkFactory
from wedding.shared_kernel.actor import Actor


class GetBaseline:
    def __init__(
        self, uow_factory: WeddingUnitOfWorkFactory, guest_count: GuestCountReader
    ) -> None:
        self._uow_factory = uow_factory
        self._guest_count = guest_count

    def execute(self, actor: Actor) -> BaselineDto:
        with self._uow_factory(actor) as uow:
            return to_baseline_dto(uow.baseline.all(), self._guest_count.total_nominal(actor))
