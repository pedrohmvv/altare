from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    UniqueConstraint,
    Uuid,
    text,
)

from wedding.modules.wedding.domain.scope_values import Origin, Priority, ScopeStatus
from wedding.platform.db.audit import audit_columns
from wedding.platform.db.metadata import metadata
from wedding.platform.db.types import UtcDateTime
from wedding.shared_kernel.profile import ProfileKind

_LIVE = text("deleted_at IS NULL")


def _values(kind: type) -> list[str]:
    return [member.value for member in kind]  # type: ignore[attr-defined]


def _enum(kind: type, name: str, length: int) -> Enum:
    return Enum(
        kind,
        name=name,
        native_enum=False,
        create_constraint=True,
        length=length,
        values_callable=_values,
    )


def _name_columns() -> list[Column]:  # type: ignore[type-arg]
    return [
        Column("name", String(60), nullable=False, comment="Como o casal chama; exibido."),
        Column(
            "name_key",
            String(120),
            nullable=False,
            comment="Nome sem caixa nem espaços repetidos: a chave de unicidade entre os vivos.",
        ),
        Column("position", Integer, nullable=False, comment="Ordem de exibição."),
        Column(
            "origin",
            _enum(Origin, "scope_origin", 8),
            nullable=False,
            comment="catalogo veio com o Altare e só se oculta; casal foi criado por vocês.",
        ),
        Column("hidden_at", UtcDateTime, comment="Quando saiu das telas; nulo se visível."),
    ]


scope_groups = Table(
    "scope_groups",
    metadata,
    *audit_columns(),
    *_name_columns(),
    CheckConstraint("position >= 0", name="position_not_negative"),
    CheckConstraint("origin = 'casal' OR deleted_at IS NULL", name="catalog_not_deleted"),
    Index(
        "uq_scope_groups_name_key_live",
        "name_key",
        unique=True,
        sqlite_where=_LIVE,
        postgresql_where=_LIVE,
    ),
    comment="Grupos de frentes do casamento (F-PLN-02).",
)

scope_categories = Table(
    "scope_categories",
    metadata,
    *audit_columns(),
    Column(
        "group_id",
        Uuid,
        ForeignKey("scope_groups.id", ondelete="RESTRICT"),
        nullable=False,
        comment="O grupo da frente.",
    ),
    *_name_columns(),
    Column(
        "status",
        _enum(ScopeStatus, "scope_status", 20),
        nullable=False,
        comment="A decisão conjunta (F-PLN-03).",
    ),
    Column(
        "estimate_cents",
        BigInteger,
        comment="Estimativa inicial em centavos; nula é sem estimativa, nunca zero (F-PLN-05).",
    ),
    CheckConstraint("position >= 0", name="position_not_negative"),
    CheckConstraint("estimate_cents IS NULL OR estimate_cents > 0", name="estimate_positive"),
    CheckConstraint("origin = 'casal' OR deleted_at IS NULL", name="catalog_not_deleted"),
    Index(
        "uq_scope_categories_name_key_live",
        "name_key",
        unique=True,
        sqlite_where=_LIVE,
        postgresql_where=_LIVE,
    ),
    Index("ix_scope_categories_group_id", "group_id"),
    comment="Frentes do casamento e a decisão conjunta sobre cada uma (F-PLN-02 e F-PLN-03).",
)

scope_evaluations = Table(
    "scope_evaluations",
    metadata,
    *audit_columns(),
    Column(
        "category_id",
        Uuid,
        ForeignKey("scope_categories.id", ondelete="RESTRICT"),
        nullable=False,
        comment="A frente avaliada.",
    ),
    Column(
        "profile",
        _enum(ProfileKind, "profile_kind", 8),
        nullable=False,
        comment="Quem avalia; cada frente tem uma linha por perfil desde que nasce.",
    ),
    Column(
        "priority",
        _enum(Priority, "scope_priority", 12),
        comment="Quero muito, Se couber ou Dispenso; nula enquanto não avaliou.",
    ),
    Column("note", String(500), comment="O que esse perfil espera da frente."),
    UniqueConstraint("category_id", "profile"),
    CheckConstraint("profile != 'Ambos'", name="profile_is_login"),
    comment="Prioridade e nota de cada perfil por frente (F-PLN-04 e F-PLN-05).",
)

scope_status_changes = Table(
    "scope_status_changes",
    metadata,
    *audit_columns(),
    Column(
        "category_id",
        Uuid,
        ForeignKey("scope_categories.id", ondelete="RESTRICT"),
        nullable=False,
        comment="A frente que mudou.",
    ),
    Column("from_status", _enum(ScopeStatus, "scope_status_from", 20), nullable=False),
    Column("to_status", _enum(ScopeStatus, "scope_status_to", 20), nullable=False),
    Column("reason", String(300), comment="Por que ficou de fora; só para Fica de fora."),
    Column(
        "profile",
        _enum(ProfileKind, "profile_kind", 8),
        nullable=False,
        comment="Perfil de quem mudou, gravado para não depender do cadastro de usuários.",
    ),
    CheckConstraint("from_status != to_status", name="status_changed"),
    CheckConstraint(
        "to_status != 'Fica de fora' OR (reason IS NOT NULL AND length(trim(reason)) > 0)",
        name="discard_has_reason",
    ),
    CheckConstraint("profile != 'Ambos'", name="profile_is_login"),
    Index("ix_scope_status_changes_category_id", "category_id", "created_at"),
    comment="Histórico de status das frentes (F-PLN-03): só se acrescenta.",
)
