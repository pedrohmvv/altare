from wedding.modules.files.infrastructure.repositories import SqlFileRepository
from wedding.platform.db.uow import SqlAlchemyUnitOfWork


class SqlFilesUnitOfWork(SqlAlchemyUnitOfWork):
    @property
    def files(self) -> SqlFileRepository:
        return SqlFileRepository(self.session)
