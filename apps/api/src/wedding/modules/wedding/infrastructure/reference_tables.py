from sqlalchemy import CheckConstraint, Column, Enum, ForeignKey, Index, String, Table, Uuid

from wedding.modules.wedding.domain.reference import ReferenceKind
from wedding.platform.db.audit import audit_columns
from wedding.platform.db.metadata import metadata
from wedding.shared_kernel.profile import ProfileKind

scope_references = Table(
    "scope_references",
    metadata,
    *audit_columns(),
    Column(
        "category_id",
        Uuid,
        ForeignKey("scope_categories.id", ondelete="RESTRICT"),
        nullable=False,
        comment="A frente em que a inspiração foi guardada.",
    ),
    Column(
        "kind",
        Enum(
            ReferenceKind,
            name="reference_kind",
            native_enum=False,
            create_constraint=True,
            length=8,
            values_callable=lambda kind: [member.value for member in kind],
        ),
        nullable=False,
        comment="link ou imagem.",
    ),
    Column(
        "profile",
        Enum(
            ProfileKind,
            name="profile_kind",
            native_enum=False,
            create_constraint=True,
            length=8,
            values_callable=lambda kind: [member.value for member in kind],
        ),
        nullable=False,
        comment="Quem adicionou; só esse perfil remove (F-PLN-06).",
    ),
    Column("url", String(2000), comment="O endereço, já validado; nulo para imagem."),
    Column(
        "file_id",
        Uuid,
        ForeignKey("file_assets.id", ondelete="RESTRICT"),
        comment="O arquivo da imagem, enviado pelo módulo de arquivos; nulo para link.",
    ),
    Column("title", String(120), comment="Texto curto, opcional."),
    Column("comment", String(500), comment="Texto livre, opcional."),
    CheckConstraint(
        "(kind = 'link' AND url IS NOT NULL AND file_id IS NULL) "
        "OR (kind = 'imagem' AND file_id IS NOT NULL AND url IS NULL)",
        name="kind_matches_content",
    ),
    CheckConstraint("profile != 'Ambos'", name="profile_is_login"),
    Index("ix_scope_references_category_id", "category_id", "created_at"),
    comment="Referências de inspiração por frente, link ou imagem (F-PLN-06).",
)
