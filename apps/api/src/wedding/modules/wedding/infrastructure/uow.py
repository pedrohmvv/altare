from sqlalchemy.exc import IntegrityError

from wedding.modules.wedding.domain.errors import DuplicateScopeName
from wedding.modules.wedding.infrastructure.repositories import SqlBaselineRepository
from wedding.modules.wedding.infrastructure.scope_repositories import SqlScopeRepository
from wedding.platform.db.uow import SqlAlchemyUnitOfWork


class SqlWeddingUnitOfWork(SqlAlchemyUnitOfWork):
    @property
    def baseline(self) -> SqlBaselineRepository:
        return SqlBaselineRepository(self.session)

    @property
    def scope(self) -> SqlScopeRepository:
        return SqlScopeRepository(self.session)

    def commit(self) -> None:
        """Duas pessoas criando ou renomeando para o mesmo nome ao mesmo tempo passam juntas pela
        checagem; o índice único pega a segunda, e ela recebe "nome já usado", não erro de banco."""
        try:
            super().commit()
        except IntegrityError as error:
            self.session.rollback()
            if "name_key" in str(error.orig):
                raise DuplicateScopeName() from error
            raise
