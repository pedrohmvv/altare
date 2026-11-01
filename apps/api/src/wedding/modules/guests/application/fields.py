from dataclasses import dataclass

from wedding.modules.guests.domain.values import AgeBand, Probability, Side


@dataclass(frozen=True)
class HouseholdFields:
    """O que o formulário do núcleo envia (F-CNV-01). Nada de autoria: ela vem da sessão."""

    name: str
    side: Side
    street: str | None = None
    number: str | None = None
    complement: str | None = None
    district: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    note: str | None = None


@dataclass(frozen=True)
class GuestFields:
    """O que o formulário da pessoa envia (F-CNV-01). O status muda por um caso de uso próprio."""

    name: str | None
    band: AgeBand = AgeBand.ADULT
    age: int | None = None
    probability: Probability = Probability.PROBABLE
    dietary_restriction: str | None = None
    note: str | None = None
    phone: str | None = None
    email: str | None = None
