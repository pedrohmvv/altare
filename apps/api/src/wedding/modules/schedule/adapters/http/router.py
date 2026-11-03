from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from wedding.modules.schedule.adapters.http.mappers import to_schedule_out
from wedding.modules.schedule.adapters.http.schemas import (
    MilestoneStateIn,
    MilestoneUpdateIn,
    ScheduleOut,
)
from wedding.modules.schedule.application.commands.change_milestone_state import (
    ChangeMilestoneStateCommand,
)
from wedding.modules.schedule.application.commands.update_milestone import UpdateMilestoneCommand
from wedding.modules.schedule.application.use_cases import ScheduleProvider
from wedding.platform.http.problem import problem_responses
from wedding.platform.http.session import current_actor
from wedding.shared_kernel.actor import Actor

CurrentActor = Annotated[Actor, Depends(current_actor)]
_WRITE_ERRORS = problem_responses(401, 404, 409, 422)


def build_router(provide: ScheduleProvider) -> APIRouter:
    """Todo `PUT` devolve o cronograma inteiro já atualizado: marcar um marco muda o estado dos que
    dependem dele, e a tela troca o cache de uma vez em vez de remendar pedaços."""
    router = APIRouter(prefix="/schedule", tags=["schedule"])

    @router.get(
        "",
        operation_id="read_schedule",
        response_model=ScheduleOut,
        responses=problem_responses(401),
    )
    def read_schedule(actor: CurrentActor) -> ScheduleOut:
        return to_schedule_out(provide().read_schedule.execute(actor))

    @router.put(
        "/milestones/{milestone_id}",
        operation_id="update_milestone",
        response_model=ScheduleOut,
        responses=_WRITE_ERRORS,
    )
    def update_milestone(
        milestone_id: UUID, body: MilestoneUpdateIn, actor: CurrentActor
    ) -> ScheduleOut:
        command = UpdateMilestoneCommand(
            milestone_id, body.responsible, body.note, body.target_date, body.version
        )
        return to_schedule_out(provide().update_milestone.execute(command, actor))

    @router.put(
        "/milestones/{milestone_id}/state",
        operation_id="change_milestone_state",
        response_model=ScheduleOut,
        responses=_WRITE_ERRORS,
    )
    def change_milestone_state(
        milestone_id: UUID, body: MilestoneStateIn, actor: CurrentActor
    ) -> ScheduleOut:
        command = ChangeMilestoneStateCommand(
            milestone_id, body.state, body.ignore_block, body.version
        )
        return to_schedule_out(provide().change_milestone_state.execute(command, actor))

    return router
