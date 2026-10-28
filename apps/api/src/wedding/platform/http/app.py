from collections.abc import Sequence

from fastapi import APIRouter, FastAPI

from wedding.platform.http import health
from wedding.platform.http.constants import API_PREFIX
from wedding.platform.http.csrf import CsrfMiddleware
from wedding.platform.http.errors import install_error_handlers
from wedding.platform.http.openapi import install_problem_media_type
from wedding.platform.http.session import ActorResolver


def create_app(
    routers: Sequence[APIRouter] = (), *, actor_resolver: ActorResolver | None = None
) -> FastAPI:
    app = FastAPI(
        title="Altare API",
        version="0.1.0",
        openapi_url=f"{API_PREFIX}/openapi.json",
        docs_url=f"{API_PREFIX}/docs",
        swagger_ui_oauth2_redirect_url=f"{API_PREFIX}/docs/oauth2-redirect",
        redoc_url=None,
    )
    app.state.actor_resolver = actor_resolver
    app.add_middleware(CsrfMiddleware)
    install_error_handlers(app)
    install_problem_media_type(app)

    api = APIRouter(prefix=API_PREFIX)
    api.include_router(health.router)
    for router in routers:
        api.include_router(router)
    app.include_router(api)
    return app
