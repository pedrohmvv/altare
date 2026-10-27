from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response

from wedding.modules.identity.adapters.http.mappers import to_current_user_out
from wedding.modules.identity.adapters.http.schemas import CurrentUserOut, LoginIn
from wedding.modules.identity.application.commands.login import LoginCommand
from wedding.modules.identity.application.use_cases import IdentityProvider
from wedding.modules.identity.domain.rules import ABSOLUTE_LIMIT
from wedding.platform.http.constants import API_ROOT, SESSION_COOKIE
from wedding.platform.http.problem import problem_responses
from wedding.platform.http.session import current_actor
from wedding.shared_kernel.actor import Actor

_COOKIE_MAX_AGE = int(ABSOLUTE_LIMIT.total_seconds())


def build_router(provide: IdentityProvider, *, cookie_secure: bool) -> APIRouter:
    router = APIRouter(prefix="/auth", tags=["auth"])

    @router.post(
        "/login",
        operation_id="login",
        response_model=CurrentUserOut,
        responses=problem_responses(401, 403, 422, 429),
    )
    def login(body: LoginIn, request: Request, response: Response) -> CurrentUserOut:
        result = provide().login.execute(
            LoginCommand(
                username=body.username,
                password=body.password,
                ip=request.client.host if request.client else "desconhecido",
                previous_token=request.cookies.get(SESSION_COOKIE),
            )
        )
        response.set_cookie(
            SESSION_COOKIE,
            result.token,
            max_age=_COOKIE_MAX_AGE,
            path=API_ROOT,
            secure=cookie_secure,
            httponly=True,
            samesite="lax",
        )
        return to_current_user_out(result.user)

    @router.post(
        "/logout", operation_id="logout", status_code=204, responses=problem_responses(403)
    )
    def logout(request: Request) -> Response:
        provide().logout.execute(request.cookies.get(SESSION_COOKIE))
        response = Response(status_code=204)
        # Os atributos precisam ser os mesmos do login, senão o navegador mantém o cookie.
        response.delete_cookie(
            SESSION_COOKIE, path=API_ROOT, secure=cookie_secure, httponly=True, samesite="lax"
        )
        return response

    @router.get(
        "/me",
        operation_id="read_current_user",
        response_model=CurrentUserOut,
        responses=problem_responses(401),
    )
    def read_current_user(actor: Annotated[Actor, Depends(current_actor)]) -> CurrentUserOut:
        return to_current_user_out(provide().current_user.execute(actor.user_id))

    return router
