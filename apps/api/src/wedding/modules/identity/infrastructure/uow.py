from wedding.modules.identity.infrastructure.repositories import (
    SqlSessionRepository,
    SqlUserRepository,
)
from wedding.platform.db.uow import SqlAlchemyUnitOfWork


class SqlIdentityUnitOfWork(SqlAlchemyUnitOfWork):
    @property
    def users(self) -> SqlUserRepository:
        return SqlUserRepository(self.session)

    @property
    def sessions(self) -> SqlSessionRepository:
        return SqlSessionRepository(self.session)
