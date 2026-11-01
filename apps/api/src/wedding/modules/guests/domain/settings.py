from dataclasses import dataclass
from uuid import UUID

from wedding.modules.guests.domain.age import AgeLimits
from wedding.modules.guests.domain.headcount import Weights


@dataclass
class GuestSettings:
    """As decisões do casal sobre a lista: os pesos por probabilidade e os limites de idade. Há uma
    linha só, criada vazia pela migration (nada é presumido, `D-030`). Os três pesos andam juntos:
    ou os três existem ou nenhum, e `version` é mantido pelo mapeamento."""

    id: UUID
    weight_certain_pct: int | None = None
    weight_probable_pct: int | None = None
    weight_phase_2_pct: int | None = None
    exempt_until_age: int | None = None
    paying_until_age: int | None = None
    version: int = 0

    @property
    def weights(self) -> Weights | None:
        pcts = (self.weight_certain_pct, self.weight_probable_pct, self.weight_phase_2_pct)
        if any(pct is None for pct in pcts):
            return None
        certain, probable, phase_2 = pcts
        assert certain is not None
        assert probable is not None
        assert phase_2 is not None
        return Weights(certain, probable, phase_2)

    @property
    def age_limits(self) -> AgeLimits:
        return AgeLimits(self.exempt_until_age, self.paying_until_age)

    def update(self, weights: Weights | None, limits: AgeLimits) -> bool:
        """Devolve se algo mudou. Mudar os limites ou os pesos não toca em nenhuma pessoa: a idade
        só sugere, e o ponderado é derivado (F-CNV-03, regra 4)."""
        new_pcts = (
            (weights.certain_pct, weights.probable_pct, weights.phase_2_pct)
            if weights
            else (None, None, None)
        )
        current = (
            self.weight_certain_pct,
            self.weight_probable_pct,
            self.weight_phase_2_pct,
            self.exempt_until_age,
            self.paying_until_age,
        )
        updated = (*new_pcts, limits.exempt_until, limits.paying_until)
        if current == updated:
            return False
        (
            self.weight_certain_pct,
            self.weight_probable_pct,
            self.weight_phase_2_pct,
            self.exempt_until_age,
            self.paying_until_age,
        ) = updated
        return True
