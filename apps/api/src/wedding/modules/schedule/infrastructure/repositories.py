from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from wedding.modules.schedule.domain.entities import Dependency, Milestone, MilestoneChange, Phase
from wedding.modules.schedule.infrastructure.tables import (
    milestone_dependencies,
    milestones,
    schedule_phases,
)


class SqlScheduleRepository:
    """Tudo o que lê já filtra a exclusão lógica."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list_phases(self) -> list[Phase]:
        query = select(Phase).where(schedule_phases.c.deleted_at.is_(None))
        return list(self._session.execute(query).scalars())

    def list_milestones(self) -> list[Milestone]:
        query = select(Milestone).where(milestones.c.deleted_at.is_(None))
        return list(self._session.execute(query).scalars())

    def get_milestone(self, milestone_id: UUID) -> Milestone | None:
        query = select(Milestone).where(
            milestones.c.id == milestone_id, milestones.c.deleted_at.is_(None)
        )
        return self._session.execute(query).scalar_one_or_none()

    def dependencies(self) -> list[Dependency]:
        """Só os vínculos vivos, entre marcos vivos."""
        live = select(milestones.c.id).where(milestones.c.deleted_at.is_(None))
        query = select(
            milestone_dependencies.c.milestone_id, milestone_dependencies.c.depends_on_id
        ).where(
            milestone_dependencies.c.deleted_at.is_(None),
            milestone_dependencies.c.milestone_id.in_(live),
            milestone_dependencies.c.depends_on_id.in_(live),
        )
        return [
            Dependency(row.milestone_id, row.depends_on_id) for row in self._session.execute(query)
        ]

    def add_change(self, change: MilestoneChange) -> None:
        self._session.add(change)
