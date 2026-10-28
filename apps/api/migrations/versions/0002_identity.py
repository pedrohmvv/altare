"""identity

Revision ID: 0002
Revises: 0001
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
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
            "username", sa.String(32), nullable=False, comment="Usuário de login, em minúsculas."
        ),
        sa.Column(
            "profile",
            sa.String(8),
            nullable=False,
            comment="Noivo ou Noiva; Ambos não é um perfil de login.",
        ),
        sa.Column("password_hash", sa.String(), nullable=False, comment="Hash Argon2 da senha."),
        sa.CheckConstraint("profile IN ('Noivo', 'Noiva', 'Ambos')", name=op.f("ck_users_profile")),
        sa.CheckConstraint("profile != 'Ambos'", name=op.f("ck_users_profile_is_login")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        comment="Os dois logins do casal, criados só pela CLI.",
    )
    op.create_index(
        "uq_users_username_live",
        "users",
        ["username"],
        unique=True,
        sqlite_where=sa.text("deleted_at IS NULL"),
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index(
        "uq_users_profile_live",
        "users",
        ["profile"],
        unique=True,
        sqlite_where=sa.text("deleted_at IS NULL"),
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.create_table(
        "user_sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False, comment="SHA-256 do token."),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_user_sessions_user_id_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_sessions")),
        sa.UniqueConstraint("token_hash", name=op.f("uq_user_sessions_token_hash")),
        comment="Sessões abertas; o logout apaga a linha.",
    )
    op.create_index("ix_user_sessions_user_id", "user_sessions", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_user_sessions_user_id", table_name="user_sessions")
    op.drop_table("user_sessions")
    op.drop_index("uq_users_profile_live", table_name="users")
    op.drop_index("uq_users_username_live", table_name="users")
    op.drop_table("users")
