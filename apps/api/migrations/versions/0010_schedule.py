"""schedule

Revision ID: 0010
Revises: 0009
"""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

import sqlalchemy as sa
from alembic import op

revision: str = "0010"
down_revision: str | None = "0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# A semente (F-CRN-02): 5 fases e 29 marcos com as dependências do catálogo. Os ids são fixos
# (uuid5) para a migration dar o mesmo resultado em qualquer banco. A categoria liga pelo id fixo
# da frente no Mapa de Escopo (0005), nunca pelo nome; o C11 usa o nome da semente do Mapa, que é
# "Música (DJ, banda)". Responsável `Ambos` em todos, nenhum prazo, nenhum estado marcado. A janela
# sugerida fica guardada em deslocamentos (início antes, fim antes, unidade) para o cálculo de
# datas, que é de outro PR, não exigir refazer a semente.
SEED_NAMESPACE = uuid.UUID("5c0e7a6e-2b0d-5f61-9a39-6c1d7e0f5a01")
PHASES = [
    "Marco Zero",
    "Contrato Âncora",
    "Fornecedores Essenciais",
    "Identidade, Complementares e Convidados",
    "Reta Final",
]
# (código, fase a partir de 1, título, categoria, depende de, janela: início, fim, unidade)
MILESTONES = [
    ("C01", 1, "Classificar o Mapa de Escopo", None, (), None),
    ("C02", 1, "Montar a lista preliminar de convidados", None, (), None),
    ("C03", 1, "Definir o teto macro e simular orçamentos", None, ("C01", "C02"), None),
    ("C04", 1, "Escolher o caminho macro (formato e região)", None, ("C03",), None),
    ("C05", 2, "Definir a data (ou janela de datas)", None, ("C04",), None),
    ("C06", 2, "Fechar o Espaço", "Espaço", ("C05",), (14, 10, "meses")),
    ("C07", 3, "Fechar o Buffet", "Buffet", ("C06",), (12, 8, "meses")),
    ("C08", 3, "Fechar a Fotografia", "Fotografia", ("C06",), (12, 8, "meses")),
    ("C09", 3, "Fechar o Vídeo", "Vídeo", ("C06",), (12, 8, "meses")),
    ("C10", 3, "Fechar o Cerimonial do dia", "Cerimonial do dia", ("C06",), (10, 7, "meses")),
    ("C11", 3, "Fechar a Música", "Música (DJ, banda)", ("C06",), (10, 6, "meses")),
    ("C12", 3, "Organizar a cerimônia civil", "Cerimônia civil", ("C05",), (6, 3, "meses")),
    (
        "C13",
        3,
        "Organizar a cerimônia religiosa ou simbólica",
        "Cerimônia religiosa ou simbólica",
        ("C05",),
        (12, 6, "meses"),
    ),
    ("C14", 4, "Fechar Decoração e flores", "Decoração e flores", ("C06",), (9, 5, "meses")),
    ("C15", 4, "Fechar Iluminação e som", "Iluminação e som", ("C06",), (8, 5, "meses")),
    ("C16", 4, "Fechar Bebidas e bar", "Bebidas e bar", ("C07",), (8, 5, "meses")),
    ("C17", 4, "Fechar Bolo e doces", "Bolo e doces", ("C07",), (6, 3, "meses")),
    ("C18", 4, "Definir os trajes", "Trajes", ("C05",), (10, 5, "meses")),
    ("C19", 4, "Contratar a beleza", "Beleza (noivos)", ("C18",), (6, 3, "meses")),
    (
        "C20",
        4,
        "Convites e papelaria",
        "Convites e papelaria",
        ("C02", "C06"),
        (7, 4, "meses"),
    ),
    ("C21", 4, "Lembrancinhas", "Lembrancinhas", ("C06",), (5, 3, "meses")),
    ("C22", 4, "Montar o enxoval e a lista de presentes", None, ("C05",), (6, 3, "meses")),
    ("C23", 4, "Planejar a lua de mel", "Lua de mel", ("C05",), (8, 3, "meses")),
    ("C24", 4, "Reservar a noite de núpcias", "Noite de núpcias", ("C06",), (4, 2, "meses")),
    ("C25", 5, "Enviar os convites", None, ("C20",), (4, 2, "meses")),
    ("C26", 5, "Confirmar as presenças", None, ("C25",), (2, 1, "meses")),
    ("C27", 5, "Degustações e provas finais", None, ("C07", "C18"), (2, 1, "meses")),
    ("C28", 5, "Quitar os contratos", None, ("C26",), (4, 1, "semanas")),
    ("C29", 5, "Entregar o Dossiê ao cerimonialista", None, ("C10", "C26"), (4, 2, "semanas")),
]
STATES = "'Em andamento', 'Concluído'"
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


