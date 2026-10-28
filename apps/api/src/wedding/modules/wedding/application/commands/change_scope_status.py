from dataclasses import dataclass
from uuid import UUID

from wedding.modules.wedding.application.ports import ScopeUnitOfWorkFactory
from wedding.modules.wedding.application.scope_dto import ScopeMapDto
from wedding.modules.wedding.application.scope_map import build_scope_map, require_category
from wedding.modules.wedding.domain.scope_entities import ScopeStatusChange
from wedding.modules.wedding.domain.scope_values import ScopeStatus, clean_reason
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.errors import VersionConflict
from wedding.shared_kernel.ids import IdGenerator


@dataclass(frozen=True)
class ChangeScopeStatusCommand:
    category_id: UUID
    status: ScopeStatus
    reason: str | None
    version: int


class ChangeScopeStatus:
    def __init__(self, uow_factory: ScopeUnitOfWorkFactory, ids: IdGenerator) -> None:
        self._uow_factory = uow_factory
        self._ids = ids

    def execute(self, command: ChangeScopeStatusCommand, actor: Actor) -> ScopeMapDto:
        """Qualquer um dos dois muda o status (D-029); a mudança fica com autor, status anterior e,
        para `Fica de fora`, o motivo. Repetir o status não grava nada."""
        with self._uow_factory(actor) as uow:
            category = require_category(uow.scope, command.category_id)
            if category.version != command.version:
                raise VersionConflict()
            before = category.status
            if category.change_status(command.status, command.reason):
                uow.scope.add_status_change(
                    ScopeStatusChange(
                        id=self._ids.new_id(),
                        category_id=category.id,
                        from_status=before,
                        to_status=category.status,
                        reason=clean_reason(command.reason)
                        if category.status is ScopeStatus.OUT
                        else None,
                        profile=actor.profile,
                    )
                )
                uow.commit()
            return build_scope_map(uow.scope)
