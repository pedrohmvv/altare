"""guest settings

Revision ID: 0008
Revises: 0007
"""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

import sqlalchemy as sa
from alembic import op

revision: str = "0008"
down_revision: str | None = "0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# A semente (F-CNV-06): uma linha com pesos e limites de idade vazios, porque são decisões do
# casal e nenhum valor é presumido (`D-030`). O id é fixo para a migration dar o mesmo resultado
# em qualquer banco.
SEED_ID = uuid.UUID("5b0a7a58-3a5f-5b4a-8d7e-6f1d2c9e4b10")


def upgrade() -> None:
    settings = op.create_table(
        "guest_settings",
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
        sa.Column(
            "weight_certain_pct",
            sa.Integer(),
            comment="Peso de Certeza no Estimado Ponderado, de 0 a 100; nulo até o casal definir.",
        ),
        sa.Column(
            "weight_probable_pct",
            sa.Integer(),
            comment="Peso de Provável, de 0 a 100; nulo até definir.",
        ),
        sa.Column(
            "weight_phase_2_pct",
            sa.Integer(),
            comment="Peso de Fase 2, de 0 a 100; nulo até definir.",
        ),
        sa.Column(
            "exempt_until_age",
            sa.Integer(),
            comment="Criança isenta até esta idade; nulo até definir.",
        ),
        sa.Column(
            "paying_until_age",
            sa.Integer(),
            comment="Criança pagante até esta idade; nulo até definir.",
        ),
        sa.CheckConstraint(
            "(weight_certain_pct IS NULL) = (weight_probable_pct IS NULL) "
            "AND (weight_probable_pct IS NULL) = (weight_phase_2_pct IS NULL)",
            name=op.f("ck_guest_settings_weights_all_or_none"),
        ),
        sa.CheckConstraint(
            "(weight_certain_pct IS NULL OR weight_certain_pct BETWEEN 0 AND 100) "
            "AND (weight_probable_pct IS NULL OR weight_probable_pct BETWEEN 0 AND 100) "
            "AND (weight_phase_2_pct IS NULL OR weight_phase_2_pct BETWEEN 0 AND 100)",
            name=op.f("ck_guest_settings_weights_between_0_and_100"),
        ),
        sa.CheckConstraint(
            "(exempt_until_age IS NULL OR exempt_until_age BETWEEN 0 AND 17) "
            "AND (paying_until_age IS NULL OR paying_until_age BETWEEN 0 AND 17)",
            name=op.f("ck_guest_settings_ages_between_0_and_17"),
        ),
        sa.CheckConstraint(
            "exempt_until_age IS NULL OR paying_until_age IS NULL "
            "OR exempt_until_age <= paying_until_age",
            name=op.f("ck_guest_settings_exempt_not_above_paying"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_guest_settings")),
        comment="Pesos e limites de idade da lista (F-CNV-03 e F-CNV-06): uma linha.",
    )
    now = datetime.now(UTC)
    op.bulk_insert(settings, [{"id": SEED_ID, "created_at": now, "updated_at": now, "version": 1}])


def downgrade() -> None:
    op.drop_table("guest_settings")
