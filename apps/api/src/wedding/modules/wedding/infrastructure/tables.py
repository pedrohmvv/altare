from sqlalchemy import JSON, CheckConstraint, Column, Enum, Index, String, Table, UniqueConstraint

from wedding.modules.wedding.domain.value_objects import BaselineKey, DefinitionStatus
from wedding.platform.db.audit import audit_columns
from wedding.platform.db.metadata import metadata
from wedding.shared_kernel.profile import ProfileKind


def _values(kind: type) -> list[str]:
    return [member.value for member in kind]  # type: ignore[attr-defined]


def _baseline_key() -> Enum:
    return Enum(
        BaselineKey,
        name="baseline_key",
        native_enum=False,
        create_constraint=True,
        length=10,
        values_callable=_values,
    )


baseline_fields = Table(
    "baseline_fields",
    metadata,
    *audit_columns(),
    Column("field_key", _baseline_key(), nullable=False, comment="Qual variável do casamento."),
    Column(
        "status",
        Enum(
            DefinitionStatus,
            name="definition_status",
            native_enum=False,
            create_constraint=True,
            length=16,
            values_callable=_values,
        ),
        nullable=False,
        comment="Em definição ou Definido.",
    ),
    Column(
        "value",
        JSON(none_as_null=True),
        comment="O valor, validado pelo domínio; nulo enquanto o campo está vazio.",
    ),
    Column("note", String(500), comment="Por que estamos em dúvida; texto livre."),
    UniqueConstraint("field_key"),
    CheckConstraint("status != 'Definido' OR value IS NOT NULL", name="defined_has_value"),
    comment=(
        "Definições Base do casamento (F-PLN-01): uma linha por variável, criadas pela migration."
    ),
)

baseline_changes = Table(
    "baseline_changes",
    metadata,
    *audit_columns(),
    Column("field_key", _baseline_key(), nullable=False, comment="Qual variável mudou."),
    Column("state_before", JSON, nullable=False, comment="Status, valor e nota antes da mudança."),
    Column("state_after", JSON, nullable=False, comment="Status, valor e nota depois da mudança."),
    Column(
        "profile",
        Enum(
            ProfileKind,
            name="profile_kind",
            native_enum=False,
            create_constraint=True,
            length=8,
            values_callable=_values,
        ),
        nullable=False,
        comment="Perfil de quem mudou, para o histórico não depender do cadastro de usuários.",
    ),
    CheckConstraint("profile != 'Ambos'", name="profile_is_login"),
    Index("ix_baseline_changes_created_at", "created_at"),
    comment="Histórico das Definições Base (F-PLN-01, regra 3): só se acrescenta.",
)
