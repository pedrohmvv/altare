from sqlalchemy import inspect
from sqlalchemy.orm import relationship

from wedding.modules.schedule.domain.entities import (
    Milestone,
    MilestoneChange,
    MilestoneDependency,
    Phase,
)
from wedding.modules.schedule.infrastructure.tables import (
    milestone_changes,
    milestone_dependencies,
    milestones,
    schedule_phases,
)
from wedding.platform.db.metadata import mapper_registry


def start_mappers() -> None:
    """Liga as dataclasses do domínio às tabelas; pode ser chamada mais de uma vez. A janela
    sugerida fica só na tabela por enquanto: nenhuma regra a usa.

    O domínio não tem associações entre as entidades, mas o ORM só sabe a ordem de gravação (a
    fase antes do marco, o marco antes do vínculo) por um `relationship`. Ele nunca é lido nem
    preenchido (`lazy="raise"`): serve só para ordenar o `INSERT`.
    """
    if inspect(Phase, raiseerr=False) is None:
        mapper_registry.map_imperatively(
            Phase, schedule_phases, version_id_col=schedule_phases.c.version
        )
    if inspect(Milestone, raiseerr=False) is None:
        mapper_registry.map_imperatively(
            Milestone,
            milestones,
            version_id_col=milestones.c.version,
            properties={"_phase": relationship(Phase, lazy="raise")},
        )
    if inspect(MilestoneDependency, raiseerr=False) is None:
        mapper_registry.map_imperatively(
            MilestoneDependency,
            milestone_dependencies,
            version_id_col=milestone_dependencies.c.version,
            properties={
                "_milestone": relationship(
                    Milestone,
                    lazy="raise",
                    foreign_keys=[milestone_dependencies.c.milestone_id],
                ),
                "_predecessor": relationship(
                    Milestone,
                    lazy="raise",
                    foreign_keys=[milestone_dependencies.c.depends_on_id],
                ),
            },
        )
    if inspect(MilestoneChange, raiseerr=False) is None:
        mapper_registry.map_imperatively(
            MilestoneChange,
            milestone_changes,
            version_id_col=milestone_changes.c.version,
            properties={"_milestone": relationship(Milestone, lazy="raise")},
        )
