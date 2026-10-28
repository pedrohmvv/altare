from types import TracebackType
from typing import Self

from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm.exc import StaleDataError

from wedding.platform.db.audit import ACTOR_KEY, CLOCK_KEY
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.clock import Clock
from wedding.shared_kernel.errors import VersionConflict


class SqlAlchemyUnitOfWork:
    """Uma transação por caso de uso (architecture.md §3): o bloco `with` abre a sessão e,
    sem `commit()`, tudo é desfeito."""

    def __init__(
        self, session_factory: sessionmaker[Session], clock: Clock, actor: Actor | None = None
    ) -> None:
        self._factory = session_factory
        self._clock = clock
        self._actor = actor
        self._session: Session | None = None

    @property
    def session(self) -> Session:
        if self._session is None:
            raise RuntimeError("Usou a sessão fora de um bloco `with` da UnitOfWork")
        return self._session

    def __enter__(self) -> Self:
        self._session = self._factory()
        self._session.info[CLOCK_KEY] = self._clock
        self._session.info[ACTOR_KEY] = self._actor.user_id if self._actor else None
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        try:
            self.session.rollback()
        finally:
            self.session.close()
            self._session = None

    def act_as(self, actor: Actor) -> None:
        """Define o ator depois de abrir, quando só o caso de uso sabe quem age (o login)."""
        self._actor = actor
        self.session.info[ACTOR_KEY] = actor.user_id

    def commit(self) -> None:
        try:
            self.session.commit()
        except StaleDataError as error:
            self.session.rollback()
            raise VersionConflict() from error

    def rollback(self) -> None:
        self.session.rollback()
