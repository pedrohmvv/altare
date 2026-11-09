from sqlalchemy import inspect
from sqlalchemy.orm import relationship

from wedding.modules.schedule.domain.attachments import Attachment
from wedding.modules.schedule.domain.entities import (
    ChecklistItem,
    Milestone,
    MilestoneChange,
    MilestoneDependency,
    Phase,
    Task,
)
from wedding.modules.schedule.infrastructure.tables import (
    attachments,
    checklist_items,
    milestone_changes,
    milestone_dependencies,
    milestones,
    schedule_phases,
    schedule_tasks,
)
from wedding.platform.db.metadata import mapper_registry


def start_mappers() -> None:
    """Liga as dataclasses do domínio às tabelas; pode ser chamada mais de uma vez. A janela
    (`window_*`) e a marca de editada são colunas da própria entidade `Milestone`.

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
    if inspect(Task, raiseerr=False) is None:
        mapper_registry.map_imperatively(
            Task, schedule_tasks, version_id_col=schedule_tasks.c.version
        )
    if inspect(ChecklistItem, raiseerr=False) is None:
        # Cada item tem a `version` própria: marcar, editar e remover um item não toca o dono.
        mapper_registry.map_imperatively(
            ChecklistItem,
            checklist_items,
            version_id_col=checklist_items.c.version,
            properties={
                "_milestone": relationship(
                    Milestone, lazy="raise", foreign_keys=[checklist_items.c.milestone_id]
                ),
                "_task": relationship(Task, lazy="raise", foreign_keys=[checklist_items.c.task_id]),
            },
        )
    if inspect(Attachment, raiseerr=False) is None:
        # O dono não tem chave estrangeira (a tabela é genérica): o mapeamento só renomeia a coluna
        # `owner_type` para o `owner_kind` do domínio. Cada anexo tem a `version` própria.
        mapper_registry.map_imperatively(
            Attachment,
            attachments,
            version_id_col=attachments.c.version,
            properties={"owner_kind": attachments.c.owner_type},
        )
