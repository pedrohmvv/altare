from collections.abc import Callable
from dataclasses import dataclass

from wedding.modules.identity.application.commands.create_user import CreateUser
from wedding.modules.identity.application.commands.login import Login
from wedding.modules.identity.application.commands.logout import Logout
from wedding.modules.identity.application.commands.set_password import SetPassword
from wedding.modules.identity.application.queries.current_user import GetCurrentUser
from wedding.modules.identity.application.queries.resolve_session import ResolveSession


@dataclass(frozen=True)
class IdentityUseCases:
    login: Login
    logout: Logout
    current_user: GetCurrentUser
    resolve_session: ResolveSession
    create_user: CreateUser
    set_password: SetPassword


# Os adaptadores recebem um provedor, não os casos de uso: o banco só é aberto quando alguém
# de fato os usa (o `export-openapi` e o `--help` não precisam dele).
IdentityProvider = Callable[[], IdentityUseCases]
