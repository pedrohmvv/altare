from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from uuid import UUID

from wedding.modules.guests.domain.entities import Guest
from wedding.modules.guests.domain.values import GuestStatus


@dataclass(frozen=True)
class HouseholdSummary:
    """O resumo do núcleo ("3 de 4 confirmados", F-CNV-04): derivado, nunca gravado."""

    total: int
    confirmed: int
    invited: int
    draft: int
    declined: int


def household_summary(statuses: Iterable[GuestStatus]) -> HouseholdSummary:
    counts = dict.fromkeys(GuestStatus, 0)
    for status in statuses:
        counts[status] += 1
    return HouseholdSummary(
        total=sum(counts.values()),
        confirmed=counts[GuestStatus.CONFIRMED],
        invited=counts[GuestStatus.INVITED],
        draft=counts[GuestStatus.DRAFT],
        declined=counts[GuestStatus.DECLINED],
    )


def display_order(guests: Sequence[Guest]) -> list[Guest]:
    """Ordem de cadastro, com o acompanhante logo depois do titular (F-CNV-02). Um acompanhante
    cujo titular não está na lista fica onde o cadastro o pôs."""
    ordered = sorted(guests, key=lambda guest: guest.position)
    present = {guest.id for guest in ordered}
    companions: dict[UUID, Guest] = {
        guest.companion_of_id: guest
        for guest in ordered
        if guest.companion_of_id is not None and guest.companion_of_id in present
    }
    result: list[Guest] = []
    for guest in ordered:
        if guest.companion_of_id is not None and guest.companion_of_id in present:
            continue
        result.append(guest)
        if guest.id in companions:
            result.append(companions[guest.id])
    return result
