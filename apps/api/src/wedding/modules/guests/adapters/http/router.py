from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from wedding.modules.guests.adapters.http.mappers import (
    to_guest_fields,
    to_guest_list_out,
    to_household_fields,
    to_status_change_out,
)
from wedding.modules.guests.adapters.http.schemas import (
    CompanionIn,
    GuestFieldsIn,
    GuestListOut,
    GuestStatusChangeOut,
    GuestStatusIn,
    GuestUpdateIn,
    HouseholdCreateIn,
    HouseholdUpdateIn,
    MoveIn,
)
from wedding.modules.guests.application.commands.add_companion import AddCompanionCommand
from wedding.modules.guests.application.commands.add_guest import AddGuestCommand
from wedding.modules.guests.application.commands.change_guest_status import (
    ChangeGuestStatusCommand,
)
from wedding.modules.guests.application.commands.create_household import CreateHouseholdCommand
from wedding.modules.guests.application.commands.delete_guest import (
    CompanionChoice,
    DeleteGuestCommand,
)
from wedding.modules.guests.application.commands.delete_household import DeleteHouseholdCommand
from wedding.modules.guests.application.commands.move_guest import MoveGuestCommand
from wedding.modules.guests.application.commands.restore_guest import RestoreGuestCommand
from wedding.modules.guests.application.commands.restore_household import RestoreHouseholdCommand
from wedding.modules.guests.application.commands.update_guest import UpdateGuestCommand
from wedding.modules.guests.application.commands.update_household import UpdateHouseholdCommand
from wedding.modules.guests.application.use_cases import GuestsProvider
from wedding.platform.http.private_cache import private_no_store
from wedding.platform.http.problem import problem_responses
from wedding.platform.http.session import current_actor
from wedding.shared_kernel.actor import Actor

CurrentActor = Annotated[Actor, Depends(current_actor)]
Version = Annotated[int, Query(ge=1, description="A versão que a tela viu; divergir dá 409.")]
Companion = Annotated[
    CompanionChoice | None,
    Query(description="O que fazer com o acompanhante ao excluir o titular: delete ou keep."),
]
_WRITE_ERRORS = problem_responses(401, 404, 409, 422)


