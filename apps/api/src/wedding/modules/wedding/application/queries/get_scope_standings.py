from wedding.modules.wedding.application.ports import ScopeUnitOfWorkFactory
from wedding.modules.wedding.application.scope_dto import CategoryStandingDto
from wedding.modules.wedding.domain.scope_rules import is_visible
from wedding.shared_kernel.actor import Actor


class GetScopeStandings:
    """Leitura mínima para outro módulo (`application/public.py`): cada categoria viva com o
    status e a visibilidade. A categoria excluída não aparece; a oculta aparece como invisível."""

    def __init__(self, uow_factory: ScopeUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    def execute(self, actor: Actor) -> tuple[CategoryStandingDto, ...]:
        with self._uow_factory(actor) as uow:
            group_hidden = {
                group.id: group.hidden_at is not None for group in uow.scope.list_groups()
            }
            return tuple(
                CategoryStandingDto(
                    id=category.id,
                    name=category.name,
                    status=category.status,
                    visible=is_visible(
                        category_hidden=category.hidden_at is not None,
                        group_hidden=group_hidden.get(category.group_id, False),
                        deleted=False,
                    ),
                )
                for category in uow.scope.list_categories()
            )
