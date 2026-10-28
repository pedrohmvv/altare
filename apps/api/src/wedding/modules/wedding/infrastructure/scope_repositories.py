from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from wedding.modules.wedding.application.scope_dto import StatusChangeDto
from wedding.modules.wedding.domain.scope_entities import (
    ScopeCategory,
    ScopeEvaluation,
    ScopeGroup,
    ScopeStatusChange,
)
from wedding.modules.wedding.domain.scope_values import ScopeStatus
from wedding.modules.wedding.infrastructure.scope_tables import (
    scope_categories,
    scope_evaluations,
    scope_groups,
    scope_status_changes,
)
from wedding.shared_kernel.profile import ProfileKind


class SqlScopeRepository:
    """Lê com a exclusão lógica filtrada (architecture.md §10). Ocultas continuam aparecendo."""

    def __init__(self, session: Session) -> None:
        self._session = session

    # --- grupos

    def get_group(self, group_id: UUID) -> ScopeGroup | None:
        query = select(ScopeGroup).where(
            scope_groups.c.id == group_id, scope_groups.c.deleted_at.is_(None)
        )
        return self._session.execute(query).scalar_one_or_none()

    def list_groups(self) -> list[ScopeGroup]:
        query = select(ScopeGroup).where(scope_groups.c.deleted_at.is_(None))
        return list(self._session.execute(query).scalars())

    def add_group(self, group: ScopeGroup) -> None:
        self._session.add(group)

    def next_group_position(self) -> int:
        query = select(func.coalesce(func.max(scope_groups.c.position), -1) + 1).where(
            scope_groups.c.deleted_at.is_(None)
        )
        return int(self._session.execute(query).scalar_one())

    def group_name_taken(self, key: str, *, excluding: UUID | None = None) -> bool:
        return self._name_taken(scope_groups, key, excluding)

    def count_categories(self, group_id: UUID) -> int:
        query = select(func.count()).where(
            scope_categories.c.group_id == group_id, scope_categories.c.deleted_at.is_(None)
        )
        return int(self._session.execute(query).scalar_one())

    # --- categorias

    def get_category(self, category_id: UUID) -> ScopeCategory | None:
        query = select(ScopeCategory).where(
            scope_categories.c.id == category_id, scope_categories.c.deleted_at.is_(None)
        )
        return self._session.execute(query).scalar_one_or_none()

    def list_categories(self) -> list[ScopeCategory]:
        query = select(ScopeCategory).where(scope_categories.c.deleted_at.is_(None))
        return list(self._session.execute(query).scalars())

    def add_category(self, category: ScopeCategory) -> None:
        self._session.add(category)

    def next_category_position(self, group_id: UUID) -> int:
        query = select(func.coalesce(func.max(scope_categories.c.position), -1) + 1).where(
            scope_categories.c.group_id == group_id, scope_categories.c.deleted_at.is_(None)
        )
        return int(self._session.execute(query).scalar_one())

    def category_name_taken(self, key: str, *, excluding: UUID | None = None) -> bool:
        return self._name_taken(scope_categories, key, excluding)

    def _name_taken(self, table, key: str, excluding: UUID | None) -> bool:  # type: ignore[no-untyped-def]
        # Sem autoflush: a checagem roda depois de o caso de uso mexer na entidade, e o índice único
        # não pode estourar aqui como erro de banco antes de virar "nome já usado".
        query = select(func.count()).where(table.c.name_key == key, table.c.deleted_at.is_(None))
        if excluding is not None:
            query = query.where(table.c.id != excluding)
        with self._session.no_autoflush:
            return int(self._session.execute(query).scalar_one()) > 0

    # --- avaliações

    def get_evaluation(self, category_id: UUID, profile: ProfileKind) -> ScopeEvaluation | None:
        query = select(ScopeEvaluation).where(
            scope_evaluations.c.category_id == category_id, scope_evaluations.c.profile == profile
        )
        return self._session.execute(query).scalar_one_or_none()

    def list_evaluations(self) -> list[ScopeEvaluation]:
        live = select(scope_categories.c.id).where(scope_categories.c.deleted_at.is_(None))
        query = select(ScopeEvaluation).where(scope_evaluations.c.category_id.in_(live))
        return list(self._session.execute(query).scalars())

    def add_evaluation(self, evaluation: ScopeEvaluation) -> None:
        self._session.add(evaluation)

    # --- histórico

    def add_status_change(self, change: ScopeStatusChange) -> None:
        self._session.add(change)

    def status_history(self, category_id: UUID) -> list[StatusChangeDto]:
        table = scope_status_changes
        query = (
            select(
                table.c.id,
                table.c.from_status,
                table.c.to_status,
                table.c.reason,
                table.c.profile,
                table.c.created_at,
            )
            .where(table.c.category_id == category_id)
            .order_by(table.c.created_at.desc(), table.c.id.desc())
        )
        return [
            StatusChangeDto(
                id=row.id,
                from_status=row.from_status,
                to_status=row.to_status,
                reason=row.reason,
                profile=row.profile,
                changed_at=row.created_at,
            )
            for row in self._session.execute(query)
        ]

    def discard_reasons(self) -> dict[UUID, str | None]:
        table = scope_status_changes
        query = (
            select(table.c.category_id, table.c.reason)
            .where(table.c.to_status == ScopeStatus.OUT)
            .order_by(table.c.created_at, table.c.id)
        )
        return {row.category_id: row.reason for row in self._session.execute(query)}
