from wedding.modules.schedule.infrastructure.repositories import SqlScheduleRepository
from wedding.platform.db.uow import SqlAlchemyUnitOfWork


class SqlScheduleUnitOfWork(SqlAlchemyUnitOfWork):
    @property
    def schedule(self) -> SqlScheduleRepository:
        return SqlScheduleRepository(self.session)
