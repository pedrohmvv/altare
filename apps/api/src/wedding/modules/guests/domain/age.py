from dataclasses import dataclass

from wedding.modules.guests.domain.errors import InvalidAgeLimits
from wedding.modules.guests.domain.values import MAX_CHILD_AGE, AgeBand


def _valid(limit: int | None) -> bool:
    return limit is None or (
        isinstance(limit, int) and not isinstance(limit, bool) and 0 <= limit <= MAX_CHILD_AGE
    )


@dataclass(frozen=True)
class AgeLimits:
    """ "Isenta até N anos" e "pagante até M anos" (F-CNV-03): decisão do casal, vazia no início,
    porque a regra de cobrança depende de cada fornecedor. Só servem para sugerir a faixa."""

    exempt_until: int | None = None
    paying_until: int | None = None

    def __post_init__(self) -> None:
        if not (_valid(self.exempt_until) and _valid(self.paying_until)):
            raise InvalidAgeLimits()
        if (
            self.exempt_until is not None
            and self.paying_until is not None
            and self.exempt_until > self.paying_until
        ):
            raise InvalidAgeLimits()


def suggest_band(age: int | None, limits: AgeLimits) -> AgeBand | None:
    """A faixa que a idade sugere, só quando os limites decidem (F-CNV-03, regra 3): até N isenta,
    de N a M pagante, acima de M adulta. Faltando o limite que decide, não há sugestão. Nunca muda a
    faixa sozinha: quem aplica é o casal."""
    if age is None:
        return None
    exempt, paying = limits.exempt_until, limits.paying_until
    if exempt is not None and age <= exempt:
        return AgeBand.EXEMPT_CHILD
    if paying is not None and age > paying:
        return AgeBand.ADULT
    if exempt is not None and paying is not None and exempt < age <= paying:
        return AgeBand.PAYING_CHILD
    return None
