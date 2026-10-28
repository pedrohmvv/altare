from dataclasses import dataclass
from uuid import UUID

from wedding.modules.wedding.application.ports import ScopeUnitOfWorkFactory
from wedding.modules.wedding.application.scope_dto import ScopeMapDto
from wedding.modules.wedding.application.scope_map import build_scope_map
from wedding.modules.wedding.domain.errors import DuplicateScopeName
from wedding.modules.wedding.domain.scope_entities import ScopeCategory, ScopeEvaluation
from wedding.modules.wedding.domain.scope_values import Origin
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.errors import NotFound
from wedding.shared_kernel.ids import IdGenerator
from wedding.shared_kernel.profile import ProfileKind


@dataclass(frozen=True)
class CreateScopeCategoryCommand:
    group_id: UUID
    name: str
    estimate_cents: int | None


class CreateScopeCategory:
    def __init__(self, uow_factory: ScopeUnitOfWorkFactory, ids: IdGenerator) -> None:
        self._uow_factory = uow_factory
        self._ids = ids

    def execute(self, command: CreateScopeCategoryCommand, actor: Actor) -> ScopeMapDto:
        """Cria a frente e o par de avaliações juntos: toda categoria tem uma de cada perfil desde o
        início, então avaliar sempre atualiza (nunca há corrida de criar ou atualizar)."""
        with self._uow_factory(actor) as uow:
            if uow.scope.get_group(command.group_id) is None:
                raise NotFound()
            category = ScopeCategory(
                id=self._ids.new_id(),
                group_id=command.group_id,
                name=command.name,
                position=uow.scope.next_category_position(command.group_id),
                origin=Origin.COUPLE,
                estimate_cents=command.estimate_cents,
            )
            if uow.scope.category_name_taken(category.name_key):
                raise DuplicateScopeName()
            uow.scope.add_category(category)
            for profile in (ProfileKind.NOIVO, ProfileKind.NOIVA):
                uow.scope.add_evaluation(
                    ScopeEvaluation(id=self._ids.new_id(), category_id=category.id, profile=profile)
                )
            uow.commit()
            return build_scope_map(uow.scope)
