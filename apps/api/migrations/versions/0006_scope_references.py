"""scope references

Revision ID: 0006
Revises: 0005
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "scope_references",
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
            "category_id",
            sa.Uuid(),
            nullable=False,
            comment="A frente em que a inspiração foi guardada.",
        ),
        sa.Column("kind", sa.String(8), nullable=False, comment="link ou imagem."),
        sa.Column(
            "profile",
            sa.String(8),
            nullable=False,
            comment="Quem adicionou; só esse perfil remove (F-PLN-06).",
        ),
        sa.Column("url", sa.String(2000), comment="O endereço, já validado; nulo para imagem."),
        sa.Column(
            "file_id",
            sa.Uuid(),
            comment="O arquivo da imagem, enviado pelo módulo de arquivos; nulo para link.",
        ),
        sa.Column("title", sa.String(120), comment="Texto curto, opcional."),
        sa.Column("comment", sa.String(500), comment="Texto livre, opcional."),
        sa.CheckConstraint(
            "kind IN ('link', 'imagem')", name=op.f("ck_scope_references_reference_kind")
        ),
        sa.CheckConstraint(
            "profile IN ('Noivo', 'Noiva', 'Ambos')", name=op.f("ck_scope_references_profile_kind")
        ),
        sa.CheckConstraint(
            "(kind = 'link' AND url IS NOT NULL AND file_id IS NULL) "
            "OR (kind = 'imagem' AND file_id IS NOT NULL AND url IS NULL)",
            name=op.f("ck_scope_references_kind_matches_content"),
        ),
        sa.CheckConstraint("profile != 'Ambos'", name=op.f("ck_scope_references_profile_is_login")),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["scope_categories.id"],
            name=op.f("fk_scope_references_category_id_scope_categories"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["file_id"],
            ["file_assets.id"],
            name=op.f("fk_scope_references_file_id_file_assets"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_scope_references")),
        comment="Referências de inspiração por frente, link ou imagem (F-PLN-06).",
    )
    op.create_index(
        "ix_scope_references_category_id", "scope_references", ["category_id", "created_at"]
    )


def downgrade() -> None:
    op.drop_index("ix_scope_references_category_id", table_name="scope_references")
    op.drop_table("scope_references")
