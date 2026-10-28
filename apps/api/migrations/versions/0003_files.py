"""files

Revision ID: 0003
Revises: 0002
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "file_assets",
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
            "original_name",
            sa.String(120),
            nullable=False,
            comment="Nome que a pessoa deu; só exibição.",
        ),
        sa.Column(
            "content_type",
            sa.String(20),
            nullable=False,
            comment="Tipo pela assinatura real do arquivo.",
        ),
        sa.Column(
            "size_bytes", sa.BigInteger(), nullable=False, comment="Tamanho do conteúdo em bytes."
        ),
        sa.Column(
            "sha256",
            sa.String(64),
            nullable=False,
            comment="SHA-256 do conteúdo; a chave no storage.",
        ),
        sa.CheckConstraint(
            "content_type IN ('application/pdf', 'image/jpeg', 'image/png', 'image/webp')",
            name=op.f("ck_file_assets_file_kind"),
        ),
        sa.CheckConstraint("size_bytes > 0", name=op.f("ck_file_assets_size_positive")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_file_assets")),
        comment="Um registro por envio; o mesmo conteúdo, de mesmo hash, fica uma vez no storage.",
    )
    op.create_index("ix_file_assets_sha256", "file_assets", ["sha256"])


def downgrade() -> None:
    op.drop_index("ix_file_assets_sha256", table_name="file_assets")
    op.drop_table("file_assets")
