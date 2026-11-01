from dataclasses import dataclass

from wedding.modules.wedding.application.dto import BaselineDto, to_baseline_dto
from wedding.modules.wedding.application.ports import GuestCountReader, WeddingUnitOfWorkFactory
from wedding.modules.wedding.domain.entities import BaselineChange
from wedding.modules.wedding.domain.value_objects import (
    BaselineKey,
    BaselineValue,
    DefinitionStatus,
)
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.errors import NotFound, VersionConflict
from wedding.shared_kernel.ids import IdGenerator


@dataclass(frozen=True)
class UpdateBaselineFieldCommand:
    key: BaselineKey
    value: BaselineValue | None
    status: DefinitionStatus
    note: str | None
    version: int


class UpdateBaselineField:
    def __init__(
        self,
        uow_factory: WeddingUnitOfWorkFactory,
        ids: IdGenerator,
        guest_count: GuestCountReader,
    ) -> None:
        self._uow_factory = uow_factory
        self._ids = ids
        self._guest_count = guest_count

    def execute(self, command: UpdateBaselineFieldCommand, actor: Actor) -> BaselineDto:
        """Troca o estado de um campo e devolve o quadro inteiro. A `version` enviada precisa ser a
        que a tela viu; o histórico só ganha uma linha quando algo de fato mudou."""
        with self._uow_factory(actor) as uow:
            field = uow.baseline.get(command.key)
            if field is None:
                raise NotFound()
            if field.version != command.version:
                raise VersionConflict()
            before = field.snapshot()
            if field.update(command.value, command.status, command.note):
                uow.baseline.add_change(
                    BaselineChange(
                        id=self._ids.new_id(),
                        key=command.key,
                        before=before,
                        after=field.snapshot(),
                        profile=actor.profile,
                    )
                )
                uow.commit()
            return to_baseline_dto(uow.baseline.all(), self._guest_count.total_nominal(actor))
