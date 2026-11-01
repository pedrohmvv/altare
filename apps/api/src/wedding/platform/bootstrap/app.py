from fastapi import FastAPI

from wedding.modules.files.adapters.http.router import build_router as build_files_router
from wedding.modules.guests.adapters.http.router import build_router as build_guests_router
from wedding.modules.identity.adapters.http.router import build_router as build_identity_router
from wedding.modules.identity.application.ports import PasswordHasher
from wedding.modules.wedding.adapters.http.reference_router import build_reference_router
from wedding.modules.wedding.adapters.http.router import build_router as build_wedding_router
from wedding.modules.wedding.adapters.http.scope_router import build_scope_router
from wedding.platform.bootstrap.database import Database
from wedding.platform.bootstrap.files import FilesContainer
from wedding.platform.bootstrap.guests import GuestsContainer
from wedding.platform.bootstrap.identity import IdentityContainer
from wedding.platform.bootstrap.wedding import WeddingContainer
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
    database = Database(settings.database_url)
    identity = IdentityContainer(settings, clock=clock, hasher=hasher, database=database)
    files = FilesContainer(settings, database, clock=clock)
    wedding = WeddingContainer(database, files.use_cases, clock=clock)
    guests = GuestsContainer(database, clock=clock)
    app = create_app(
        routers=[
            build_identity_router(identity.use_cases, cookie_secure=settings.session_cookie_secure),
            build_files_router(files.use_cases),
            build_wedding_router(wedding.use_cases),
            build_scope_router(wedding.scope_use_cases),
            build_reference_router(wedding.reference_use_cases),
            build_guests_router(guests.use_cases),
        ],
        actor_resolver=lambda token: identity.use_cases().resolve_session.execute(token),
    )
    app.state.identity = identity
    return app
