from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from wedding.modules.guests.domain.rules import HouseholdSummary
from wedding.modules.guests.domain.values import AgeBand, GuestStatus, Probability, Side
from wedding.shared_kernel.profile import ProfileKind


@dataclass(frozen=True)
class GuestDto:
    id: UUID
    household_id: UUID
    name: str | None
    companion_of_id: UUID | None
    holder_name: str | None
    band: AgeBand
    age: int | None
    probability: Probability
    status: GuestStatus
    decline_reason: str | None
    dietary_restriction: str | None
    note: str | None
    phone: str | None
    whatsapp_url: str | None
    email: str | None
    version: int


@dataclass(frozen=True)
class HouseholdDto:
    id: UUID
    name: str
    side: Side
    street: str | None
    number: str | None
    complement: str | None
    district: str | None
    city: str | None
    state: str | None
    postal_code: str | None
    note: str | None
    summary: HouseholdSummary
    guests: tuple[GuestDto, ...]
    version: int


@dataclass(frozen=True)
class GuestListDto:
    households: tuple[HouseholdDto, ...]


@dataclass(frozen=True)
class GuestStatusChangeDto:
    id: UUID
    from_status: GuestStatus
    to_status: GuestStatus
    reason: str | None
    profile: ProfileKind
    changed_at: datetime
