import sqlalchemy as sa
from sqlalchemy import (
    BigInteger,
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

from wedding.modules.schedule.domain.attachments import AttachmentKind
from wedding.modules.schedule.domain.values import ManualState, OwnerKind, TaskState
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
    CheckConstraint("length(trim(title)) > 0", name="title_not_blank"),
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
        comment=(
            "Prazo-alvo digitado à mão (F-CRN-05); nulo se não há. Sem ele, o prazo é o fim da "
            "janela calculada, que se deriva e nunca se grava; o Atrasado se deriva do prazo."
        ),
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
        comment="Janela (F-CRN-05): início, quantas unidades antes da data; nulo sem janela.",
    ),
    Column(
        "window_end_before",
        Integer,
        comment="Janela: fim, quantas unidades antes da data; nulo sem janela.",
    ),
    Column("window_unit", String(8), comment="meses ou semanas; nulo sem janela."),
    Column(
        "window_edited",
        Boolean,
        nullable=False,
        server_default=sa.false(),
        comment=(
            "Verdadeiro se o casal editou a janela; falso é a sugestão genérica da semente "
            "(F-CRN-02). Sem janela, falso."
        ),
    ),
    Column(
        "dependencies_revision",
        Integer,
        nullable=False,
        server_default=text("0"),
        comment="Sobe quando o conjunto de predecessores muda: duas edições se conflitam.",
    ),
    CheckConstraint("position >= 0", name="position_not_negative"),
    CheckConstraint("length(trim(title)) > 0", name="title_not_blank"),
    CheckConstraint("dependencies_revision >= 0", name="dependencies_revision_not_negative"),
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

schedule_tasks = Table(
    "schedule_tasks",
    metadata,
    *audit_columns(),
    Column("title", String(120), nullable=False, comment="O nome da tarefa avulsa; exibido."),
    Column(
        "responsible",
        _enum(ProfileKind, "task_responsible", 8),
        nullable=False,
        comment="Noivo, Noiva ou Ambos; por padrão, o perfil de quem criou (F-CRN-06).",
    ),
    Column("note", String(500), comment="Nota livre."),
    Column(
        "target_date",
        Date,
        comment=(
            "Prazo digitado à mão; nulo se não há. O Atrasada e os dias que faltam se derivam "
            "dele na leitura e nunca se gravam."
        ),
    ),
    Column(
        "state",
        _enum(TaskState, "task_state", 12),
        nullable=False,
        comment="A fazer, Em andamento ou Concluída (feminino, diferente do Concluído do marco).",
    ),
    CheckConstraint("length(trim(title)) > 0", name="title_not_blank"),
    comment=(
        "Tarefas avulsas do cronograma (F-CRN-06): sem fase, categoria nem dependências, fora da "
        "derivação dos marcos. Atrasada se deriva na leitura."
    ),
)

checklist_items = Table(
    "checklist_items",
    metadata,
    *audit_columns(),
    Column(
        "milestone_id",
        Uuid,
        ForeignKey("milestones.id", ondelete="RESTRICT"),
        comment="O marco dono do item; nulo se o dono é uma tarefa avulsa.",
    ),
    Column(
        "task_id",
        Uuid,
        ForeignKey("schedule_tasks.id", ondelete="RESTRICT"),
        comment="A tarefa avulsa dona do item; nulo se o dono é um marco.",
    ),
    Column("text", String(200), nullable=False, comment="O que fazer; exibido."),
    Column(
        "done",
        Boolean,
        nullable=False,
        server_default=sa.false(),
        comment="Verdadeiro se o item foi feito; nunca muda o estado do dono (F-CRN-07).",
    ),
    Column(
        "position",
        Integer,
        nullable=False,
        comment="Ordem entre os itens vivos do dono, a partir de zero; pode ter buracos.",
    ),
    CheckConstraint("length(trim(text)) > 0", name="text_not_blank"),
    CheckConstraint("position >= 0", name="position_not_negative"),
    CheckConstraint(
        "(milestone_id IS NOT NULL AND task_id IS NULL) "
        "OR (milestone_id IS NULL AND task_id IS NOT NULL)",
        name="one_owner",
    ),
    Index(
        "ix_checklist_items_milestone_live",
        "milestone_id",
        "position",
        sqlite_where=_LIVE,
        postgresql_where=_LIVE,
    ),
    Index(
        "ix_checklist_items_task_live",
        "task_id",
        "position",
        sqlite_where=_LIVE,
        postgresql_where=_LIVE,
    ),
    comment=(
        "Itens do checklist (F-CRN-07) de um marco ou de uma tarefa avulsa: exatamente um dos "
        "dois donos. Sair é exclusão lógica; o dono excluído esconde os itens, sem apagá-los."
    ),
)

attachments = Table(
    "attachments",
    metadata,
    *audit_columns(),
    Column(
        "owner_type",
        _enum(OwnerKind, "attachment_owner_type", 10),
        nullable=False,
        comment="De quem é o anexo: milestones (um marco) ou tasks (uma tarefa avulsa).",
    ),
    Column(
        "owner_id",
        Uuid,
        nullable=False,
        comment=(
            "O id do marco ou da avulsa, conforme owner_type. Sem chave estrangeira: a tabela é "
            "genérica e a integridade fica no caso de uso e no leitor (D-080)."
        ),
    ),
    Column(
        "kind",
        _enum(AttachmentKind, "attachment_kind", 4),
        nullable=False,
        comment="link ou file.",
    ),
    Column(
        "profile",
        _enum(ProfileKind, "profile_kind", 8),
        nullable=False,
        comment="Quem anexou; só esse perfil remove (F-CRN-08).",
    ),
    Column("url", String(2000), comment="O endereço, já validado; nulo para arquivo."),
    Column(
        "file_id",
        Uuid,
        ForeignKey("file_assets.id", ondelete="RESTRICT"),
        comment="O arquivo enviado pelo módulo de arquivos; nulo para link.",
    ),
    Column(
        "file_name",
        String(120),
        comment="Cópia do nome do arquivo ao anexar; nulo para link. O arquivo é imutável.",
    ),
    Column(
        "content_type",
        String(20),
        comment="Cópia do tipo do arquivo ao anexar (PDF ou imagem); nulo para link.",
    ),
    Column(
        "size_bytes",
        BigInteger,
        comment="Cópia do tamanho do arquivo em bytes ao anexar; nulo para link.",
    ),
    Column("title", String(120), comment="Texto curto, opcional."),
    Column("comment", String(500), comment="Texto livre, opcional."),
    CheckConstraint("profile != 'Ambos'", name="profile_is_login"),
    CheckConstraint(
        "(kind = 'link' AND url IS NOT NULL AND file_id IS NULL AND file_name IS NULL "
        "AND content_type IS NULL AND size_bytes IS NULL) "
        "OR (kind = 'file' AND url IS NULL AND file_id IS NOT NULL AND file_name IS NOT NULL "
        "AND content_type IS NOT NULL AND size_bytes IS NOT NULL)",
        name="kind_matches_content",
    ),
    Index(
        "ix_attachments_owner_live",
        "owner_type",
        "owner_id",
        "created_at",
        sqlite_where=_LIVE,
        postgresql_where=_LIVE,
    ),
    comment=(
        "Anexos de marcos e de tarefas avulsas (F-CRN-08): um link ou um arquivo já enviado, com "
        "a cópia do nome, tipo e tamanho. Sair é exclusão lógica; o dono excluído esconde os "
        "anexos, sem apagá-los."
    ),
)
