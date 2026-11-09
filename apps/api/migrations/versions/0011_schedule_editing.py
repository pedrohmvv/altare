"""schedule editing

Revision ID: 0011
Revises: 0010
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0011"
down_revision: str | None = "0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _foreign_keys(enabled: bool) -> None:
    """O lote recria a tabela (copia, apaga e renomeia), e apagar `milestones` com as dependências
    e o histórico apontando para ela falha com as chaves estrangeiras ligadas. O `PRAGMA` só vale
    fora de uma transação, então vem antes de qualquer escrita; o PostgreSQL não o conhece."""
    if op.get_bind().dialect.name == "sqlite":
        op.execute(sa.text(f"PRAGMA foreign_keys={'ON' if enabled else 'OFF'}"))


def upgrade() -> None:
    # Em lote, porque o SQLite não acrescenta restrição a uma tabela que já existe. A semente não
    # muda: os ids, os títulos e as posições seguem os da 0010.
    _foreign_keys(False)
    with op.batch_alter_table("milestones") as batch:
        batch.add_column(
            sa.Column(
                "dependencies_revision",
                sa.Integer(),
                nullable=False,
                server_default=sa.text("0"),
                comment="Sobe quando o conjunto de predecessores muda: duas edições se conflitam.",
            )
        )
        batch.create_check_constraint(
            op.f("ck_milestones_title_not_blank"), "length(trim(title)) > 0"
        )
        batch.create_check_constraint(
            op.f("ck_milestones_dependencies_revision_not_negative"), "dependencies_revision >= 0"
        )
    with op.batch_alter_table("schedule_phases") as batch:
        batch.create_check_constraint(
            op.f("ck_schedule_phases_title_not_blank"), "length(trim(title)) > 0"
        )
    _foreign_keys(True)


def downgrade() -> None:
    _foreign_keys(False)
    with op.batch_alter_table("schedule_phases") as batch:
        batch.drop_constraint(op.f("ck_schedule_phases_title_not_blank"), type_="check")
    with op.batch_alter_table("milestones") as batch:
        batch.drop_constraint(
            op.f("ck_milestones_dependencies_revision_not_negative"), type_="check"
        )
        batch.drop_constraint(op.f("ck_milestones_title_not_blank"), type_="check")
        batch.drop_column("dependencies_revision")
    _foreign_keys(True)
