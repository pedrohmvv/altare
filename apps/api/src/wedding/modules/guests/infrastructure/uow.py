from sqlalchemy.exc import IntegrityError

from wedding.modules.guests.domain.errors import CompanionAlreadyExists, DuplicateHouseholdName
from wedding.modules.guests.infrastructure.repositories import SqlGuestRepository
from wedding.platform.db.uow import SqlAlchemyUnitOfWork


class SqlGuestsUnitOfWork(SqlAlchemyUnitOfWork):
    @property
    def guests(self) -> SqlGuestRepository:
        return SqlGuestRepository(self.session)

    def commit(self) -> None:
        """Duas pessoas criando o mesmo nome (ou o mesmo +1) ao mesmo tempo passam juntas pela
        checagem; o índice único pega a segunda, e ela recebe a mensagem de domínio, não o erro de
        banco (que também não pode levar o dado pessoal para fora, `hide_parameters`)."""
        try:
            super().commit()
        except IntegrityError as error:
            self.session.rollback()
            detail = str(error.orig)
            if "name_key" in detail:
                raise DuplicateHouseholdName() from error
            if "companion_of_id" in detail:
                raise CompanionAlreadyExists() from error
            raise
