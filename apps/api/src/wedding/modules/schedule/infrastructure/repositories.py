from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from wedding.modules.schedule.domain.entities import (
    Dependency,
    Milestone,
    MilestoneChange,
    MilestoneDependency,
    Phase,
)
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

    def get_phase(self, phase_id: UUID) -> Phase | None:
        query = select(Phase).where(
            schedule_phases.c.id == phase_id, schedule_phases.c.deleted_at.is_(None)
        )
        return self._session.execute(query).scalar_one_or_none()

    def add_phase(self, phase: Phase) -> None:
        self._session.add(phase)

    def next_phase_position(self) -> int:
        query = select(func.max(schedule_phases.c.position)).where(
            schedule_phases.c.deleted_at.is_(None)
        )
        highest = self._session.execute(query).scalar()
        return 0 if highest is None else highest + 1

    def get_milestone(
        self, milestone_id: UUID, *, include_deleted: bool = False
    ) -> Milestone | None:
        query = select(Milestone).where(milestones.c.id == milestone_id)
        if not include_deleted:
            query = query.where(milestones.c.deleted_at.is_(None))
        return self._session.execute(query).scalar_one_or_none()

    def add_milestone(self, milestone: Milestone) -> None:
        self._session.add(milestone)

    def next_milestone_position(self, phase_id: UUID) -> int:
        query = select(func.max(milestones.c.position)).where(
            milestones.c.phase_id == phase_id, milestones.c.deleted_at.is_(None)
        )
        highest = self._session.execute(query).scalar()
        return 0 if highest is None else highest + 1

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

    def live_links_of(self, milestone_id: UUID) -> list[MilestoneDependency]:
        return self._links_of(milestone_id, live=True)

    def deleted_links_of(self, milestone_id: UUID) -> list[MilestoneDependency]:
        return self._links_of(milestone_id, live=False)

    def _links_of(self, milestone_id: UUID, *, live: bool) -> list[MilestoneDependency]:
        deleted = milestone_dependencies.c.deleted_at
        query = select(MilestoneDependency).where(
            or_(
                milestone_dependencies.c.milestone_id == milestone_id,
                milestone_dependencies.c.depends_on_id == milestone_id,
            ),
            deleted.is_(None) if live else deleted.is_not(None),
        )
        return list(self._session.execute(query).scalars())

    def add_link(self, link: MilestoneDependency) -> None:
        self._session.add(link)

    def add_change(self, change: MilestoneChange) -> None:
        self._session.add(change)
