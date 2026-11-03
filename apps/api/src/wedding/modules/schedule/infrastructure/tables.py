from sqlalchemy import (
    Boolean,
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

from wedding.modules.schedule.domain.values import ManualState
from wedding.platform.db.audit import audit_columns
from wedding.platform.db.metadata import metadata
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


schedule_phases = Table(
    "schedule_phases",
    metadata,
    *audit_columns(),
    Column("title", String(60), nullable=False, comment="Como o casal chama a fase; exibido."),
    Column("position", Integer, nullable=False, comment="Ordem de exibição, a partir de zero."),
    CheckConstraint("position >= 0", name="position_not_negative"),
    comment="Fases do cronograma (F-CRN-01); as cinco do catálogo vêm da migration.",
)

milestones = Table(
    "milestones",
    metadata,
    *audit_columns(),
    Column(
        "phase_id",
        Uuid,
        ForeignKey("schedule_phases.id", ondelete="RESTRICT"),
        nullable=False,
        comment="A fase do marco.",
    ),
    Column("position", Integer, nullable=False, comment="Ordem dentro da fase, a partir de zero."),
    Column("title", String(120), nullable=False, comment="O nome do marco; exibido."),
    Column(
        "responsible",
        _enum(ProfileKind, "milestone_responsible", 8),
        nullable=False,
        comment="Noivo, Noiva ou Ambos; Ambos no catálogo inicial (F-CRN-02).",
    ),
    Column(
        "category_id",
        Uuid,
        ForeignKey("scope_categories.id", ondelete="RESTRICT"),
        comment="A categoria do Mapa de Escopo, ligada pelo id e nunca pelo nome; nulo se não tem.",
    ),
    Column("note", String(500), comment="Nota livre."),
    Column(
        "target_date",
        Date,
        comment="Prazo-alvo digitado à mão (F-CRN-05); nulo se não há. Atrasado se deriva dele.",
    ),
    Column(
        "manual_state",
        _enum(ManualState, "manual_state", 12),
        comment=(
            "O que o casal marcou: Em andamento ou Concluído; nulo é o estado derivado "
            "(Bloqueado ou Destravado, que nunca se grava)."
        ),
    ),
    Column(
        "window_start_before",
        Integer,
        comment=(
            "Janela sugerida (F-CRN-02): início, quantas unidades antes da data; nulo sem janela."
        ),
    ),
    Column(
        "window_end_before",
        Integer,
        comment="Janela sugerida: fim, quantas unidades antes da data; nulo sem janela.",
    ),
    Column("window_unit", String(8), comment="meses ou semanas; nulo sem janela."),
    CheckConstraint("position >= 0", name="position_not_negative"),
    CheckConstraint("window_unit IN ('meses', 'semanas')", name="window_unit_known"),
    CheckConstraint(
        "(window_start_before IS NULL) = (window_end_before IS NULL) "
        "AND (window_end_before IS NULL) = (window_unit IS NULL)",
        name="window_all_or_none",
    ),
    CheckConstraint(
        "window_start_before IS NULL OR "
        "(window_end_before >= 0 AND window_start_before >= window_end_before)",
        name="window_starts_before_it_ends",
    ),
    Index("ix_milestones_phase_id", "phase_id", "position"),
    comment=(
        "Marcos do cronograma (F-CRN-01). Guarda só fatos: Bloqueado, Destravado, Atrasado, "
        "Opcional e Arquivado se derivam na leitura."
    ),
)

milestone_dependencies = Table(
    "milestone_dependencies",
    metadata,
    *audit_columns(),
    Column(
        "milestone_id",
        Uuid,
        ForeignKey("milestones.id", ondelete="RESTRICT"),
        nullable=False,
        comment="O marco que espera.",
    ),
    Column(
        "depends_on_id",
        Uuid,
        ForeignKey("milestones.id", ondelete="RESTRICT"),
        nullable=False,
        comment="O marco de que ele depende.",
    ),
    CheckConstraint("milestone_id <> depends_on_id", name="not_self"),
    Index(
        "uq_milestone_dependencies_pair_live",
        "milestone_id",
        "depends_on_id",
        unique=True,
        sqlite_where=_LIVE,
        postgresql_where=_LIVE,
    ),
    comment="Dependências entre marcos (F-CRN-03): A depende de B. Sai com exclusão lógica.",
)

milestone_changes = Table(
    "milestone_changes",
    metadata,
    *audit_columns(),
    Column(
        "milestone_id",
        Uuid,
        ForeignKey("milestones.id", ondelete="RESTRICT"),
        nullable=False,
        comment="O marco que mudou de estado.",
    ),
    Column(
        "state_before",
        _enum(ManualState, "milestone_state_before", 12),
        comment="O estado marcado antes; nulo era o derivado.",
    ),
    Column(
        "state_after",
        _enum(ManualState, "milestone_state_after", 12),
        comment="O estado marcado depois; nulo é reabrir, voltar ao derivado.",
    ),
    Column(
        "ignored_block",
        Boolean,
        nullable=False,
        comment="Verdadeiro se o marco estava Bloqueado e o casal confirmou ignorar o bloqueio.",
    ),
    Column(
        "profile",
        _enum(ProfileKind, "profile_kind", 8),
        nullable=False,
        comment="Perfil de quem mudou, gravado para não depender do cadastro de usuários.",
    ),
    CheckConstraint(
        "COALESCE(state_before, '') <> COALESCE(state_after, '')", name="state_changed"
    ),
    CheckConstraint(
        "NOT ignored_block OR state_after IS NOT NULL", name="ignored_block_needs_state"
    ),
    CheckConstraint("profile != 'Ambos'", name="profile_is_login"),
    Index("ix_milestone_changes_milestone_id", "milestone_id", "created_at"),
    comment="Histórico de estado dos marcos (F-CRN-03, regra 4): só se acrescenta.",
)
