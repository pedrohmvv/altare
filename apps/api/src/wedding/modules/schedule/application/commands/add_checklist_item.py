from dataclasses import dataclass
from uuid import UUID

from wedding.modules.schedule.application.dto import ScheduleDto
from wedding.modules.schedule.application.ports import ScheduleUnitOfWorkFactory
from wedding.modules.schedule.application.schedule_map import (
    ScheduleReader,
    require_checklist_owner,
)
from wedding.modules.schedule.domain.entities import ChecklistItem
from wedding.modules.schedule.domain.errors import ChecklistFull
from wedding.modules.schedule.domain.values import MAX_CHECKLIST_ITEMS, OwnerKind
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.ids import IdGenerator


@dataclass(frozen=True)
class AddChecklistItemCommand:
    owner_kind: OwnerKind
    owner_id: UUID
    text: str


class AddChecklistItem:
    def __init__(
        self, uow_factory: ScheduleUnitOfWorkFactory, ids: IdGenerator, reader: ScheduleReader
    ) -> None:
        self._uow_factory = uow_factory
        self._ids = ids
        self._reader = reader

    def execute(self, command: AddChecklistItemCommand, actor: Actor) -> ScheduleDto:
        """Acrescenta um item não feito ao fim do checklist do marco ou da avulsa (F-CRN-07). A
        posição é a maior viva mais um (0 se vazio); com 50 itens vivos, 422 `checklist_full`. O
        dono não é tocado: o estado e a `version` dele ficam como estavam."""
        with self._uow_factory(actor) as uow:
            owner = require_checklist_owner(uow.schedule, command.owner_kind, command.owner_id)
            live = uow.schedule.live_items_of(command.owner_kind, owner.id)
            if len(live) >= MAX_CHECKLIST_ITEMS:
                raise ChecklistFull()
            position = max((item.position for item in live), default=-1) + 1
            uow.schedule.add_checklist_item(
                ChecklistItem.of_owner(
                    self._ids.new_id(), command.owner_kind, owner.id, command.text, position
                )
            )
            uow.commit()
            return self._reader.read(uow.schedule, actor)
