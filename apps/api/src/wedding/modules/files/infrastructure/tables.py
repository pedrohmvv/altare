from sqlalchemy import BigInteger, CheckConstraint, Column, Enum, Index, String, Table

from wedding.modules.files.domain.value_objects import FileKind
from wedding.platform.db.audit import audit_columns
from wedding.platform.db.metadata import metadata

file_assets = Table(
    "file_assets",
    metadata,
    *audit_columns(),
    Column(
        "original_name", String(120), nullable=False, comment="Nome que a pessoa deu; só exibição."
    ),
    Column(
        "content_type",
        Enum(
            FileKind,
            name="file_kind",
            native_enum=False,
            create_constraint=True,
            length=20,
            values_callable=lambda kind: [member.value for member in kind],
        ),
        nullable=False,
        comment="Tipo pela assinatura real do arquivo.",
    ),
    Column("size_bytes", BigInteger, nullable=False, comment="Tamanho do conteúdo em bytes."),
    Column(
        "sha256", String(64), nullable=False, comment="SHA-256 do conteúdo; a chave no storage."
    ),
    CheckConstraint("size_bytes > 0", name="size_positive"),
    Index("ix_file_assets_sha256", "sha256"),
    comment="Um registro por envio; o mesmo conteúdo, de mesmo hash, fica uma vez no storage.",
)
