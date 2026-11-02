from sqlalchemy import inspect

from wedding.modules.schedule.domain.entities import Milestone, MilestoneChange, Phase
from wedding.modules.schedule.infrastructure.tables import (
    milestone_changes,
    milestones,
    schedule_phases,
)
from wedding.platform.db.metadata import mapper_registry


def start_mappers() -> None:
    """Liga as dataclasses do domínio às tabelas; pode ser chamada mais de uma vez. A janela
    sugerida e as dependências ficam só nas tabelas por enquanto: nenhuma regra deste PR as usa."""
    for entity, table in (
        (Phase, schedule_phases),
        (Milestone, milestones),
        (MilestoneChange, milestone_changes),
    ):
        if inspect(entity, raiseerr=False) is None:
            mapper_registry.map_imperatively(entity, table, version_id_col=table.c.version)
