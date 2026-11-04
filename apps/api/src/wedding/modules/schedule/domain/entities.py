from dataclasses import dataclass
from datetime import date, datetime
from typing import NamedTuple
from uuid import UUID

from wedding.modules.schedule.domain.values import (
    ManualState,
    clean_milestone_title,
    clean_note,
    clean_phase_title,
    clean_target_date,
)
from wedding.modules.schedule.domain.windows import Window, WindowUnit, validate_window
from wedding.shared_kernel.profile import ProfileKind


@dataclass
class Phase:
    """Uma fase do cronograma (F-CRN-01). `version` é mantido pelo mapeamento."""

    id: UUID
    title: str
    position: int
    version: int = 0

    def __post_init__(self) -> None:
        self.title = clean_phase_title(self.title)

    def rename(self, title: str) -> bool:
        cleaned = clean_phase_title(title)
        if cleaned == self.title:
            return False
        self.title = cleaned
        return True


@dataclass
class Milestone:
    """Um marco (F-CRN-01). Guarda só fatos: o estado manual, o responsável, o prazo manual, a
    janela e a nota. As datas calculadas da janela, o prazo efetivo, a contagem regressiva e se está
    `Bloqueado`, `Destravado`, `Atrasado` ou arquivado se derivam na leitura
    (`domain/derivation.py`), nunca se gravam. `version` é mantido pelo mapeamento."""

    id: UUID
    phase_id: UUID
    title: str
    position: int
    responsible: ProfileKind = ProfileKind.AMBOS
    category_id: UUID | None = None
    note: str | None = None
    target_date: date | None = None
    manual_state: ManualState | None = None
    # A janela, em deslocamentos antes da data do casamento (F-CRN-05); `window_unit` guarda o
    # valor de `WindowUnit`. Sem `window_edited`, é a sugestão genérica da semente (F-CRN-02).
    window_start_before: int | None = None
    window_end_before: int | None = None
    window_unit: str | None = None
    window_edited: bool = False
    # Sobe quando o conjunto de predecessores muda: duas edições das dependências do mesmo marco
    # se conflitam (`D-072`, `members_revision`), embora a linha do marco em si não mude.
    dependencies_revision: int = 0
    deleted_at: datetime | None = None
    deleted_by: UUID | None = None
    version: int = 0

    def __post_init__(self) -> None:
        self.title = clean_milestone_title(self.title)

    def rename(self, title: str) -> bool:
        cleaned = clean_milestone_title(title)
        if cleaned == self.title:
            return False
        self.title = cleaned
        return True

    def link_category(self, category_id: UUID | None) -> bool:
        """Liga o marco a outra categoria do Mapa (ou a nenhuma); muda o efeito derivado
        (F-CRN-04), nunca o estado marcado."""
        if category_id == self.category_id:
            return False
        self.category_id = category_id
        return True

    def move_to(self, phase_id: UUID, position: int) -> bool:
        """Muda de fase, indo para a posição dada; a mesma fase não é mudança."""
        if phase_id == self.phase_id:
            return False
        self.phase_id, self.position = phase_id, position
        return True

    def touch_dependencies(self) -> None:
        self.dependencies_revision += 1

    def delete(self, now: datetime, by: UUID | None) -> None:
        self.deleted_at, self.deleted_by = now, by

    def restore(self, position: int) -> None:
        """Volta ao fim da fase em que estava; o estado marcado e o resto ficam como estavam."""
        self.deleted_at = self.deleted_by = None
        self.position = position

    def edit(self, responsible: ProfileKind, note: str | None, target_date: date | None) -> bool:
        """Troca responsável, nota e prazo-alvo manual e diz se algo mudou."""
        cleaned_note = clean_note(note)
        cleaned_target = clean_target_date(target_date)
        before = (self.responsible, self.note, self.target_date)
        after = (responsible, cleaned_note, cleaned_target)
        if before == after:
            return False
        self.responsible, self.note, self.target_date = after
        return True

    @property
    def window(self) -> Window | None:
        """A janela do marco, sugerida pelo catálogo ou editada pelo casal; `None` se não tem."""
        if self.window_start_before is None or self.window_end_before is None:
            return None
        if self.window_unit is None:
            return None
        return Window(
            self.window_start_before, self.window_end_before, WindowUnit(self.window_unit)
        )

    @property
    def window_is_suggestion(self) -> bool:
        """Há janela e ninguém a editou: o rótulo "sugestão genérica" (F-CRN-02)."""
        return self.window is not None and not self.window_edited

    def set_window(self, start_before: int, end_before: int, unit: WindowUnit) -> bool:
        """O casal edita a janela (F-CRN-05, regra 5), mesmo a de um marco que não tinha. Mesmo com
        os deslocamentos da sugestão, a primeira vez já conta como edição (deixa de ser sugestão);
        repetir uma janela já editada não é mudança."""
        validate_window(start_before, end_before, unit)
        after = (start_before, end_before, unit.value)
        before = (self.window_start_before, self.window_end_before, self.window_unit)
        if self.window_edited and before == after:
            return False
        self.window_start_before, self.window_end_before, self.window_unit = after
        self.window_edited = True
        return True

    def set_manual_state(self, state: ManualState | None) -> bool:
        """`None` reabre: volta ao estado derivado. Repetir o estado não é mudança."""
        if state is self.manual_state:
            return False
        self.manual_state = state
        return True


@dataclass
class MilestoneChange:
    """Uma mudança de estado manual (F-CRN-03, regra 4): só se acrescenta; o instante vem do
    histórico básico. `None` é "sem marca", o estado derivado."""

    id: UUID
    milestone_id: UUID
    state_before: ManualState | None
    state_after: ManualState | None
    ignored_block: bool
    profile: ProfileKind


@dataclass
class MilestoneDependency:
    """O vínculo gravado "`milestone_id` depende de `depends_on_id`". Sai e volta com o carimbo de
    exclusão do marco que o levou junto (F-CRN-01, regra 1)."""

    id: UUID
    milestone_id: UUID
    depends_on_id: UUID
    deleted_at: datetime | None = None
    deleted_by: UUID | None = None
    version: int = 0

    def delete(self, now: datetime, by: UUID | None) -> None:
        self.deleted_at, self.deleted_by = now, by

    def restore(self) -> None:
        self.deleted_at = self.deleted_by = None

    def as_edge(self) -> "Dependency":
        return Dependency(self.milestone_id, self.depends_on_id)


class Dependency(NamedTuple):
    """ "`milestone_id` depende de `depends_on_id`" (F-CRN-03)."""

    milestone_id: UUID
    depends_on_id: UUID
