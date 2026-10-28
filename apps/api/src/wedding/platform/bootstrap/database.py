from threading import Lock

from sqlalchemy.orm import Session, sessionmaker

from wedding.platform.db.engine import create_db_engine, create_session_factory


class Database:
    """O banco do app, aberto só na primeira vez que alguém o pede e compartilhado pelos módulos:
    gerar o contrato OpenAPI e listar a ajuda da CLI não precisam dele."""

    def __init__(self, url: str) -> None:
        self._url = url
        self._lock = Lock()
        self._sessions: sessionmaker[Session] | None = None

    def sessions(self) -> sessionmaker[Session]:
        with self._lock:
            if self._sessions is None:
                self._sessions = create_session_factory(create_db_engine(self._url))
            return self._sessions
