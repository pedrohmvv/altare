from sqlalchemy import inspect
from sqlalchemy.orm import relationship

from wedding.modules.guests.domain.entities import Guest, GuestStatusChange, Household
from wedding.modules.guests.infrastructure.tables import (
    guest_households,
    guest_status_changes,
    guests,
)
from wedding.platform.db.metadata import mapper_registry


def start_mappers() -> None:
    """Liga as dataclasses do domínio às tabelas; pode ser chamada mais de uma vez.

    O domínio não tem associações entre as entidades, mas o ORM só sabe a ordem de gravação (o
    núcleo antes da pessoa, a pessoa antes do histórico) por um `relationship`. Ele nunca é lido
    nem preenchido (`lazy="raise"`): serve só para ordenar o `INSERT`.
    """
    if inspect(Household, raiseerr=False) is None:
        mapper_registry.map_imperatively(
            Household, guest_households, version_id_col=guest_households.c.version
        )
    if inspect(Guest, raiseerr=False) is None:
        mapper_registry.map_imperatively(
            Guest,
            guests,
            version_id_col=guests.c.version,
            properties={"_household": relationship(Household, lazy="raise")},
        )
    if inspect(GuestStatusChange, raiseerr=False) is None:
        mapper_registry.map_imperatively(
            GuestStatusChange,
            guest_status_changes,
            version_id_col=guest_status_changes.c.version,
            properties={"_guest": relationship(Guest, lazy="raise")},
        )
