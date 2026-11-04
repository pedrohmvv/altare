import datetime as dt
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from wedding.modules.schedule.adapters.http.mappers import (
    to_created_milestone_out,
    to_date_preview_out,
    to_restore_out,
    to_schedule_out,
)
from wedding.modules.schedule.adapters.http.schemas import (
    CreatedMilestoneOut,
    DatePreviewOut,
    MilestoneCreateIn,
    MilestoneDependenciesIn,
    MilestoneStateIn,
    MilestoneUpdateIn,
    MilestoneWindowIn,
    PhaseCreateIn,
    PhaseOrderIn,
    PhaseRenameIn,
    RestoreOut,
    ScheduleOut,
)
from wedding.modules.schedule.application.commands.change_milestone_state import (
    ChangeMilestoneStateCommand,
)
from wedding.modules.schedule.application.commands.create_milestone import CreateMilestoneCommand
from wedding.modules.schedule.application.commands.create_phase import CreatePhaseCommand
from wedding.modules.schedule.application.commands.delete_milestone import DeleteMilestoneCommand
from wedding.modules.schedule.application.commands.rename_phase import RenamePhaseCommand
from wedding.modules.schedule.application.commands.reorder_phases import ReorderPhasesCommand
from wedding.modules.schedule.application.commands.restore_milestone import (
    RestoreMilestoneCommand,
)
from wedding.modules.schedule.application.commands.set_milestone_dependencies import (
    SetMilestoneDependenciesCommand,
)
from wedding.modules.schedule.application.commands.update_milestone import UpdateMilestoneCommand
from wedding.modules.schedule.application.commands.update_milestone_window import (
    UpdateMilestoneWindowCommand,
)
from wedding.modules.schedule.application.queries.preview_date_change import (
    PreviewDateChangeCommand,
)
from wedding.modules.schedule.application.use_cases import ScheduleProvider
from wedding.platform.http.problem import problem_responses
from wedding.platform.http.session import current_actor
from wedding.shared_kernel.actor import Actor

CurrentActor = Annotated[Actor, Depends(current_actor)]
Version = Annotated[int, Query(ge=1, description="A versão que a tela viu; divergir dá 409.")]
_WRITE_ERRORS = problem_responses(401, 404, 409, 422)


