from dataclasses import dataclass
from datetime import date
from typing import NamedTuple
from uuid import UUID

from wedding.modules.schedule.domain.values import ManualState, clean_note, clean_target_date
from wedding.shared_kernel.profile import ProfileKind


@dataclass
class Phase:
    """Uma fase do cronograma (F-CRN-01). `version` é mantido pelo mapeamento."""

    id: UUID
    title: str
    position: int
    version: int = 0


@dataclass
class Milestone:
    """Um marco (F-CRN-01). Guarda só fatos: o estado manual, o responsável, o prazo e a nota. Se
    está `Bloqueado`, `Destravado`, `Atrasado` ou arquivado se deriva na leitura
    (`domain/derivation.py`), nunca se grava. `version` é mantido pelo mapeamento."""

    id: UUID
    phase_id: UUID
    title: str
    position: int
    responsible: ProfileKind = ProfileKind.AMBOS
    category_id: UUID | None = None
    note: str | None = None
    target_date: date | None = None
    manual_state: ManualState | None = None
    version: int = 0

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


class Dependency(NamedTuple):
    """ "`milestone_id` depende de `depends_on_id`" (F-CRN-03)."""

    milestone_id: UUID
    depends_on_id: UUID
