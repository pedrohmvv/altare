from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from wedding.modules.wedding.domain.errors import CatalogItemNotDeletable, DiscardReasonRequired
from wedding.modules.wedding.domain.scope_values import (
    Origin,
    Priority,
    ScopeStatus,
    clean_estimate,
    clean_name,
    clean_note,
    clean_reason,
    name_key,
)
from wedding.shared_kernel.profile import ProfileKind


def _set_hidden(
    current: datetime | None, hidden: bool, now: datetime
) -> tuple[datetime | None, bool]:
    """Oculta ou mostra sem repetir: devolve o novo `hidden_at` e se algo mudou."""
    if hidden:
        return (current, False) if current is not None else (now, True)
    return (None, current is not None)


@dataclass
class ScopeGroup:
    """Um grupo de frentes (F-PLN-02). `version` é mantido pelo mapeamento (bloqueio otimista)."""

    id: UUID
    name: str
    position: int
    origin: Origin
    name_key: str = field(init=False, default="")
    hidden_at: datetime | None = None
    deleted_at: datetime | None = None
    deleted_by: UUID | None = None
    version: int = 0

    def __post_init__(self) -> None:
        self.name = clean_name(self.name)
        self.name_key = name_key(self.name)

    def rename(self, name: str) -> bool:
        cleaned = clean_name(name)
        if cleaned == self.name:
            return False
        self.name, self.name_key = cleaned, name_key(cleaned)
        return True

    def set_hidden(self, hidden: bool, now: datetime) -> bool:
        self.hidden_at, changed = _set_hidden(self.hidden_at, hidden, now)
        return changed

    def delete(self, now: datetime, by: UUID | None) -> None:
        """Só o grupo criado pelo casal sai; o do catálogo só se oculta (F-PLN-02, regra 1)."""
        if self.origin is Origin.CATALOG:
            raise CatalogItemNotDeletable()
        self.deleted_at, self.deleted_by = now, by


@dataclass
class ScopeCategory:
    """Uma frente do casamento e a decisão conjunta sobre ela (F-PLN-03). A prioridade de cada um
    fica em `ScopeEvaluation`; alinhamento, progresso e totais são derivados, nunca gravados."""

    id: UUID
    group_id: UUID
    name: str
    position: int
    origin: Origin
    status: ScopeStatus = ScopeStatus.IN_DISCUSSION
    estimate_cents: int | None = None
    name_key: str = field(init=False, default="")
    hidden_at: datetime | None = None
    deleted_at: datetime | None = None
    deleted_by: UUID | None = None
    version: int = 0

    def __post_init__(self) -> None:
        self.name = clean_name(self.name)
        self.name_key = name_key(self.name)
        self.estimate_cents = clean_estimate(self.estimate_cents)

    def update(self, name: str, group_id: UUID, estimate_cents: int | None) -> bool:
        cleaned_name = clean_name(name)
        cleaned_estimate = clean_estimate(estimate_cents)
        before = (self.name, self.group_id, self.estimate_cents)
        after = (cleaned_name, group_id, cleaned_estimate)
        if before == after:
            return False
        self.name, self.name_key = cleaned_name, name_key(cleaned_name)
        self.group_id, self.estimate_cents = group_id, cleaned_estimate
        return True

    def change_status(self, to: ScopeStatus, reason: str | None) -> bool:
        """`Fica de fora` exige motivo (F-PLN-03, regra 1); repetir o status não é mudança."""
        if to is self.status:
            return False
        if to is ScopeStatus.OUT and clean_reason(reason) is None:
            raise DiscardReasonRequired()
        self.status = to
        return True

    def set_hidden(self, hidden: bool, now: datetime) -> bool:
        self.hidden_at, changed = _set_hidden(self.hidden_at, hidden, now)
        return changed

    def delete(self, now: datetime, by: UUID | None) -> None:
        if self.origin is Origin.CATALOG:
            raise CatalogItemNotDeletable()
        self.deleted_at, self.deleted_by = now, by


@dataclass
class ScopeEvaluation:
    """A prioridade e a nota de um perfil sobre uma categoria (F-PLN-04 e F-PLN-05). Existe um par
    por categoria desde que ela nasce, então avaliar sempre atualiza."""

    id: UUID
    category_id: UUID
    profile: ProfileKind
    priority: Priority | None = None
    note: str | None = None
    version: int = 0

    def update(self, priority: Priority | None, note: str | None) -> bool:
        cleaned_note = clean_note(note)
        if (priority, cleaned_note) == (self.priority, self.note):
            return False
        self.priority, self.note = priority, cleaned_note
        return True


@dataclass
class ScopeStatusChange:
    """Uma mudança de status (F-PLN-03): só se acrescenta; o instante vem do histórico básico."""

    id: UUID
    category_id: UUID
    from_status: ScopeStatus
    to_status: ScopeStatus
    reason: str | None
    profile: ProfileKind
