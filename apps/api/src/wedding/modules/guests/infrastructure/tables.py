from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Uuid,
    text,
)

from wedding.modules.guests.domain.values import (
    AgeBand,
    GuestStatus,
    InviteChannel,
    Probability,
    Side,
)
from wedding.platform.db.audit import audit_columns
from wedding.platform.db.metadata import metadata
from wedding.shared_kernel.profile import ProfileKind

_LIVE = text("deleted_at IS NULL")
_LIVE_COMPANION = text("deleted_at IS NULL AND companion_of_id IS NOT NULL")


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


guest_households = Table(
    "guest_households",
    metadata,
    *audit_columns(),
    Column("name", String(80), nullable=False, comment="Como o casal chama o núcleo; exibido."),
    Column(
        "name_key",
        String(240),
        nullable=False,
        comment="Nome sem caixa nem espaços repetidos: a chave de unicidade entre os vivos.",
    ),
    Column(
        "side",
        _enum(Side, "guest_side", 8),
        nullable=False,
        comment="Noivo, Noiva ou Comum; as pessoas herdam o lado do núcleo.",
    ),
    Column("street", String(120), comment="Logradouro do endereço postal (convite impresso)."),
    Column("number", String(20), comment="Número do endereço."),
    Column("complement", String(60), comment="Complemento do endereço."),
    Column("district", String(60), comment="Bairro."),
    Column("city", String(60), comment="Cidade."),
    Column("state", String(2), comment="UF, duas letras."),
    Column("postal_code", String(8), comment="CEP, oito dígitos, sem hífen."),
    Column("note", String(500), comment="Observação livre do casal."),
    Column(
        "members_revision",
        Integer,
        nullable=False,
        comment="Sobe quando uma pessoa sai do núcleo: duas saídas simultâneas se conflitam.",
    ),
    Column("invite_sent_on", Date, comment="Quando o convite do núcleo foi enviado (F-CNV-05)."),
    Column(
        "invite_channel",
        _enum(InviteChannel, "guest_invite_channel", 12),
        comment="Canal do envio; anda junto com a data.",
    ),
    CheckConstraint("state IS NULL OR length(state) = 2", name="state_has_two_letters"),
    CheckConstraint(
        "(invite_sent_on IS NULL) = (invite_channel IS NULL)",
        name="invite_date_and_channel_together",
    ),
    CheckConstraint(
        "postal_code IS NULL OR length(postal_code) = 8", name="postal_code_has_eight_digits"
    ),
    CheckConstraint("members_revision >= 0", name="members_revision_not_negative"),
    Index(
        "uq_guest_households_name_key_live",
        "name_key",
        unique=True,
        sqlite_where=_LIVE,
        postgresql_where=_LIVE,
    ),
    comment="Núcleos familiares da lista de convidados (F-CNV-01). Dado pessoal de terceiros.",
)

guests = Table(
    "guests",
    metadata,
    *audit_columns(),
    Column(
        "household_id",
        Uuid,
        ForeignKey("guest_households.id", ondelete="RESTRICT"),
        nullable=False,
        comment="O núcleo da pessoa.",
    ),
    Column("position", Integer, nullable=False, comment="Ordem de cadastro no núcleo."),
    Column(
        "companion_of_id",
        Uuid,
        ForeignKey("guests.id", ondelete="RESTRICT"),
        comment="O titular, quando a pessoa é o acompanhante (+1); nulo nas demais.",
    ),
    Column("name", String(80), comment="Nome; nulo só no acompanhante a confirmar (F-CNV-02)."),
    Column("band", _enum(AgeBand, "guest_age_band", 15), nullable=False, comment="Faixa de custo."),
    Column("age", Integer, comment="Idade da criança em anos; só vale para criança (F-CNV-03)."),
    Column(
        "probability",
        _enum(Probability, "guest_probability", 8),
        nullable=False,
        comment="Certeza, Provável ou Fase 2: define o peso no Estimado Ponderado.",
    ),
    Column(
        "status",
        _enum(GuestStatus, "guest_status", 10),
        nullable=False,
        comment="Rascunho, Convidado, Confirmado ou Não irá (F-CNV-04).",
    ),
    Column("decline_reason", String(300), comment="Por que não irá; só com o status Não irá."),
    Column(
        "dietary_restriction",
        String(120),
        comment="Restrição alimentar; pode revelar saúde, tratar como dado sensível.",
    ),
    Column("note", String(500), comment="Observação livre do casal."),
    Column("phone", String(11), comment="Telefone brasileiro, só os dígitos (DDD e número)."),
    Column("email", String(254), comment="E-mail, validado só no formato."),
    CheckConstraint("position >= 0", name="position_not_negative"),
    CheckConstraint(
        "name IS NOT NULL OR companion_of_id IS NOT NULL", name="name_required_unless_companion"
    ),
    CheckConstraint("companion_of_id IS NULL OR companion_of_id <> id", name="companion_not_self"),
    CheckConstraint(
        "age IS NULL OR (band <> 'Adulto' AND age BETWEEN 0 AND 17)", name="age_only_for_children"
    ),
    CheckConstraint(
        "decline_reason IS NULL OR status = 'Não irá'", name="reason_only_when_declined"
    ),
    CheckConstraint("phone IS NULL OR length(phone) IN (10, 11)", name="phone_has_ddd_and_number"),
    Index(
        "uq_guests_companion_of_id_live",
        "companion_of_id",
        unique=True,
        sqlite_where=_LIVE_COMPANION,
        postgresql_where=_LIVE_COMPANION,
    ),
    Index("ix_guests_household_id", "household_id"),
    comment="Pessoas da lista de convidados (F-CNV-01). Dado pessoal de terceiros.",
)

