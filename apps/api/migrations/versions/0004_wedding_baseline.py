"""wedding baseline

Revision ID: 0004
Revises: 0003
"""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# A semente (F-PLN-01): as seis variáveis nascem vazias e `Em definição`. Os ids são fixos para a
# migration dar o mesmo resultado em qualquer banco; nenhum valor do casamento é inventado.
SEED_KEYS = ("date", "city", "format", "size", "ceiling", "ceremony")
SEED_NAMESPACE = uuid.UUID("0d9a6a52-6a6e-5a2f-9f43-1c5c5a1e7a00")


def _audit_columns() -> list[sa.Column]:
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
    baseline_fields = op.create_table(
        "baseline_fields",
        *_audit_columns(),
        sa.Column(
            "field_key", sa.String(10), nullable=False, comment="Qual variável do casamento."
        ),
        sa.Column("status", sa.String(16), nullable=False, comment="Em definição ou Definido."),
        sa.Column(
            "value",
            sa.JSON(none_as_null=True),
            comment="O valor, validado pelo domínio; nulo enquanto o campo está vazio.",
        ),
        sa.Column("note", sa.String(500), comment="Por que estamos em dúvida; texto livre."),
        sa.CheckConstraint(
            "field_key IN ('date', 'city', 'format', 'size', 'ceiling', 'ceremony')",
            name=op.f("ck_baseline_fields_baseline_key"),
        ),
        sa.CheckConstraint(
            "status IN ('Em definição', 'Definido')",
            name=op.f("ck_baseline_fields_definition_status"),
        ),
        sa.CheckConstraint(
            "status != 'Definido' OR value IS NOT NULL",
            name=op.f("ck_baseline_fields_defined_has_value"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_baseline_fields")),
        sa.UniqueConstraint("field_key", name=op.f("uq_baseline_fields_field_key")),
        comment=(
            "Definições Base do casamento (F-PLN-01): "
            "uma linha por variável, criadas pela migration."
        ),
    )
    op.create_table(
        "baseline_changes",
        *_audit_columns(),
        sa.Column("field_key", sa.String(10), nullable=False, comment="Qual variável mudou."),
        sa.Column(
            "state_before",
            sa.JSON(),
            nullable=False,
            comment="Status, valor e nota antes da mudança.",
        ),
        sa.Column(
            "state_after",
            sa.JSON(),
            nullable=False,
            comment="Status, valor e nota depois da mudança.",
        ),
        sa.Column(
            "profile",
            sa.String(8),
            nullable=False,
            comment="Perfil de quem mudou, para o histórico não depender do cadastro de usuários.",
        ),
        sa.CheckConstraint(
            "field_key IN ('date', 'city', 'format', 'size', 'ceiling', 'ceremony')",
            name=op.f("ck_baseline_changes_baseline_key"),
        ),
        sa.CheckConstraint(
            "profile IN ('Noivo', 'Noiva', 'Ambos')", name=op.f("ck_baseline_changes_profile_kind")
        ),
        sa.CheckConstraint("profile != 'Ambos'", name=op.f("ck_baseline_changes_profile_is_login")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_baseline_changes")),
        comment="Histórico das Definições Base (F-PLN-01, regra 3): só se acrescenta.",
    )
    op.create_index("ix_baseline_changes_created_at", "baseline_changes", ["created_at"])

    now = datetime.now(UTC)
    op.bulk_insert(
        baseline_fields,
        [
            {
                "id": uuid.uuid5(SEED_NAMESPACE, key),
                "created_at": now,
                "updated_at": now,
                "version": 1,
                "field_key": key,
                "status": "Em definição",
            }
            for key in SEED_KEYS
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_baseline_changes_created_at", table_name="baseline_changes")
    op.drop_table("baseline_changes")
    op.drop_table("baseline_fields")
