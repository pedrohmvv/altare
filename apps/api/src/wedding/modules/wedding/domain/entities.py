from dataclasses import dataclass
from typing import Any
from uuid import UUID

from wedding.modules.wedding.domain.errors import BaselineValueRequired, InvalidBaselineValue
from wedding.modules.wedding.domain.value_objects import (
    VALUE_TYPES,
    BaselineKey,
    BaselineValue,
    DefinitionStatus,
)
from wedding.shared_kernel.profile import ProfileKind

MAX_NOTE = 500


@dataclass
class BaselineField:
    """Uma variável estrutural do casamento (F-PLN-01): nasce vazia e `Em definição`, e vira
    `Definido` quando o casal decide. O valor é guardado em JSON, já validado pelo objeto de valor
    da chave; `version` é mantido pelo mapeamento (bloqueio otimista)."""

    id: UUID
    key: BaselineKey
    status: DefinitionStatus
    value: dict[str, Any] | None = None
    note: str | None = None
    version: int = 0

    def update(
        self, value: BaselineValue | None, status: DefinitionStatus, note: str | None
    ) -> bool:
        """Troca o estado do campo e diz se algo mudou. `Definido` exige valor (F-PLN-01, regra 1);
        voltar a `Em definição` é permitido (regra 4)."""
        if value is not None and not isinstance(value, VALUE_TYPES[self.key]):
            raise TypeError(f"{type(value).__name__} não é o valor de {self.key.value}")
        if status is DefinitionStatus.DEFINED and value is None:
            raise BaselineValueRequired()
        cleaned_note = (note or "").strip() or None
        if cleaned_note is not None and len(cleaned_note) > MAX_NOTE:
            raise InvalidBaselineValue()

        new_value = value.to_json() if value is not None else None
        if (new_value, status, cleaned_note) == (self.value, self.status, self.note):
            return False
        self.value, self.status, self.note = new_value, status, cleaned_note
        return True

    def snapshot(self) -> dict[str, Any]:
        """O estado do campo como dado simples, para o histórico guardar o antes e o depois."""
        return {"status": self.status.value, "value": self.value, "note": self.note}


@dataclass
class BaselineChange:
    """Uma alteração de campo (F-PLN-01, regra 3): o antes e o depois, com o perfil de quem mexeu.
    Só se acrescenta, nunca se edita; o instante vem do histórico básico (`created_at`)."""

    id: UUID
    key: BaselineKey
    before: dict[str, Any]
    after: dict[str, Any]
    profile: ProfileKind
