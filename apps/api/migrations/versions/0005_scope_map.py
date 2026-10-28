"""scope map

Revision ID: 0005
Revises: 0004
"""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# A semente (F-PLN-02): os 8 grupos e as 18 frentes do catálogo, todos `Em discussão`, sem
# estimativa e com o par de avaliações vazio. Os ids são fixos para a migration dar o mesmo
# resultado em qualquer banco; nenhum valor do casamento é inventado.
SEED_NAMESPACE = uuid.UUID("5c0e7a6e-2b0d-5f61-9a39-6c1d7e0f5a01")
CATALOG = [
    ("Cerimônia", ["Cerimônia civil", "Cerimônia religiosa ou simbólica"]),
    ("Espaço e alimentação", ["Espaço", "Buffet", "Bebidas e bar", "Bolo e doces"]),
    ("Registro", ["Fotografia", "Vídeo"]),
    ("Som e ambiente", ["Música (DJ, banda)", "Decoração e flores", "Iluminação e som"]),
    ("Estética", ["Trajes", "Beleza (noivos)"]),
    ("Papelaria e lembranças", ["Convites e papelaria", "Lembrancinhas"]),
    ("Condução", ["Cerimonial do dia"]),
    ("Pós-festa", ["Noite de núpcias", "Lua de mel"]),
]
STATUSES = "'Em discussão', 'Entra (Essencial)', 'Talvez (Se couber)', 'Fica de fora'"


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


def _name_columns() -> list[sa.Column]:  # type: ignore[type-arg]
    return [
        sa.Column("name", sa.String(60), nullable=False, comment="Como o casal chama; exibido."),
        sa.Column(
            "name_key",
            sa.String(120),
            nullable=False,
            comment="Nome sem caixa nem espaços repetidos: a chave de unicidade entre os vivos.",
        ),
        sa.Column("position", sa.Integer(), nullable=False, comment="Ordem de exibição."),
        sa.Column(
            "origin",
            sa.String(8),
            nullable=False,
            comment="catalogo veio com o Altare e só se oculta; casal foi criado por vocês.",
        ),
        sa.Column(
            "hidden_at",
            sa.DateTime(timezone=True),
            comment="Quando saiu das telas; nulo se visível.",
        ),
    ]


def _key(name: str) -> str:
    return " ".join(name.split()).casefold()


