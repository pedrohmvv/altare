from fastapi import FastAPI

from wedding.modules.identity.adapters.http.router import build_router as build_identity_router
from wedding.modules.identity.application.ports import PasswordHasher
from wedding.platform.bootstrap.identity import IdentityContainer
from wedding.platform.config import Settings
from wedding.platform.http.app import create_app
from wedding.shared_kernel.clock import Clock


def build_app(
    settings: Settings | None = None,
    *,
    clock: Clock | None = None,
    hasher: PasswordHasher | None = None,
) -> FastAPI:
    """A composição: liga os módulos à plataforma. `clock` e `hasher` existem para os testes."""
    settings = settings or Settings()
    identity = IdentityContainer(settings, clock=clock, hasher=hasher)
    app = create_app(
        routers=[
            build_identity_router(identity.use_cases, cookie_secure=settings.session_cookie_secure)
        ],
        actor_resolver=lambda token: identity.use_cases().resolve_session.execute(token),
    )
    app.state.identity = identity
    return app
