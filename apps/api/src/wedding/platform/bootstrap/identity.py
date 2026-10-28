from threading import Lock

from wedding.modules.identity.application.commands.create_user import CreateUser
from wedding.modules.identity.application.commands.login import Login
from wedding.modules.identity.application.commands.logout import Logout
from wedding.modules.identity.application.commands.set_password import SetPassword
from wedding.modules.identity.application.ports import PasswordHasher
from wedding.modules.identity.application.queries.current_user import GetCurrentUser
from wedding.modules.identity.application.queries.resolve_session import ResolveSession
from wedding.modules.identity.application.use_cases import IdentityUseCases
from wedding.modules.identity.infrastructure.argon2_hasher import Argon2PasswordHasher
from wedding.modules.identity.infrastructure.login_attempts import InMemoryLoginAttempts
from wedding.modules.identity.infrastructure.mapping import start_mappers
from wedding.modules.identity.infrastructure.uow import SqlIdentityUnitOfWork
from wedding.platform.bootstrap.database import Database
from wedding.platform.config import Settings
from wedding.shared_kernel.clock import Clock, SystemClock
from wedding.shared_kernel.ids import UuidGenerator


class IdentityContainer:
    """Monta os casos de uso de identidade na primeira vez que alguém os pede.

    A montagem abre o banco e cria o hasher, então fica fora da criação do app: gerar o contrato
    OpenAPI e listar a ajuda da CLI não precisam de nenhum dos dois.
    """

    def __init__(
        self,
        settings: Settings,
        *,
        clock: Clock | None = None,
        hasher: PasswordHasher | None = None,
        database: Database | None = None,
    ) -> None:
        self._settings = settings
        self._database = database or Database(settings.database_url)
        self._clock = clock or SystemClock()
        self._hasher = hasher
        self._lock = Lock()
        self._use_cases: IdentityUseCases | None = None

    def use_cases(self) -> IdentityUseCases:
        with self._lock:
            if self._use_cases is None:
                self._use_cases = self._build()
            return self._use_cases

    def _build(self) -> IdentityUseCases:
        start_mappers()
        sessions = self._database.sessions()
        clock = self._clock
        ids = UuidGenerator()
        hasher = self._hasher or Argon2PasswordHasher()
        attempts = InMemoryLoginAttempts()

        def uow_factory() -> SqlIdentityUnitOfWork:
            return SqlIdentityUnitOfWork(sessions, clock)

        return IdentityUseCases(
            login=Login(uow_factory, hasher, attempts, clock, ids),
            logout=Logout(uow_factory),
            current_user=GetCurrentUser(uow_factory),
            resolve_session=ResolveSession(uow_factory, clock),
            create_user=CreateUser(uow_factory, hasher, ids),
            set_password=SetPassword(uow_factory, hasher),
        )
