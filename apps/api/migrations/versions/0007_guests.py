"""guests

Revision ID: 0007
Revises: 0006
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SIDES = "'Noivo', 'Noiva', 'Comum'"
BANDS = "'Adulto', 'Criança pagante', 'Criança isenta'"
PROBABILITIES = "'Certeza', 'Provável', 'Fase 2'"
STATUSES = "'Rascunho', 'Convidado', 'Confirmado', 'Não irá'"
PROFILES = "'Noivo', 'Noiva', 'Ambos'"


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
    live = sa.text("deleted_at IS NULL")
    live_companion = sa.text("deleted_at IS NULL AND companion_of_id IS NOT NULL")

    op.create_table(
        "guest_households",
        *_audit_columns(),
        sa.Column(
            "name", sa.String(80), nullable=False, comment="Como o casal chama o núcleo; exibido."
        ),
        sa.Column(
            "name_key",
            sa.String(240),
            nullable=False,
            comment="Nome sem caixa nem espaços repetidos: a chave de unicidade entre os vivos.",
        ),
        sa.Column(
            "side",
            sa.String(8),
            nullable=False,
            comment="Noivo, Noiva ou Comum; as pessoas herdam o lado do núcleo.",
        ),
        sa.Column(
            "street", sa.String(120), comment="Logradouro do endereço postal (convite impresso)."
        ),
        sa.Column("number", sa.String(20), comment="Número do endereço."),
        sa.Column("complement", sa.String(60), comment="Complemento do endereço."),
        sa.Column("district", sa.String(60), comment="Bairro."),
        sa.Column("city", sa.String(60), comment="Cidade."),
        sa.Column("state", sa.String(2), comment="UF, duas letras."),
        sa.Column("postal_code", sa.String(8), comment="CEP, oito dígitos, sem hífen."),
        sa.Column("note", sa.String(500), comment="Observação livre do casal."),
        sa.Column(
            "members_revision",
            sa.Integer(),
            nullable=False,
            comment="Sobe quando uma pessoa sai do núcleo: duas saídas simultâneas se conflitam.",
        ),
        sa.CheckConstraint(f"side IN ({SIDES})", name=op.f("ck_guest_households_guest_side")),
        sa.CheckConstraint(
            "state IS NULL OR length(state) = 2",
            name=op.f("ck_guest_households_state_has_two_letters"),
        ),
        sa.CheckConstraint(
            "postal_code IS NULL OR length(postal_code) = 8",
            name=op.f("ck_guest_households_postal_code_has_eight_digits"),
        ),
        sa.CheckConstraint(
            "members_revision >= 0", name=op.f("ck_guest_households_members_revision_not_negative")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_guest_households")),
        comment="Núcleos familiares da lista de convidados (F-CNV-01). Dado pessoal de terceiros.",
    )
    op.create_index(
        "uq_guest_households_name_key_live",
        "guest_households",
        ["name_key"],
        unique=True,
        sqlite_where=live,
        postgresql_where=live,
    )

    op.create_table(
        "guests",
        *_audit_columns(),
        sa.Column("household_id", sa.Uuid(), nullable=False, comment="O núcleo da pessoa."),
        sa.Column("position", sa.Integer(), nullable=False, comment="Ordem de cadastro no núcleo."),
        sa.Column(
            "companion_of_id",
            sa.Uuid(),
            comment="O titular, quando a pessoa é o acompanhante (+1); nulo nas demais.",
        ),
        sa.Column(
            "name", sa.String(80), comment="Nome; nulo só no acompanhante a confirmar (F-CNV-02)."
        ),
        sa.Column("band", sa.String(15), nullable=False, comment="Faixa de custo."),
        sa.Column(
            "age",
            sa.Integer(),
            comment="Idade da criança em anos; só vale para criança (F-CNV-03).",
        ),
        sa.Column(
            "probability",
            sa.String(8),
            nullable=False,
            comment="Certeza, Provável ou Fase 2: define o peso no Estimado Ponderado.",
        ),
        sa.Column(
            "status",
            sa.String(10),
            nullable=False,
            comment="Rascunho, Convidado, Confirmado ou Não irá (F-CNV-04).",
        ),
        sa.Column(
            "decline_reason", sa.String(300), comment="Por que não irá; só com o status Não irá."
        ),
        sa.Column(
            "dietary_restriction",
            sa.String(120),
            comment="Restrição alimentar; pode revelar saúde, tratar como dado sensível.",
        ),
        sa.Column("note", sa.String(500), comment="Observação livre do casal."),
        sa.Column(
            "phone", sa.String(11), comment="Telefone brasileiro, só os dígitos (DDD e número)."
        ),
        sa.Column("email", sa.String(254), comment="E-mail, validado só no formato."),
        sa.CheckConstraint(f"band IN ({BANDS})", name=op.f("ck_guests_guest_age_band")),
        sa.CheckConstraint(
            f"probability IN ({PROBABILITIES})", name=op.f("ck_guests_guest_probability")
        ),
        sa.CheckConstraint(f"status IN ({STATUSES})", name=op.f("ck_guests_guest_status")),
        sa.CheckConstraint("position >= 0", name=op.f("ck_guests_position_not_negative")),
        sa.CheckConstraint(
            "name IS NOT NULL OR companion_of_id IS NOT NULL",
            name=op.f("ck_guests_name_required_unless_companion"),
        ),
        sa.CheckConstraint(
            "companion_of_id IS NULL OR companion_of_id <> id",
            name=op.f("ck_guests_companion_not_self"),
        ),
        sa.CheckConstraint(
            "age IS NULL OR (band <> 'Adulto' AND age BETWEEN 0 AND 17)",
            name=op.f("ck_guests_age_only_for_children"),
        ),
        sa.CheckConstraint(
            "decline_reason IS NULL OR status = 'Não irá'",
            name=op.f("ck_guests_reason_only_when_declined"),
        ),
        sa.CheckConstraint(
            "phone IS NULL OR length(phone) IN (10, 11)",
            name=op.f("ck_guests_phone_has_ddd_and_number"),
        ),
        sa.ForeignKeyConstraint(
            ["household_id"],
            ["guest_households.id"],
            name=op.f("fk_guests_household_id_guest_households"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["companion_of_id"],
            ["guests.id"],
            name=op.f("fk_guests_companion_of_id_guests"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_guests")),
        comment="Pessoas da lista de convidados (F-CNV-01). Dado pessoal de terceiros.",
    )
    op.create_index(
        "uq_guests_companion_of_id_live",
        "guests",
        ["companion_of_id"],
        unique=True,
        sqlite_where=live_companion,
        postgresql_where=live_companion,
    )
    op.create_index("ix_guests_household_id", "guests", ["household_id"])

    op.create_table(
        "guest_status_changes",
        *_audit_columns(),
        sa.Column("guest_id", sa.Uuid(), nullable=False, comment="A pessoa que mudou de status."),
        sa.Column("from_status", sa.String(10), nullable=False),
        sa.Column("to_status", sa.String(10), nullable=False),
        sa.Column("reason", sa.String(300), comment="Por que não irá; só para Não irá."),
        sa.Column(
            "profile",
            sa.String(8),
            nullable=False,
            comment="Perfil de quem mudou, gravado para não depender do cadastro de usuários.",
        ),
        sa.CheckConstraint(
            f"from_status IN ({STATUSES})", name=op.f("ck_guest_status_changes_guest_status_from")
        ),
        sa.CheckConstraint(
            f"to_status IN ({STATUSES})", name=op.f("ck_guest_status_changes_guest_status_to")
        ),
        sa.CheckConstraint(
            f"profile IN ({PROFILES})", name=op.f("ck_guest_status_changes_profile_kind")
        ),
        sa.CheckConstraint(
            "from_status <> to_status", name=op.f("ck_guest_status_changes_status_changed")
        ),
        sa.CheckConstraint(
            "reason IS NULL OR to_status = 'Não irá'",
            name=op.f("ck_guest_status_changes_reason_only_when_declined"),
        ),
        sa.CheckConstraint(
            "profile != 'Ambos'", name=op.f("ck_guest_status_changes_profile_is_login")
        ),
        sa.ForeignKeyConstraint(
            ["guest_id"],
            ["guests.id"],
            name=op.f("fk_guest_status_changes_guest_id_guests"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_guest_status_changes")),
        comment="Histórico de status das pessoas (F-CNV-04): só se acrescenta.",
    )
    op.create_index(
        "ix_guest_status_changes_guest_id", "guest_status_changes", ["guest_id", "created_at"]
    )


def downgrade() -> None:
    op.drop_index("ix_guest_status_changes_guest_id", table_name="guest_status_changes")
    op.drop_table("guest_status_changes")
    op.drop_index("ix_guests_household_id", table_name="guests")
    op.drop_index("uq_guests_companion_of_id_live", table_name="guests")
    op.drop_table("guests")
    op.drop_index("uq_guest_households_name_key_live", table_name="guest_households")
    op.drop_table("guest_households")
