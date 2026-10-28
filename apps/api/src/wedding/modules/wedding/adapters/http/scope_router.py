from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from wedding.modules.wedding.adapters.http.scope_mappers import (
    to_scope_map_out,
    to_status_change_out,
)
from wedding.modules.wedding.adapters.http.scope_schemas import (
    CategoryCreateIn,
    CategoryUpdateIn,
    EvaluationIn,
    GroupCreateIn,
    GroupRenameIn,
    ScopeMapOut,
    StatusChangeOut,
    StatusIn,
    VisibilityIn,
)
from wedding.modules.wedding.application.commands.change_scope_status import (
    ChangeScopeStatusCommand,
)
from wedding.modules.wedding.application.commands.create_scope_category import (
    CreateScopeCategoryCommand,
)
from wedding.modules.wedding.application.commands.create_scope_group import CreateScopeGroupCommand
from wedding.modules.wedding.application.commands.delete_scope_category import (
    DeleteScopeCategoryCommand,
)
from wedding.modules.wedding.application.commands.delete_scope_group import DeleteScopeGroupCommand
from wedding.modules.wedding.application.commands.rename_scope_group import RenameScopeGroupCommand
from wedding.modules.wedding.application.commands.set_my_evaluation import SetMyEvaluationCommand
from wedding.modules.wedding.application.commands.set_scope_category_visibility import (
    SetScopeCategoryVisibilityCommand,
)
from wedding.modules.wedding.application.commands.set_scope_group_visibility import (
    SetScopeGroupVisibilityCommand,
)
from wedding.modules.wedding.application.commands.update_scope_category import (
    UpdateScopeCategoryCommand,
)
from wedding.modules.wedding.application.scope_use_cases import ScopeProvider
from wedding.platform.http.problem import problem_responses
from wedding.platform.http.session import current_actor
from wedding.shared_kernel.actor import Actor

CurrentActor = Annotated[Actor, Depends(current_actor)]
Version = Annotated[int, Query(ge=1, description="A versão que a tela viu; divergir dá 409.")]
_WRITE_ERRORS = problem_responses(401, 404, 409, 422)


