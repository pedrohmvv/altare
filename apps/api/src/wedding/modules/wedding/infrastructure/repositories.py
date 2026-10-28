from sqlalchemy import select
from sqlalchemy.orm import Session

from wedding.modules.wedding.application.dto import BaselineChangeDto, to_snapshot_dto
from wedding.modules.wedding.domain.entities import BaselineChange, BaselineField
from wedding.modules.wedding.domain.value_objects import BaselineKey
from wedding.modules.wedding.infrastructure.tables import baseline_changes, baseline_fields


class SqlBaselineRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, key: BaselineKey) -> BaselineField | None:
        query = select(BaselineField).where(
            baseline_fields.c.field_key == key, baseline_fields.c.deleted_at.is_(None)
        )
        return self._session.execute(query).scalar_one_or_none()

    def all(self) -> list[BaselineField]:
        query = select(BaselineField).where(baseline_fields.c.deleted_at.is_(None))
        return list(self._session.execute(query).scalars())

    def add_change(self, change: BaselineChange) -> None:
        self._session.add(change)

    def changes(self, limit: int) -> list[BaselineChangeDto]:
        """Consulta direta ao SQL, sem carregar entidades (architecture.md §3, item 3). O desempate
        pelo `id` mantém a ordem estável quando duas mudanças caem no mesmo instante."""
        query = (
            select(
                baseline_changes.c.id,
                baseline_changes.c.field_key,
                baseline_changes.c.state_before,
                baseline_changes.c.state_after,
                baseline_changes.c.profile,
                baseline_changes.c.created_at,
            )
            .where(baseline_changes.c.deleted_at.is_(None))
            .order_by(baseline_changes.c.created_at.desc(), baseline_changes.c.id.desc())
            .limit(limit)
        )
        return [
            BaselineChangeDto(
                id=row.id,
                key=row.field_key,
                before=to_snapshot_dto(row.field_key, row.state_before),
                after=to_snapshot_dto(row.field_key, row.state_after),
                profile=row.profile,
                changed_at=row.created_at,
            )
            for row in self._session.execute(query)
        ]