def upgrade() -> None:
    live = sa.text("deleted_at IS NULL")
    groups = op.create_table(
        "scope_groups",
        *_audit_columns(),
        *_name_columns(),
        sa.CheckConstraint(
            "origin IN ('catalogo', 'casal')", name=op.f("ck_scope_groups_scope_origin")
        ),
        sa.CheckConstraint("position >= 0", name=op.f("ck_scope_groups_position_not_negative")),
        sa.CheckConstraint(
            "origin = 'casal' OR deleted_at IS NULL",
            name=op.f("ck_scope_groups_catalog_not_deleted"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_scope_groups")),
        comment="Grupos de frentes do casamento (F-PLN-02).",
    )
    op.create_index(
        "uq_scope_groups_name_key_live",
        "scope_groups",
        ["name_key"],
        unique=True,
        sqlite_where=live,
        postgresql_where=live,
    )
    categories = op.create_table(
        "scope_categories",
        *_audit_columns(),
        sa.Column("group_id", sa.Uuid(), nullable=False, comment="O grupo da frente."),
        *_name_columns(),
        sa.Column(
            "status", sa.String(20), nullable=False, comment="A decisão conjunta (F-PLN-03)."
        ),
        sa.Column(
            "estimate_cents",
            sa.BigInteger(),
            comment="Estimativa inicial em centavos; nula é sem estimativa, nunca zero (F-PLN-05).",
        ),
        sa.CheckConstraint(
            "origin IN ('catalogo', 'casal')", name=op.f("ck_scope_categories_scope_origin")
        ),
        sa.CheckConstraint(
            f"status IN ({STATUSES})", name=op.f("ck_scope_categories_scope_status")
        ),
        sa.CheckConstraint("position >= 0", name=op.f("ck_scope_categories_position_not_negative")),
        sa.CheckConstraint(
            "estimate_cents IS NULL OR estimate_cents > 0",
            name=op.f("ck_scope_categories_estimate_positive"),
        ),
        sa.CheckConstraint(
            "origin = 'casal' OR deleted_at IS NULL",
            name=op.f("ck_scope_categories_catalog_not_deleted"),
        ),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["scope_groups.id"],
            name=op.f("fk_scope_categories_group_id_scope_groups"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_scope_categories")),
        comment="Frentes do casamento e a decisão conjunta sobre cada uma (F-PLN-02 e F-PLN-03).",
    )
    op.create_index(
        "uq_scope_categories_name_key_live",
        "scope_categories",
        ["name_key"],
        unique=True,
        sqlite_where=live,
        postgresql_where=live,
    )
    op.create_index("ix_scope_categories_group_id", "scope_categories", ["group_id"])
    evaluations = op.create_table(
        "scope_evaluations",
        *_audit_columns(),
        sa.Column("category_id", sa.Uuid(), nullable=False, comment="A frente avaliada."),
        sa.Column(
            "profile",
            sa.String(8),
            nullable=False,
            comment="Quem avalia; cada frente tem uma linha por perfil desde que nasce.",
        ),
        sa.Column(
            "priority",
            sa.String(12),
            comment="Quero muito, Se couber ou Dispenso; nula enquanto não avaliou.",
        ),
        sa.Column("note", sa.String(500), comment="O que esse perfil espera da frente."),
        sa.CheckConstraint(
            "profile IN ('Noivo', 'Noiva', 'Ambos')",
            name=op.f("ck_scope_evaluations_profile_kind"),
        ),
        sa.CheckConstraint(
            "priority IN ('Quero muito', 'Se couber', 'Dispenso')",
            name=op.f("ck_scope_evaluations_scope_priority"),
        ),
        sa.CheckConstraint(
            "profile != 'Ambos'", name=op.f("ck_scope_evaluations_profile_is_login")
        ),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["scope_categories.id"],
            name=op.f("fk_scope_evaluations_category_id_scope_categories"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_scope_evaluations")),
        sa.UniqueConstraint(
            "category_id", "profile", name=op.f("uq_scope_evaluations_category_id")
        ),
        comment="Prioridade e nota de cada perfil por frente (F-PLN-04 e F-PLN-05).",
    )
    op.create_table(
        "scope_status_changes",
        *_audit_columns(),
        sa.Column("category_id", sa.Uuid(), nullable=False, comment="A frente que mudou."),
        sa.Column("from_status", sa.String(20), nullable=False),
        sa.Column("to_status", sa.String(20), nullable=False),
        sa.Column("reason", sa.String(300), comment="Por que ficou de fora; só para Fica de fora."),
        sa.Column(
            "profile",
            sa.String(8),
            nullable=False,
            comment="Perfil de quem mudou, gravado para não depender do cadastro de usuários.",
        ),
        sa.CheckConstraint(
            f"from_status IN ({STATUSES})", name=op.f("ck_scope_status_changes_scope_status_from")
        ),
        sa.CheckConstraint(
            f"to_status IN ({STATUSES})", name=op.f("ck_scope_status_changes_scope_status_to")
        ),
        sa.CheckConstraint(
            "profile IN ('Noivo', 'Noiva', 'Ambos')",
            name=op.f("ck_scope_status_changes_profile_kind"),
        ),
        sa.CheckConstraint(
            "from_status != to_status", name=op.f("ck_scope_status_changes_status_changed")
        ),
        sa.CheckConstraint(
            "to_status != 'Fica de fora' OR (reason IS NOT NULL AND length(trim(reason)) > 0)",
            name=op.f("ck_scope_status_changes_discard_has_reason"),
        ),
        sa.CheckConstraint(
            "profile != 'Ambos'", name=op.f("ck_scope_status_changes_profile_is_login")
        ),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["scope_categories.id"],
            name=op.f("fk_scope_status_changes_category_id_scope_categories"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_scope_status_changes")),
        comment="Histórico de status das frentes (F-PLN-03): só se acrescenta.",
    )
    op.create_index(
        "ix_scope_status_changes_category_id", "scope_status_changes", ["category_id", "created_at"]
    )

    now = datetime.now(UTC)
    audit = {"created_at": now, "updated_at": now, "version": 1}
    group_rows, category_rows, evaluation_rows = [], [], []
    for group_position, (group_name, names) in enumerate(CATALOG):
        group_id = uuid.uuid5(SEED_NAMESPACE, f"grupo:{group_name}")
        group_rows.append(
            {
                "id": group_id,
                "name": group_name,
                "name_key": _key(group_name),
                "position": group_position,
                "origin": "catalogo",
                **audit,
            }
        )
        for category_position, name in enumerate(names):
            category_id = uuid.uuid5(SEED_NAMESPACE, f"categoria:{name}")
            category_rows.append(
                {
                    "id": category_id,
                    "group_id": group_id,
                    "name": name,
                    "name_key": _key(name),
                    "position": category_position,
                    "origin": "catalogo",
                    "status": "Em discussão",
                    **audit,
                }
            )
            for profile in ("Noivo", "Noiva"):
                evaluation_rows.append(
                    {
                        "id": uuid.uuid5(SEED_NAMESPACE, f"avaliacao:{name}:{profile}"),
                        "category_id": category_id,
                        "profile": profile,
                        **audit,
                    }
                )
    op.bulk_insert(groups, group_rows)
    op.bulk_insert(categories, category_rows)
    op.bulk_insert(evaluations, evaluation_rows)


def downgrade() -> None:
    op.drop_index("ix_scope_status_changes_category_id", table_name="scope_status_changes")
    op.drop_table("scope_status_changes")
    op.drop_table("scope_evaluations")
    op.drop_index("ix_scope_categories_group_id", table_name="scope_categories")
    op.drop_index("uq_scope_categories_name_key_live", table_name="scope_categories")
    op.drop_table("scope_categories")
    op.drop_index("uq_scope_groups_name_key_live", table_name="scope_groups")
    op.drop_table("scope_groups")
