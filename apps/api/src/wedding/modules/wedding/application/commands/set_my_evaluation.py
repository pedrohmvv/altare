from dataclasses import dataclass
from uuid import UUID

from wedding.modules.wedding.application.ports import ScopeUnitOfWorkFactory
from wedding.modules.wedding.application.scope_dto import ScopeMapDto
from wedding.modules.wedding.application.scope_map import build_scope_map, require_category
from wedding.modules.wedding.domain.scope_values import Priority
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.errors import NotFound, VersionConflict


@dataclass(frozen=True)
class SetMyEvaluationCommand:
    category_id: UUID
    priority: Priority | None
    note: str | None
    version: int


class SetMyEvaluation:
    def __init__(self, uow_factory: ScopeUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    def execute(self, command: SetMyEvaluationCommand, actor: Actor) -> ScopeMapDto:
        """O perfil vem da sessão: ninguém edita a avaliação do outro (F-PLN-04, regra 1), e a
        prioridade não muda o status conjunto. `version` é a da avaliação."""
        with self._uow_factory(actor) as uow:
            category = require_category(uow.scope, command.category_id)
            evaluation = uow.scope.get_evaluation(category.id, actor.profile)
            if evaluation is None:
                raise NotFound()
            if evaluation.version != command.version:
                raise VersionConflict()
            if evaluation.update(command.priority, command.note):
                uow.commit()
            return build_scope_map(uow.scope)
