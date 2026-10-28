from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from wedding.modules.wedding.adapters.http.reference_schemas import (
    ImageReferenceIn,
    LinkReferenceIn,
    ReferenceOut,
)
from wedding.modules.wedding.application.commands.add_image_reference import (
    AddImageReferenceCommand,
)
from wedding.modules.wedding.application.commands.add_link_reference import AddLinkReferenceCommand
from wedding.modules.wedding.application.commands.remove_reference import RemoveReferenceCommand
from wedding.modules.wedding.application.reference_use_cases import ReferenceProvider
from wedding.modules.wedding.application.scope_dto import ReferenceDto
from wedding.platform.http.problem import problem_responses
from wedding.platform.http.session import current_actor
from wedding.shared_kernel.actor import Actor

CurrentActor = Annotated[Actor, Depends(current_actor)]
_WRITE_ERRORS = problem_responses(401, 403, 404, 422)


def _out(dto: ReferenceDto) -> ReferenceOut:
    return ReferenceOut.model_validate(
        {
            "id": dto.id,
            "kind": dto.kind,
            "url": dto.url,
            "domain": dto.domain,
            "file_id": dto.file_id,
            "title": dto.title,
            "comment": dto.comment,
            "by": dto.profile,
            "at": dto.added_at,
            "can_remove": dto.can_remove,
        }
    )


def build_reference_router(provide: ReferenceProvider) -> APIRouter:
    """As referências de uma frente (F-PLN-06); toda escrita devolve a lista atualizada."""
    router = APIRouter(
        prefix="/wedding/scope/categories/{category_id}/references", tags=["wedding"]
    )

    @router.get(
        "",
        operation_id="list_scope_references",
        response_model=list[ReferenceOut],
        responses=problem_responses(401, 404, 422),
    )
    def list_scope_references(category_id: UUID, actor: CurrentActor) -> list[ReferenceOut]:
        return [_out(r) for r in provide().list_references.execute(category_id, actor)]

    @router.post(
        "/links",
        operation_id="add_scope_link_reference",
        status_code=201,
        response_model=list[ReferenceOut],
        responses=_WRITE_ERRORS,
    )
    def add_scope_link_reference(
        category_id: UUID, body: LinkReferenceIn, actor: CurrentActor
    ) -> list[ReferenceOut]:
        command = AddLinkReferenceCommand(category_id, body.url, body.title, body.comment)
        return [_out(r) for r in provide().add_link_reference.execute(command, actor)]

    @router.post(
        "/images",
        operation_id="add_scope_image_reference",
        status_code=201,
        response_model=list[ReferenceOut],
        responses=_WRITE_ERRORS,
    )
    def add_scope_image_reference(
        category_id: UUID, body: ImageReferenceIn, actor: CurrentActor
    ) -> list[ReferenceOut]:
        command = AddImageReferenceCommand(category_id, body.file_id, body.title, body.comment)
        return [_out(r) for r in provide().add_image_reference.execute(command, actor)]

    @router.delete(
        "/{reference_id}",
        operation_id="remove_scope_reference",
        response_model=list[ReferenceOut],
        responses=_WRITE_ERRORS,
    )
    def remove_scope_reference(
        category_id: UUID, reference_id: UUID, actor: CurrentActor
    ) -> list[ReferenceOut]:
        command = RemoveReferenceCommand(category_id, reference_id)
        return [_out(r) for r in provide().remove_reference.execute(command, actor)]

    return router