guest_status_changes = Table(
    "guest_status_changes",
    metadata,
    *audit_columns(),
    Column(
        "guest_id",
        Uuid,
        ForeignKey("guests.id", ondelete="RESTRICT"),
        nullable=False,
        comment="A pessoa que mudou de status.",
    ),
    Column("from_status", _enum(GuestStatus, "guest_status_from", 10), nullable=False),
    Column("to_status", _enum(GuestStatus, "guest_status_to", 10), nullable=False),
    Column("reason", String(300), comment="Por que não irá; só para Não irá."),
    Column(
        "profile",
        _enum(ProfileKind, "profile_kind", 8),
        nullable=False,
        comment="Perfil de quem mudou, gravado para não depender do cadastro de usuários.",
    ),
    CheckConstraint("from_status <> to_status", name="status_changed"),
    CheckConstraint("reason IS NULL OR to_status = 'Não irá'", name="reason_only_when_declined"),
    CheckConstraint("profile != 'Ambos'", name="profile_is_login"),
    Index("ix_guest_status_changes_guest_id", "guest_id", "created_at"),
    comment="Histórico de status das pessoas (F-CNV-04): só se acrescenta.",
)

guest_settings = Table(
    "guest_settings",
    metadata,
    *audit_columns(),
    Column(
        "weight_certain_pct",
        Integer,
        comment="Peso de Certeza no Estimado Ponderado, de 0 a 100; nulo até o casal definir.",
    ),
    Column(
        "weight_probable_pct", Integer, comment="Peso de Provável, de 0 a 100; nulo até definir."
    ),
    Column("weight_phase_2_pct", Integer, comment="Peso de Fase 2, de 0 a 100; nulo até definir."),
    Column("exempt_until_age", Integer, comment="Criança isenta até esta idade; nulo até definir."),
    Column(
        "paying_until_age", Integer, comment="Criança pagante até esta idade; nulo até definir."
    ),
    CheckConstraint(
        "(weight_certain_pct IS NULL) = (weight_probable_pct IS NULL) "
        "AND (weight_probable_pct IS NULL) = (weight_phase_2_pct IS NULL)",
        name="weights_all_or_none",
    ),
    CheckConstraint(
        "(weight_certain_pct IS NULL OR weight_certain_pct BETWEEN 0 AND 100) "
        "AND (weight_probable_pct IS NULL OR weight_probable_pct BETWEEN 0 AND 100) "
        "AND (weight_phase_2_pct IS NULL OR weight_phase_2_pct BETWEEN 0 AND 100)",
        name="weights_between_0_and_100",
    ),
    CheckConstraint(
        "(exempt_until_age IS NULL OR exempt_until_age BETWEEN 0 AND 17) "
        "AND (paying_until_age IS NULL OR paying_until_age BETWEEN 0 AND 17)",
        name="ages_between_0_and_17",
    ),
    CheckConstraint(
        "exempt_until_age IS NULL OR paying_until_age IS NULL "
        "OR exempt_until_age <= paying_until_age",
        name="exempt_not_above_paying",
    ),
    comment="Pesos e limites de idade da lista (F-CNV-03 e F-CNV-06): uma linha.",
)
