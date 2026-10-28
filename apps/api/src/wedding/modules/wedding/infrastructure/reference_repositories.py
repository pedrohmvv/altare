from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from wedding.modules.wedding.domain.reference import ScopeReference
from wedding.modules.wedding.infrastructure.reference_tables import scope_references


class SqlReferenceRepository:
    """Só lê as não removidas: a exclusão é lógica (architecture.md §10)."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, reference: ScopeReference) -> None:
        self._session.add(reference)

    def get(self, reference_id: UUID) -> ScopeReference | None:
        query = select(ScopeReference).where(
            scope_references.c.id == reference_id, scope_references.c.deleted_at.is_(None)
        )
        return self._session.execute(query).scalar_one_or_none()

    def list_for(self, category_id: UUID) -> list[ScopeReference]:
        query = (
            select(ScopeReference)
            .where(
                scope_references.c.category_id == category_id,
                scope_references.c.deleted_at.is_(None),
            )
            .order_by(scope_references.c.created_at.desc(), scope_references.c.id.desc())
        )
        return list(self._session.execute(query).scalars())