def build_router(provide: ScheduleProvider) -> APIRouter:
    """Todo `PUT`, `POST` e `DELETE` devolve o cronograma inteiro já atualizado (o restaurar, junto
    com o que ficou de fora; o criar marco, junto com o id do novo): mexer em um marco muda o estado
    dos que dependem dele, e a tela troca o cache de uma vez em vez de remendar pedaços."""
    router = APIRouter(prefix="/schedule", tags=["schedule"])

    @router.get(
        "",
        operation_id="read_schedule",
        response_model=ScheduleOut,
        responses=problem_responses(401),
    )
    def read_schedule(actor: CurrentActor) -> ScheduleOut:
        return to_schedule_out(provide().read_schedule.execute(actor))

    @router.get(
        "/date-preview",
        operation_id="preview_date_change",
        response_model=DatePreviewOut,
        # Só leitura: não grava nada. O 422 é o ano fora de 2000 a 2100.
        responses=problem_responses(401, 422),
    )
    def preview_date_change(
        actor: CurrentActor,
        exact: Annotated[
            dt.date | None,
            Query(
                description=(
                    "A data exata que o casamento passaria a ter, já `Definida`; sem ela, o "
                    "cenário é o Modo Sem Data. O ano vai de 2000 a 2100."
                )
            ),
        ] = None,
    ) -> DatePreviewOut:
        command = PreviewDateChangeCommand(exact)
        return to_date_preview_out(provide().preview_date_change.execute(command, actor))

    @router.post(
        "/milestones",
        operation_id="create_milestone",
        status_code=201,
        response_model=CreatedMilestoneOut,
        responses=_WRITE_ERRORS,
    )
    def create_milestone(body: MilestoneCreateIn, actor: CurrentActor) -> CreatedMilestoneOut:
        command = CreateMilestoneCommand(
            body.title, body.phase_id, body.responsible, body.category_id, tuple(body.depends_on)
        )
        return to_created_milestone_out(provide().create_milestone.execute(command, actor))

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
            milestone_id,
            body.title,
            body.phase_id,
            body.responsible,
            body.category_id,
            body.note,
            body.target_date,
            body.version,
        )
        return to_schedule_out(provide().update_milestone.execute(command, actor))

    @router.put(
        "/milestones/{milestone_id}/window",
        operation_id="update_milestone_window",
        response_model=ScheduleOut,
        responses=_WRITE_ERRORS,
    )
    def update_milestone_window(
        milestone_id: UUID, body: MilestoneWindowIn, actor: CurrentActor
    ) -> ScheduleOut:
        command = UpdateMilestoneWindowCommand(
            milestone_id, body.start_before, body.end_before, body.unit, body.version
        )
        return to_schedule_out(provide().update_milestone_window.execute(command, actor))

    @router.delete(
        "/milestones/{milestone_id}",
        operation_id="delete_milestone",
        response_model=ScheduleOut,
        responses=_WRITE_ERRORS,
    )
    def delete_milestone(milestone_id: UUID, version: Version, actor: CurrentActor) -> ScheduleOut:
        command = DeleteMilestoneCommand(milestone_id, version)
        return to_schedule_out(provide().delete_milestone.execute(command, actor))

    @router.post(
        "/milestones/{milestone_id}/restore",
        operation_id="restore_milestone",
        response_model=RestoreOut,
        responses=problem_responses(401, 404),
    )
    def restore_milestone(milestone_id: UUID, actor: CurrentActor) -> RestoreOut:
        command = RestoreMilestoneCommand(milestone_id)
        return to_restore_out(provide().restore_milestone.execute(command, actor))

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

    @router.put(
        "/milestones/{milestone_id}/dependencies",
        operation_id="set_milestone_dependencies",
        response_model=ScheduleOut,
        responses=_WRITE_ERRORS,
    )
    def set_milestone_dependencies(
        milestone_id: UUID, body: MilestoneDependenciesIn, actor: CurrentActor
    ) -> ScheduleOut:
        command = SetMilestoneDependenciesCommand(
            milestone_id, tuple(body.depends_on), body.version
        )
        return to_schedule_out(provide().set_milestone_dependencies.execute(command, actor))

    @router.post(
        "/phases",
        operation_id="create_phase",
        status_code=201,
        response_model=ScheduleOut,
        responses=_WRITE_ERRORS,
    )
    def create_phase(body: PhaseCreateIn, actor: CurrentActor) -> ScheduleOut:
        return to_schedule_out(
            provide().create_phase.execute(CreatePhaseCommand(body.title), actor)
        )

    # `/phases/order` vem antes de `/phases/{phase_id}`: "order" não é um id, mas a ordem das
    # rotas é a que o FastAPI casa primeiro.
    @router.put(
        "/phases/order",
        operation_id="reorder_phases",
        response_model=ScheduleOut,
        # Sem `version`: a lista é uma permutação exata das fases vivas, o último a gravar vence
        # sem incoerência e uma fase criada no meio dá `invalid_phase_order`. Logo, sem 404 nem 409.
        responses=problem_responses(401, 422),
    )
    def reorder_phases(body: PhaseOrderIn, actor: CurrentActor) -> ScheduleOut:
        command = ReorderPhasesCommand(tuple(body.ids))
        return to_schedule_out(provide().reorder_phases.execute(command, actor))

    @router.put(
        "/phases/{phase_id}",
        operation_id="rename_phase",
        response_model=ScheduleOut,
        responses=_WRITE_ERRORS,
    )
    def rename_phase(phase_id: UUID, body: PhaseRenameIn, actor: CurrentActor) -> ScheduleOut:
        command = RenamePhaseCommand(phase_id, body.title, body.version)
        return to_schedule_out(provide().rename_phase.execute(command, actor))

    return router