def build_scope_router(provide: ScopeProvider) -> APIRouter:
    """Todo `PUT`, `POST` e `DELETE` devolve o mapa inteiro já atualizado: a tela troca o cache de
    uma vez e nunca fica com pedaços de versões diferentes."""
    router = APIRouter(prefix="/wedding/scope", tags=["wedding"])

    @router.get(
        "",
        operation_id="read_scope_map",
        response_model=ScopeMapOut,
        responses=problem_responses(401),
    )
    def read_scope_map(actor: CurrentActor) -> ScopeMapOut:
        return to_scope_map_out(provide().get_scope_map.execute(actor))

    @router.post(
        "/groups",
        operation_id="create_scope_group",
        status_code=201,
        response_model=ScopeMapOut,
        responses=_WRITE_ERRORS,
    )
    def create_scope_group(body: GroupCreateIn, actor: CurrentActor) -> ScopeMapOut:
        command = CreateScopeGroupCommand(body.name)
        return to_scope_map_out(provide().create_scope_group.execute(command, actor))

    @router.put(
        "/groups/{group_id}",
        operation_id="update_scope_group",
        response_model=ScopeMapOut,
        responses=_WRITE_ERRORS,
    )
    def update_scope_group(group_id: UUID, body: GroupRenameIn, actor: CurrentActor) -> ScopeMapOut:
        command = RenameScopeGroupCommand(group_id, body.name, body.version)
        return to_scope_map_out(provide().rename_scope_group.execute(command, actor))

    @router.put(
        "/groups/{group_id}/visibility",
        operation_id="set_scope_group_visibility",
        response_model=ScopeMapOut,
        responses=_WRITE_ERRORS,
    )
    def set_scope_group_visibility(
        group_id: UUID, body: VisibilityIn, actor: CurrentActor
    ) -> ScopeMapOut:
        command = SetScopeGroupVisibilityCommand(group_id, body.hidden, body.version)
        return to_scope_map_out(provide().set_scope_group_visibility.execute(command, actor))

    @router.delete(
        "/groups/{group_id}",
        operation_id="delete_scope_group",
        response_model=ScopeMapOut,
        responses=_WRITE_ERRORS,
    )
    def delete_scope_group(group_id: UUID, version: Version, actor: CurrentActor) -> ScopeMapOut:
        command = DeleteScopeGroupCommand(group_id, version)
        return to_scope_map_out(provide().delete_scope_group.execute(command, actor))

    @router.post(
        "/categories",
        operation_id="create_scope_category",
        status_code=201,
        response_model=ScopeMapOut,
        responses=_WRITE_ERRORS,
    )
    def create_scope_category(body: CategoryCreateIn, actor: CurrentActor) -> ScopeMapOut:
        command = CreateScopeCategoryCommand(body.group_id, body.name, body.estimate_cents)
        return to_scope_map_out(provide().create_scope_category.execute(command, actor))

    @router.put(
        "/categories/{category_id}",
        operation_id="update_scope_category",
        response_model=ScopeMapOut,
        responses=_WRITE_ERRORS,
    )
    def update_scope_category(
        category_id: UUID, body: CategoryUpdateIn, actor: CurrentActor
    ) -> ScopeMapOut:
        command = UpdateScopeCategoryCommand(
            category_id, body.name, body.group_id, body.estimate_cents, body.version
        )
        return to_scope_map_out(provide().update_scope_category.execute(command, actor))

    @router.put(
        "/categories/{category_id}/visibility",
        operation_id="set_scope_category_visibility",
        response_model=ScopeMapOut,
        responses=_WRITE_ERRORS,
    )
    def set_scope_category_visibility(
        category_id: UUID, body: VisibilityIn, actor: CurrentActor
    ) -> ScopeMapOut:
        command = SetScopeCategoryVisibilityCommand(category_id, body.hidden, body.version)
        return to_scope_map_out(provide().set_scope_category_visibility.execute(command, actor))

    @router.delete(
        "/categories/{category_id}",
        operation_id="delete_scope_category",
        response_model=ScopeMapOut,
        responses=_WRITE_ERRORS,
    )
    def delete_scope_category(
        category_id: UUID, version: Version, actor: CurrentActor
    ) -> ScopeMapOut:
        command = DeleteScopeCategoryCommand(category_id, version)
        return to_scope_map_out(provide().delete_scope_category.execute(command, actor))

    @router.put(
        "/categories/{category_id}/status",
        operation_id="change_scope_status",
        response_model=ScopeMapOut,
        responses=_WRITE_ERRORS,
    )
    def change_scope_status(category_id: UUID, body: StatusIn, actor: CurrentActor) -> ScopeMapOut:
        command = ChangeScopeStatusCommand(category_id, body.status, body.reason, body.version)
        return to_scope_map_out(provide().change_scope_status.execute(command, actor))

    @router.put(
        "/categories/{category_id}/my-evaluation",
        operation_id="set_my_evaluation",
        response_model=ScopeMapOut,
        responses=_WRITE_ERRORS,
    )
    def set_my_evaluation(
        category_id: UUID, body: EvaluationIn, actor: CurrentActor
    ) -> ScopeMapOut:
        command = SetMyEvaluationCommand(category_id, body.priority, body.note, body.version)
        return to_scope_map_out(provide().set_my_evaluation.execute(command, actor))

    @router.get(
        "/categories/{category_id}/history",
        operation_id="list_scope_category_history",
        response_model=list[StatusChangeOut],
        responses=problem_responses(401, 404, 422),
    )
    def list_scope_category_history(
        category_id: UUID, actor: CurrentActor
    ) -> list[StatusChangeOut]:
        history = provide().list_scope_category_history.execute(category_id, actor)
        return [to_status_change_out(change) for change in history]

    return router
