from sqlalchemy import CheckConstraint, Column, Enum, ForeignKey, Index, String, Table, Uuid, text

from wedding.platform.db.audit import audit_columns
from wedding.platform.db.metadata import metadata
from wedding.platform.db.types import UtcDateTime
from wedding.shared_kernel.profile import ProfileKind

_LIVE = text("deleted_at IS NULL")

users = Table(
    "users",
    metadata,
    *audit_columns(),
    Column("username", String(32), nullable=False, comment="Usuário de login, em minúsculas."),
    Column(
        "profile",
        Enum(
            ProfileKind,
            name="profile",
            native_enum=False,
            create_constraint=True,
            length=8,
            values_callable=lambda kind: [member.value for member in kind],
        ),
        nullable=False,
        comment="Noivo ou Noiva; Ambos não é um perfil de login.",
    ),
    Column("password_hash", String, nullable=False, comment="Hash Argon2 da senha."),
    CheckConstraint("profile != 'Ambos'", name="profile_is_login"),
    Index(
        "uq_users_username_live",
        "username",
        unique=True,
        sqlite_where=_LIVE,
        postgresql_where=_LIVE,
    ),
    Index(
        "uq_users_profile_live", "profile", unique=True, sqlite_where=_LIVE, postgresql_where=_LIVE
    ),
    comment="Os dois logins do casal, criados só pela CLI.",
)

user_sessions = Table(
    "user_sessions",
    metadata,
    Column("id", Uuid, primary_key=True),
    Column("user_id", Uuid, ForeignKey("users.id"), nullable=False, index=True),
    Column("token_hash", String(64), nullable=False, unique=True, comment="SHA-256 do token."),
    Column("created_at", UtcDateTime, nullable=False),
    Column("last_seen_at", UtcDateTime, nullable=False),
    comment="Sessões abertas; o logout apaga a linha.",
)
