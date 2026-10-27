from sqlalchemy import inspect

from wedding.modules.identity.domain.entities import User, UserSession
from wedding.modules.identity.infrastructure.tables import user_sessions, users
from wedding.platform.db.metadata import mapper_registry


def start_mappers() -> None:
    """Liga as dataclasses do domínio às tabelas; pode ser chamada mais de uma vez."""
    if inspect(User, raiseerr=False) is None:
        mapper_registry.map_imperatively(User, users, version_id_col=users.c.version)
    if inspect(UserSession, raiseerr=False) is None:
        mapper_registry.map_imperatively(UserSession, user_sessions)
