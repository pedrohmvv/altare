"""schedule attachments

Revision ID: 0014
Revises: 0013
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0014"
down_revision: str | None = "0013"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

PROFILES = "'Noivo', 'Noiva', 'Ambos'"
OWNER_TYPES = "'milestones', 'tasks'"
KINDS = "'link', 'file'"


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
    # Só uma tabela nova: nenhuma tabela existente é alterada, então não há lote nem `PRAGMA`.
    live = sa.text("deleted_at IS NULL")
    op.create_table(
        "attachments",
        *_audit_columns(),
        sa.Column(
            "owner_type",
            sa.String(10),
            nullable=False,
            comment="De quem é o anexo: milestones (um marco) ou tasks (uma tarefa avulsa).",
        ),
        sa.Column(
            "owner_id",
            sa.Uuid(),
            nullable=False,
            comment=(
                "O id do marco ou da avulsa, conforme owner_type. Sem chave estrangeira: a tabela "
                "é genérica e a integridade fica no caso de uso e no leitor (D-080)."
            ),
        ),
        sa.Column("kind", sa.String(4), nullable=False, comment="link ou file."),
        sa.Column(
            "profile",
            sa.String(8),
            nullable=False,
            comment="Quem anexou; só esse perfil remove (F-CRN-08).",
        ),
        sa.Column("url", sa.String(2000), comment="O endereço, já validado; nulo para arquivo."),
        sa.Column(
            "file_id",
            sa.Uuid(),
            comment="O arquivo enviado pelo módulo de arquivos; nulo para link.",
        ),
        sa.Column(
            "file_name",
            sa.String(120),
            comment="Cópia do nome do arquivo ao anexar; nulo para link. O arquivo é imutável.",
        ),
        sa.Column(
            "content_type",
            sa.String(20),
            comment="Cópia do tipo do arquivo ao anexar (PDF ou imagem); nulo para link.",
        ),
        sa.Column(
            "size_bytes",
            sa.BigInteger(),
            comment="Cópia do tamanho do arquivo em bytes ao anexar; nulo para link.",
        ),
        sa.Column("title", sa.String(120), comment="Texto curto, opcional."),
        sa.Column("comment", sa.String(500), comment="Texto livre, opcional."),
        sa.CheckConstraint(
            f"owner_type IN ({OWNER_TYPES})", name=op.f("ck_attachments_attachment_owner_type")
        ),
        sa.CheckConstraint(f"kind IN ({KINDS})", name=op.f("ck_attachments_attachment_kind")),
        sa.CheckConstraint(f"profile IN ({PROFILES})", name=op.f("ck_attachments_profile_kind")),
        sa.CheckConstraint("profile != 'Ambos'", name=op.f("ck_attachments_profile_is_login")),
        sa.CheckConstraint(
            "(kind = 'link' AND url IS NOT NULL AND file_id IS NULL AND file_name IS NULL "
            "AND content_type IS NULL AND size_bytes IS NULL) "
            "OR (kind = 'file' AND url IS NULL AND file_id IS NOT NULL AND file_name IS NOT NULL "
            "AND content_type IS NOT NULL AND size_bytes IS NOT NULL)",
            name=op.f("ck_attachments_kind_matches_content"),
        ),
        sa.ForeignKeyConstraint(
            ["file_id"],
            ["file_assets.id"],
            name=op.f("fk_attachments_file_id_file_assets"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_attachments")),
        comment=(
            "Anexos de marcos e de tarefas avulsas (F-CRN-08): um link ou um arquivo já enviado, "
            "com a cópia do nome, tipo e tamanho. Sair é exclusão lógica; o dono excluído esconde "
            "os anexos, sem apagá-los."
        ),
    )
    op.create_index(
        "ix_attachments_owner_live",
        "attachments",
        ["owner_type", "owner_id", "created_at"],
        sqlite_where=live,
        postgresql_where=live,
    )


def downgrade() -> None:
    op.drop_index("ix_attachments_owner_live", table_name="attachments")
    op.drop_table("attachments")