def build_router(provide: GuestsProvider) -> APIRouter:
    """Todo `PUT`, `POST` e `DELETE` devolve a lista inteira já atualizada: a tela troca o cache de
    uma vez e nunca fica com pedaços de versões diferentes. Nenhum dado pessoal vai em URL (o log
    de acesso grava a query string) e nenhuma resposta pode ser guardada em cache."""
    router = APIRouter(prefix="/guests", tags=["guests"], dependencies=[Depends(private_no_store)])

    @router.get(
        "",
        operation_id="read_guest_list",
        response_model=GuestListOut,
        responses=problem_responses(401),
    )
    def read_guest_list(actor: CurrentActor) -> GuestListOut:
        return to_guest_list_out(provide().get_guest_list.execute(actor))

    @router.post(
        "/households",
        operation_id="create_household",
        status_code=201,
        response_model=GuestListOut,
        responses=_WRITE_ERRORS,
    )
    def create_household(body: HouseholdCreateIn, actor: CurrentActor) -> GuestListOut:
        command = CreateHouseholdCommand(
            to_household_fields(body.household), to_guest_fields(body.first_guest)
        )
        return to_guest_list_out(provide().create_household.execute(command, actor))

    @router.put(
        "/households/{household_id}",
        operation_id="update_household",
        response_model=GuestListOut,
        responses=_WRITE_ERRORS,
    )
    def update_household(
        household_id: UUID, body: HouseholdUpdateIn, actor: CurrentActor
    ) -> GuestListOut:
        command = UpdateHouseholdCommand(household_id, body.version, to_household_fields(body))
        return to_guest_list_out(provide().update_household.execute(command, actor))

    @router.delete(
        "/households/{household_id}",
        operation_id="delete_household",
        response_model=GuestListOut,
        responses=_WRITE_ERRORS,
    )
    def delete_household(household_id: UUID, version: Version, actor: CurrentActor) -> GuestListOut:
        command = DeleteHouseholdCommand(household_id, version)
        return to_guest_list_out(provide().delete_household.execute(command, actor))

    @router.post(
        "/households/{household_id}/restore",
        operation_id="restore_household",
        response_model=GuestListOut,
        responses=_WRITE_ERRORS,
    )
    def restore_household(household_id: UUID, actor: CurrentActor) -> GuestListOut:
        command = RestoreHouseholdCommand(household_id)
        return to_guest_list_out(provide().restore_household.execute(command, actor))

    @router.post(
        "/households/{household_id}/guests",
        operation_id="add_guest",
        status_code=201,
        response_model=GuestListOut,
        responses=_WRITE_ERRORS,
    )
    def add_guest(household_id: UUID, body: GuestFieldsIn, actor: CurrentActor) -> GuestListOut:
        command = AddGuestCommand(household_id, to_guest_fields(body))
        return to_guest_list_out(provide().add_guest.execute(command, actor))

    @router.post(
        "/people/{guest_id}/companion",
        operation_id="add_companion",
        status_code=201,
        response_model=GuestListOut,
        responses=_WRITE_ERRORS,
    )
    def add_companion(guest_id: UUID, body: CompanionIn, actor: CurrentActor) -> GuestListOut:
        command = AddCompanionCommand(guest_id, body.name)
        return to_guest_list_out(provide().add_companion.execute(command, actor))

    @router.put(
        "/people/{guest_id}",
        operation_id="update_guest",
        response_model=GuestListOut,
        responses=_WRITE_ERRORS,
    )
    def update_guest(guest_id: UUID, body: GuestUpdateIn, actor: CurrentActor) -> GuestListOut:
        command = UpdateGuestCommand(
            guest_id, body.version, to_guest_fields(body), body.decline_reason
        )
        return to_guest_list_out(provide().update_guest.execute(command, actor))

    @router.delete(
        "/people/{guest_id}",
        operation_id="delete_guest",
        response_model=GuestListOut,
        responses=_WRITE_ERRORS,
    )
    def delete_guest(
        guest_id: UUID, version: Version, actor: CurrentActor, companion: Companion = None
    ) -> GuestListOut:
        command = DeleteGuestCommand(guest_id, version, companion)
        return to_guest_list_out(provide().delete_guest.execute(command, actor))

    @router.post(
        "/people/{guest_id}/restore",
        operation_id="restore_guest",
        response_model=GuestListOut,
        responses=_WRITE_ERRORS,
    )
    def restore_guest(guest_id: UUID, actor: CurrentActor) -> GuestListOut:
        command = RestoreGuestCommand(guest_id)
        return to_guest_list_out(provide().restore_guest.execute(command, actor))

    @router.put(
        "/people/{guest_id}/status",
        operation_id="change_guest_status",
        response_model=GuestListOut,
        responses=_WRITE_ERRORS,
    )
    def change_guest_status(
        guest_id: UUID, body: GuestStatusIn, actor: CurrentActor
    ) -> GuestListOut:
        command = ChangeGuestStatusCommand(guest_id, body.status, body.reason, body.version)
        return to_guest_list_out(provide().change_guest_status.execute(command, actor))

    @router.put(
        "/people/{guest_id}/household",
        operation_id="move_guest",
        response_model=GuestListOut,
        responses=_WRITE_ERRORS,
    )
    def move_guest(guest_id: UUID, body: MoveIn, actor: CurrentActor) -> GuestListOut:
        command = MoveGuestCommand(guest_id, body.household_id, body.version)
        return to_guest_list_out(provide().move_guest.execute(command, actor))

    @router.get(
        "/people/{guest_id}/history",
        operation_id="list_guest_status_history",
        response_model=list[GuestStatusChangeOut],
        responses=problem_responses(401, 404),
    )
    def list_guest_status_history(
        guest_id: UUID, actor: CurrentActor
    ) -> list[GuestStatusChangeOut]:
        history = provide().list_guest_status_history.execute(guest_id, actor)
        return [to_status_change_out(change) for change in history]

    return router
