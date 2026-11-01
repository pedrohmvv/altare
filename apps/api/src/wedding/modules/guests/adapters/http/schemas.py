import datetime as dt
from uuid import UUID

from pydantic import BaseModel, Field

from wedding.modules.guests.domain.values import AgeBand, GuestStatus, Probability, Side
from wedding.shared_kernel.profile import ProfileKind

_VERSION = Field(ge=1, description="A versão que a tela viu; divergir dá 409.")


# Entrada: nenhum campo de autoria nem de perfil; os dois vêm sempre da sessão.
class HouseholdFieldsIn(BaseModel):
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


class GuestFieldsIn(BaseModel):
    name: str | None = None
    band: AgeBand = AgeBand.ADULT
    age: int | None = None
    probability: Probability = Probability.PROBABLE
    dietary_restriction: str | None = None
    note: str | None = None
    phone: str | None = None
    email: str | None = None


class HouseholdCreateIn(BaseModel):
    household: HouseholdFieldsIn
    first_guest: GuestFieldsIn


class HouseholdUpdateIn(HouseholdFieldsIn):
    version: int = _VERSION


class GuestUpdateIn(GuestFieldsIn):
    decline_reason: str | None = None
    version: int = _VERSION


class CompanionIn(BaseModel):
    name: str | None = None


class GuestStatusIn(BaseModel):
    status: GuestStatus
    reason: str | None = None
    version: int = _VERSION


class MoveIn(BaseModel):
    household_id: UUID
    version: int = _VERSION


# Saída: nenhum valor padrão, para o contrato declarar todos os campos como obrigatórios.
class HouseholdSummaryOut(BaseModel):
    total: int
    confirmed: int
    invited: int
    draft: int
    declined: int


class GuestOut(BaseModel):
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


class HouseholdOut(BaseModel):
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
    summary: HouseholdSummaryOut
    guests: list[GuestOut]
    version: int


class GuestListOut(BaseModel):
    households: list[HouseholdOut]


class GuestStatusChangeOut(BaseModel):
    id: UUID
    from_status: GuestStatus
    to_status: GuestStatus
    reason: str | None
    profile: ProfileKind
    changed_at: dt.datetime
