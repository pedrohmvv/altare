import datetime as dt
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field

from wedding.modules.guests.domain.values import (
    AgeBand,
    GuestStatus,
    InviteChannel,
    Probability,
    Side,
)
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


class InviteIn(BaseModel):
    """O envio do convite do núcleo (F-CNV-05): data e canal juntos. `move_drafts` é o aceite da
    oferta de mover os rascunhos para `Convidado`; sem ele nenhum status muda."""

    sent_on: dt.date
    channel: InviteChannel
    move_drafts: bool = False
    version: int = _VERSION


class ExportFormat(StrEnum):
    XLSX = "xlsx"
    CSV = "csv"


class ExportIn(BaseModel):
    """O que exportar (F-CNV-08): o formato (Excel por padrão) e os ids das pessoas que estão na
    tela. Ausente, leva todas. Nenhum texto de busca viaja: o filtro é do navegador."""

    format: ExportFormat = ExportFormat.XLSX
    guest_ids: list[UUID] | None = None


class WeightsIn(BaseModel):
    certain_pct: int
    probable_pct: int
    phase_2_pct: int


class GuestSettingsIn(BaseModel):
    """Os três pesos andam juntos: o objeto inteiro ou nada (nulo limpa)."""

    weights: WeightsIn | None = None
    exempt_until_age: int | None = None
    paying_until_age: int | None = None
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
    suggested_band: AgeBand | None
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
    invite_sent_on: dt.date | None
    invite_channel: InviteChannel | None
    summary: HouseholdSummaryOut
    guests: list[GuestOut]
    version: int


class BandCountsOut(BaseModel):
    adults: int
    paying_children: int
    exempt_children: int
    total: int


class HeadcountOut(BaseModel):
    """Os contadores derivados (F-CNV-06). O ponderado vem em centésimos de pessoa e já arredondado
    para cima; fica nulo enquanto os pesos não existem ("defina os pesos")."""

    total_nominal: BandCountsOut
    confirmed: BandCountsOut
    not_attending: BandCountsOut
    certain_or_confirmed: BandCountsOut
    weighted_adults_hundredths: int | None
    weighted_paying_children_hundredths: int | None
    weighted_rounded_up: int | None


class WeightsOut(BaseModel):
    certain_pct: int
    probable_pct: int
    phase_2_pct: int


class GuestSettingsOut(BaseModel):
    weights: WeightsOut | None
    exempt_until_age: int | None
    paying_until_age: int | None
    version: int


class GuestListOut(BaseModel):
    households: list[HouseholdOut]
    headcount: HeadcountOut
    settings: GuestSettingsOut


class GuestStatusChangeOut(BaseModel):
    id: UUID
    from_status: GuestStatus
    to_status: GuestStatus
    reason: str | None
    profile: ProfileKind
    changed_at: dt.datetime
