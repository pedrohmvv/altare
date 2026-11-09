from dataclasses import dataclass
from uuid import UUID

from wedding.modules.schedule.application.dto import ScheduleDto
from wedding.modules.schedule.application.ports import ScheduleUnitOfWorkFactory
from wedding.modules.schedule.application.schedule_map import (
    ScheduleReader,
    has_open_items,
    require_milestone,
)
from wedding.modules.schedule.domain.derivation import waiting_on
from wedding.modules.schedule.domain.entities import MilestoneChange
from wedding.modules.schedule.domain.errors import ChecklistOpenItems, MilestoneBlocked
from wedding.modules.schedule.domain.values import ManualState, OwnerKind
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.errors import VersionConflict
from wedding.shared_kernel.ids import IdGenerator


@dataclass(frozen=True)
class ChangeMilestoneStateCommand:
    milestone_id: UUID
    # `None` reabre: volta ao estado derivado.
    state: ManualState | None
    ignore_block: bool
    version: int
    # A confirmação de concluir com itens do checklist em aberto (F-CRN-07, regra 5); só vale ao
    # ir para `Concluído`, com outro destino é ignorada.
    ignore_open_items: bool = False


class ChangeMilestoneState:
    def __init__(
        self, uow_factory: ScheduleUnitOfWorkFactory, ids: IdGenerator, reader: ScheduleReader
    ) -> None:
        self._uow_factory = uow_factory
        self._ids = ids
        self._reader = reader

    def execute(self, command: ChangeMilestoneStateCommand, actor: Actor) -> ScheduleDto:
        """Marca `Em andamento` ou `Concluído`, ou reabre (F-CRN-03). Marcar um marco que aguarda
        algo (categoria `Em discussão` ou dependência não resolvida) exige `ignore_block` (a
        confirmação é da tela) e o histórico registra que o bloqueio foi ignorado; sem ele, 422.
        Reabrir nunca pede confirmação. Repetir o estado não grava nada.

        Ordem: a `version` (409), repetir o estado (nem checa nada), o bloqueio (422
        `milestone_blocked`) e, ao concluir, os itens do checklist em aberto (422
        `checklist_open_items`, a confirmação é `ignore_open_items`). Concluir não altera os
        itens, e o histórico não ganha nada por causa deles."""
        with self._uow_factory(actor) as uow:
            milestone = require_milestone(uow.schedule, command.milestone_id)
            if milestone.version != command.version:
                raise VersionConflict()
            before = milestone.manual_state
            if command.state is milestone.manual_state:
                return self._reader.read(uow.schedule, actor)

            # O bloqueio se calcula sem a marca manual atual: sair de `Concluído` para
            # `Em andamento` com um predecessor pendente também pede a confirmação.
            blocked = command.state is not None and bool(
                waiting_on(self._reader.facts(uow.schedule, actor), milestone.id)
            )
            if blocked and not command.ignore_block:
                raise MilestoneBlocked()
            if (
                command.state is ManualState.DONE
                and not command.ignore_open_items
                and has_open_items(uow.schedule, OwnerKind.MILESTONE, milestone.id)
            ):
                raise ChecklistOpenItems()
            milestone.set_manual_state(command.state)
            uow.schedule.add_change(
                MilestoneChange(
                    id=self._ids.new_id(),
                    milestone_id=milestone.id,
                    state_before=before,
                    state_after=command.state,
                    ignored_block=blocked,
                    profile=actor.profile,
                )
            )
            uow.commit()
            return self._reader.read(uow.schedule, actor)
