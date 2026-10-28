from typing import Annotated

from fastapi import APIRouter, Depends, Query

from wedding.modules.wedding.adapters.http.mappers import (
    to_baseline_out,
    to_ceiling_value,
    to_ceremony_value,
    to_change_out,
    to_date_value,
    to_size_value,
    to_text_value,
)
from wedding.modules.wedding.adapters.http.schemas import (
    BaselineChangeOut,
    BaselineOut,
    CeilingFieldIn,
    CeremonyFieldIn,
    DateFieldIn,
    FieldIn,
    SizeFieldIn,
    TextFieldIn,
)
from wedding.modules.wedding.application.commands.update_baseline_field import (
    UpdateBaselineFieldCommand,
)
from wedding.modules.wedding.application.use_cases import WeddingProvider
from wedding.modules.wedding.domain.value_objects import BaselineKey, BaselineValue
from wedding.platform.http.problem import problem_responses
from wedding.platform.http.session import current_actor
from wedding.shared_kernel.actor import Actor

CurrentActor = Annotated[Actor, Depends(current_actor)]
_UPDATE_ERRORS = problem_responses(401, 403, 404, 409, 422)


def build_router(provide: WeddingProvider) -> APIRouter:
    router = APIRouter(prefix="/wedding", tags=["wedding"])

    def update(
        actor: Actor, key: BaselineKey, value: BaselineValue | None, body: FieldIn
    ) -> BaselineOut:
        command = UpdateBaselineFieldCommand(key, value, body.status, body.note, body.version)
        return to_baseline_out(provide().update_baseline_field.execute(command, actor))

    @router.get(
        "/baseline",
        operation_id="read_baseline",
        response_model=BaselineOut,
        responses=problem_responses(401),
    )
    def read_baseline(actor: CurrentActor) -> BaselineOut:
        return to_baseline_out(provide().get_baseline.execute(actor))

    @router.put(
        "/baseline/date",
        operation_id="update_baseline_date",
        response_model=BaselineOut,
        responses=_UPDATE_ERRORS,
    )
    def update_baseline_date(body: DateFieldIn, actor: CurrentActor) -> BaselineOut:
        return update(actor, BaselineKey.DATE, to_date_value(body.value), body)

    @router.put(
        "/baseline/city",
        operation_id="update_baseline_city",
        response_model=BaselineOut,
        responses=_UPDATE_ERRORS,
    )
    def update_baseline_city(body: TextFieldIn, actor: CurrentActor) -> BaselineOut:
        return update(actor, BaselineKey.CITY, to_text_value(body.value), body)

    @router.put(
        "/baseline/format",
        operation_id="update_baseline_format",
        response_model=BaselineOut,
        responses=_UPDATE_ERRORS,
    )
    def update_baseline_format(body: TextFieldIn, actor: CurrentActor) -> BaselineOut:
        return update(actor, BaselineKey.FORMAT, to_text_value(body.value), body)

    @router.put(
        "/baseline/size",
        operation_id="update_baseline_size",
        response_model=BaselineOut,
        responses=_UPDATE_ERRORS,
    )
    def update_baseline_size(body: SizeFieldIn, actor: CurrentActor) -> BaselineOut:
        return update(actor, BaselineKey.SIZE, to_size_value(body.value), body)

    @router.put(
        "/baseline/ceiling",
        operation_id="update_baseline_ceiling",
        response_model=BaselineOut,
        responses=_UPDATE_ERRORS,
    )
    def update_baseline_ceiling(body: CeilingFieldIn, actor: CurrentActor) -> BaselineOut:
        return update(actor, BaselineKey.CEILING, to_ceiling_value(body.value), body)

    @router.put(
        "/baseline/ceremony",
        operation_id="update_baseline_ceremony",
        response_model=BaselineOut,
        responses=_UPDATE_ERRORS,
    )
    def update_baseline_ceremony(body: CeremonyFieldIn, actor: CurrentActor) -> BaselineOut:
        return update(actor, BaselineKey.CEREMONY, to_ceremony_value(body.value), body)

    @router.get(
        "/baseline/changes",
        operation_id="list_baseline_changes",
        response_model=list[BaselineChangeOut],
        responses=problem_responses(401, 422),
    )
    def list_baseline_changes(
        actor: CurrentActor, limit: Annotated[int, Query(ge=1, le=200)] = 50
    ) -> list[BaselineChangeOut]:
        return [
            to_change_out(change)
            for change in provide().list_baseline_changes.execute(actor, limit)
        ]

    return router
