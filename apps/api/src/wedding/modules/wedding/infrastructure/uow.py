from wedding.modules.wedding.infrastructure.repositories import SqlBaselineRepository
from wedding.platform.db.uow import SqlAlchemyUnitOfWork


class SqlWeddingUnitOfWork(SqlAlchemyUnitOfWork):
    @property
    def baseline(self) -> SqlBaselineRepository:
        return SqlBaselineRepository(self.session)
