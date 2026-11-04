from dataclasses import dataclass
from uuid import UUID

from wedding.modules.schedule.application.dto import ScheduleDto
from wedding.modules.schedule.application.ports import ScheduleUnitOfWorkFactory
from wedding.modules.schedule.application.schedule_map import (
    ScheduleReader,
    require_checklist_owner,
)
from wedding.modules.schedule.domain.errors import InvalidChecklistOrder
from wedding.modules.schedule.domain.values import OwnerKind
from wedding.shared_kernel.actor import Actor


@dataclass(frozen=True)
class ReorderChecklistCommand:
    owner_kind: OwnerKind
    owner_id: UUID
    ids: tuple[UUID, ...]


class ReorderChecklist:
    def __init__(self, uow_factory: ScheduleUnitOfWorkFactory, reader: ScheduleReader) -> None:
        self._uow_factory = uow_factory
        self._reader = reader

    def execute(self, command: ReorderChecklistCommand, actor: Actor) -> ScheduleDto:
        """A lista precisa ser exatamente os itens vivos do dono, sem repetir e sem faltar (422
        `invalid_checklist_order`); sem `version`, como reordenar fases: o último a gravar vence. A
        posição de cada item vira o índice dele (a partir de zero), só entre os vivos."""
        with self._uow_factory(actor) as uow:
            owner = require_checklist_owner(uow.schedule, command.owner_kind, command.owner_id)
            live = {
                item.id: item for item in uow.schedule.live_items_of(command.owner_kind, owner.id)
            }
            if len(command.ids) != len(set(command.ids)) or set(command.ids) != live.keys():
                raise InvalidChecklistOrder()
            for position, item_id in enumerate(command.ids):
                live[item_id].position = position
            uow.commit()
            return self._reader.read(uow.schedule, actor)
