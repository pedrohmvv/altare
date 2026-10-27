from collections.abc import Sequence

from fastapi import APIRouter, FastAPI

from wedding.platform.http import health
from wedding.platform.http.errors import install_error_handlers

API_PREFIX = "/api/v1"


def create_app(routers: Sequence[APIRouter] = ()) -> FastAPI:
    app = FastAPI(
        title="Altare API",
        version="0.1.0",
        openapi_url=f"{API_PREFIX}/openapi.json",
        docs_url=f"{API_PREFIX}/docs",
        swagger_ui_oauth2_redirect_url=f"{API_PREFIX}/docs/oauth2-redirect",
        redoc_url=None,
    )
    install_error_handlers(app)

    api = APIRouter(prefix=API_PREFIX)
    api.include_router(health.router)
    for router in routers:
        api.include_router(router)
    app.include_router(api)
    return app
