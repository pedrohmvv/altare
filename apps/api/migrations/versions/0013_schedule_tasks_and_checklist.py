"""schedule tasks and checklist

Revision ID: 0013
Revises: 0012
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0013"
down_revision: str | None = "0012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

PROFILES = "'Noivo', 'Noiva', 'Ambos'"
TASK_STATES = "'A fazer', 'Em andamento', 'Concluída'"


def _audit_columns() -> list[sa.Column]:  # type: ignore[type-arg]
    return [
        sa.Column("id", sa.Uuid(), nullable=False, comment="Identificador do registro (UUID)."),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            comment="Instante da criação, em UTC.",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            comment="Instante da última alteração.",
        ),
        sa.Column(
            "created_by", sa.Uuid(), comment="Usuário da sessão que criou; nulo se veio da CLI."
        ),
        sa.Column("updated_by", sa.Uuid(), comment="Usuário da sessão que alterou por último."),
        sa.Column(
            "deleted_at",
            sa.DateTime(timezone=True),
            comment="Instante da exclusão lógica; nulo se ativo.",
        ),
        sa.Column("deleted_by", sa.Uuid(), comment="Usuário da sessão que excluiu."),
        sa.Column("version", sa.Integer(), nullable=False, comment="Bloqueio otimista."),
    ]


def upgrade() -> None:
    # Só tabelas novas: nenhuma tabela existente é alterada, então não há lote nem `PRAGMA`, e a
    # semente do cronograma não muda.
    live = sa.text("deleted_at IS NULL")
    op.create_table(
        "schedule_tasks",
        *_audit_columns(),
        sa.Column(
            "title", sa.String(120), nullable=False, comment="O nome da tarefa avulsa; exibido."
        ),
        sa.Column(
            "responsible",
            sa.String(8),
            nullable=False,
            comment="Noivo, Noiva ou Ambos; por padrão, o perfil de quem criou (F-CRN-06).",
        ),
        sa.Column("note", sa.String(500), comment="Nota livre."),
        sa.Column(
            "target_date",
            sa.Date(),
            comment=(
                "Prazo digitado à mão; nulo se não há. O Atrasada e os dias que faltam se derivam "
                "dele na leitura e nunca se gravam."
            ),
        ),
        sa.Column(
            "state",
            sa.String(12),
            nullable=False,
            comment=(
                "A fazer, Em andamento ou Concluída (feminino, diferente do Concluído do marco)."
            ),
        ),
        sa.CheckConstraint(
            "length(trim(title)) > 0", name=op.f("ck_schedule_tasks_title_not_blank")
        ),
        sa.CheckConstraint(
            f"responsible IN ({PROFILES})", name=op.f("ck_schedule_tasks_task_responsible")
        ),
        sa.CheckConstraint(f"state IN ({TASK_STATES})", name=op.f("ck_schedule_tasks_task_state")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_schedule_tasks")),
        comment=(
            "Tarefas avulsas do cronograma (F-CRN-06): sem fase, categoria nem dependências, fora "
            "da derivação dos marcos. Atrasada se deriva na leitura."
        ),
    )
    op.create_table(
        "checklist_items",
        *_audit_columns(),
        sa.Column(
            "milestone_id",
            sa.Uuid(),
            comment="O marco dono do item; nulo se o dono é uma tarefa avulsa.",
        ),
        sa.Column(
            "task_id",
            sa.Uuid(),
            comment="A tarefa avulsa dona do item; nulo se o dono é um marco.",
        ),
        sa.Column("text", sa.String(200), nullable=False, comment="O que fazer; exibido."),
        sa.Column(
            "done",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
            comment="Verdadeiro se o item foi feito; nunca muda o estado do dono (F-CRN-07).",
        ),
        sa.Column(
            "position",
            sa.Integer(),
            nullable=False,
            comment="Ordem entre os itens vivos do dono, a partir de zero; pode ter buracos.",
        ),
        sa.CheckConstraint(
            "length(trim(text)) > 0", name=op.f("ck_checklist_items_text_not_blank")
        ),
        sa.CheckConstraint("position >= 0", name=op.f("ck_checklist_items_position_not_negative")),
        sa.CheckConstraint(
            "(milestone_id IS NOT NULL AND task_id IS NULL) "
            "OR (milestone_id IS NULL AND task_id IS NOT NULL)",
            name=op.f("ck_checklist_items_one_owner"),
        ),
        sa.ForeignKeyConstraint(
            ["milestone_id"],
            ["milestones.id"],
            name=op.f("fk_checklist_items_milestone_id_milestones"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["task_id"],
            ["schedule_tasks.id"],
            name=op.f("fk_checklist_items_task_id_schedule_tasks"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_checklist_items")),
        comment=(
            "Itens do checklist (F-CRN-07) de um marco ou de uma tarefa avulsa: exatamente um dos "
            "dois donos. Sair é exclusão lógica; o dono excluído esconde os itens, sem apagá-los."
        ),
    )
    # Não únicos: reordenar passa por posições repetidas antes de fechar a permutação.
    op.create_index(
        "ix_checklist_items_milestone_live",
        "checklist_items",
        ["milestone_id", "position"],
        sqlite_where=live,
        postgresql_where=live,
    )
    op.create_index(
        "ix_checklist_items_task_live",
        "checklist_items",
        ["task_id", "position"],
        sqlite_where=live,
        postgresql_where=live,
    )


def downgrade() -> None:
    # Ordem inversa: os itens apontam para as avulsas e para os marcos.
    op.drop_index("ix_checklist_items_task_live", table_name="checklist_items")
    op.drop_index("ix_checklist_items_milestone_live", table_name="checklist_items")
    op.drop_table("checklist_items")
    op.drop_table("schedule_tasks")