def _seed_id(key: str) -> uuid.UUID:
    return uuid.uuid5(SEED_NAMESPACE, key)


def upgrade() -> None:
    live = sa.text("deleted_at IS NULL")
    phases = op.create_table(
        "schedule_phases",
        *_audit_columns(),
        sa.Column(
            "title", sa.String(60), nullable=False, comment="Como o casal chama a fase; exibido."
        ),
        sa.Column(
            "position", sa.Integer(), nullable=False, comment="Ordem de exibição, a partir de zero."
        ),
        sa.CheckConstraint("position >= 0", name=op.f("ck_schedule_phases_position_not_negative")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_schedule_phases")),
        comment="Fases do cronograma (F-CRN-01); as cinco do catálogo vêm da migration.",
    )
    milestones = op.create_table(
        "milestones",
        *_audit_columns(),
        sa.Column("phase_id", sa.Uuid(), nullable=False, comment="A fase do marco."),
        sa.Column(
            "position",
            sa.Integer(),
            nullable=False,
            comment="Ordem dentro da fase, a partir de zero.",
        ),
        sa.Column("title", sa.String(120), nullable=False, comment="O nome do marco; exibido."),
        sa.Column(
            "responsible",
            sa.String(8),
            nullable=False,
            comment="Noivo, Noiva ou Ambos; Ambos no catálogo inicial (F-CRN-02).",
        ),
        sa.Column(
            "category_id",
            sa.Uuid(),
            comment=(
                "A categoria do Mapa de Escopo, ligada pelo id e nunca pelo nome; nulo se não tem."
            ),
        ),
        sa.Column("note", sa.String(500), comment="Nota livre."),
        sa.Column(
            "target_date",
            sa.Date(),
            comment=(
                "Prazo-alvo digitado à mão (F-CRN-05); nulo se não há. Atrasado se deriva dele."
            ),
        ),
        sa.Column(
            "manual_state",
            sa.String(12),
            comment=(
                "O que o casal marcou: Em andamento ou Concluído; nulo é o estado derivado "
                "(Bloqueado ou Destravado, que nunca se grava)."
            ),
        ),
        sa.Column(
            "window_start_before",
            sa.Integer(),
            comment=(
                "Janela sugerida (F-CRN-02): início, quantas unidades antes da data; "
                "nulo sem janela."
            ),
        ),
        sa.Column(
            "window_end_before",
            sa.Integer(),
            comment="Janela sugerida: fim, quantas unidades antes da data; nulo sem janela.",
        ),
        sa.Column("window_unit", sa.String(8), comment="meses ou semanas; nulo sem janela."),
        sa.CheckConstraint(
            f"responsible IN ({PROFILES})", name=op.f("ck_milestones_milestone_responsible")
        ),
        sa.CheckConstraint(f"manual_state IN ({STATES})", name=op.f("ck_milestones_manual_state")),
        sa.CheckConstraint("position >= 0", name=op.f("ck_milestones_position_not_negative")),
        sa.CheckConstraint(
            "window_unit IN ('meses', 'semanas')", name=op.f("ck_milestones_window_unit_known")
        ),
        sa.CheckConstraint(
            "(window_start_before IS NULL) = (window_end_before IS NULL) "
            "AND (window_end_before IS NULL) = (window_unit IS NULL)",
            name=op.f("ck_milestones_window_all_or_none"),
        ),
        sa.CheckConstraint(
            "window_start_before IS NULL OR "
            "(window_end_before >= 0 AND window_start_before >= window_end_before)",
            name=op.f("ck_milestones_window_starts_before_it_ends"),
        ),
        sa.ForeignKeyConstraint(
            ["phase_id"],
            ["schedule_phases.id"],
            name=op.f("fk_milestones_phase_id_schedule_phases"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["scope_categories.id"],
            name=op.f("fk_milestones_category_id_scope_categories"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_milestones")),
        comment=(
            "Marcos do cronograma (F-CRN-01). Guarda só fatos: Bloqueado, Destravado, Atrasado, "
            "Opcional e Arquivado se derivam na leitura."
        ),
    )
    op.create_index("ix_milestones_phase_id", "milestones", ["phase_id", "position"])
    dependencies = op.create_table(
        "milestone_dependencies",
        *_audit_columns(),
        sa.Column("milestone_id", sa.Uuid(), nullable=False, comment="O marco que espera."),
        sa.Column(
            "depends_on_id", sa.Uuid(), nullable=False, comment="O marco de que ele depende."
        ),
        sa.CheckConstraint(
            "milestone_id <> depends_on_id", name=op.f("ck_milestone_dependencies_not_self")
        ),
        sa.ForeignKeyConstraint(
            ["milestone_id"],
            ["milestones.id"],
            name=op.f("fk_milestone_dependencies_milestone_id_milestones"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["depends_on_id"],
            ["milestones.id"],
            name=op.f("fk_milestone_dependencies_depends_on_id_milestones"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_milestone_dependencies")),
        comment="Dependências entre marcos (F-CRN-03): A depende de B. Sai com exclusão lógica.",
    )
    op.create_index(
        "uq_milestone_dependencies_pair_live",
        "milestone_dependencies",
        ["milestone_id", "depends_on_id"],
        unique=True,
        sqlite_where=live,
        postgresql_where=live,
    )
    op.create_table(
        "milestone_changes",
        *_audit_columns(),
        sa.Column(
            "milestone_id", sa.Uuid(), nullable=False, comment="O marco que mudou de estado."
        ),
        sa.Column(
            "state_before",
            sa.String(12),
            comment="O estado marcado antes; nulo era o derivado.",
        ),
        sa.Column(
            "state_after",
            sa.String(12),
            comment="O estado marcado depois; nulo é reabrir, voltar ao derivado.",
        ),
        sa.Column(
            "ignored_block",
            sa.Boolean(),
            nullable=False,
            comment=(
                "Verdadeiro se o marco estava Bloqueado e o casal confirmou ignorar o bloqueio."
            ),
        ),
        sa.Column(
            "profile",
            sa.String(8),
            nullable=False,
            comment="Perfil de quem mudou, gravado para não depender do cadastro de usuários.",
        ),
        sa.CheckConstraint(
            f"state_before IN ({STATES})", name=op.f("ck_milestone_changes_milestone_state_before")
        ),
        sa.CheckConstraint(
            f"state_after IN ({STATES})", name=op.f("ck_milestone_changes_milestone_state_after")
        ),
        sa.CheckConstraint(
            f"profile IN ({PROFILES})", name=op.f("ck_milestone_changes_profile_kind")
        ),
        sa.CheckConstraint(
            "COALESCE(state_before, '') <> COALESCE(state_after, '')",
            name=op.f("ck_milestone_changes_state_changed"),
        ),
        sa.CheckConstraint(
            "NOT ignored_block OR state_after IS NOT NULL",
            name=op.f("ck_milestone_changes_ignored_block_needs_state"),
        ),
        sa.CheckConstraint(
            "profile != 'Ambos'", name=op.f("ck_milestone_changes_profile_is_login")
        ),
        sa.ForeignKeyConstraint(
            ["milestone_id"],
            ["milestones.id"],
            name=op.f("fk_milestone_changes_milestone_id_milestones"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_milestone_changes")),
        comment="Histórico de estado dos marcos (F-CRN-03, regra 4): só se acrescenta.",
    )
    op.create_index(
        "ix_milestone_changes_milestone_id", "milestone_changes", ["milestone_id", "created_at"]
    )

    now = datetime.now(UTC)
    audit = {"created_at": now, "updated_at": now, "version": 1}
    op.bulk_insert(
        phases,
        [
            {"id": _seed_id(f"fase:{number}"), "title": title, "position": number - 1, **audit}
            for number, title in enumerate(PHASES, start=1)
        ],
    )
    position_in_phase: dict[int, int] = {}
    milestone_rows, dependency_rows = [], []
    for code, phase, title, category, depends, window in MILESTONES:
        position = position_in_phase.get(phase, 0)
        position_in_phase[phase] = position + 1
        start, end, unit = window or (None, None, None)
        milestone_rows.append(
            {
                "id": _seed_id(f"marco:{code}"),
                "phase_id": _seed_id(f"fase:{phase}"),
                "position": position,
                "title": title,
                "responsible": "Ambos",
                "category_id": _seed_id(f"categoria:{category}") if category else None,
                "window_start_before": start,
                "window_end_before": end,
                "window_unit": unit,
                **audit,
            }
        )
        dependency_rows.extend(
            {
                "id": _seed_id(f"dependencia:{code}:{predecessor}"),
                "milestone_id": _seed_id(f"marco:{code}"),
                "depends_on_id": _seed_id(f"marco:{predecessor}"),
                **audit,
            }
            for predecessor in depends
        )
    op.bulk_insert(milestones, milestone_rows)
    op.bulk_insert(dependencies, dependency_rows)


def downgrade() -> None:
    op.drop_index("ix_milestone_changes_milestone_id", table_name="milestone_changes")
    op.drop_table("milestone_changes")
    op.drop_index("uq_milestone_dependencies_pair_live", table_name="milestone_dependencies")
    op.drop_table("milestone_dependencies")
    op.drop_index("ix_milestones_phase_id", table_name="milestones")
    op.drop_table("milestones")
    op.drop_table("schedule_phases")
