from uuid import UUID

from wedding.modules.guests.application.dto import GuestDto, GuestListDto, HouseholdDto
from wedding.modules.guests.application.ports import GuestRepository
from wedding.modules.guests.domain.contact import format_phone, format_postal_code, whatsapp_url
from wedding.modules.guests.domain.entities import Guest, Household
from wedding.modules.guests.domain.rules import display_order, household_summary
from wedding.shared_kernel.errors import NotFound


def build_guest_list(guests: GuestRepository) -> GuestListDto:
    """A lista inteira, com tudo o que é derivado calculado aqui e nunca gravado
    (`architecture.md` §5): o resumo do núcleo, o link do WhatsApp e o titular do acompanhante."""
    households = sorted(guests.list_households(), key=lambda household: household.name_key)
    by_household: dict[UUID, list[Guest]] = {}
    for guest in guests.list_guests():
        by_household.setdefault(guest.household_id, []).append(guest)
    return GuestListDto(
        tuple(
            _household_dto(household, display_order(by_household.get(household.id, [])))
            for household in households
        )
    )


def _household_dto(household: Household, members: list[Guest]) -> HouseholdDto:
    names = {member.id: member.name for member in members}
    return HouseholdDto(
        id=household.id,
        name=household.name,
        side=household.side,
        street=household.street,
        number=household.number,
        complement=household.complement,
        district=household.district,
        city=household.city,
        state=household.state,
        postal_code=format_postal_code(household.postal_code) if household.postal_code else None,
        note=household.note,
        summary=household_summary(member.status for member in members),
        guests=tuple(_guest_dto(member, names) for member in members),
        version=household.version,
    )


def _guest_dto(guest: Guest, names: dict[UUID, str | None]) -> GuestDto:
    return GuestDto(
        id=guest.id,
        household_id=guest.household_id,
        name=guest.name,
        companion_of_id=guest.companion_of_id,
        holder_name=names.get(guest.companion_of_id) if guest.companion_of_id else None,
        band=guest.band,
        age=guest.age,
        probability=guest.probability,
        status=guest.status,
        decline_reason=guest.decline_reason,
        dietary_restriction=guest.dietary_restriction,
        note=guest.note,
        phone=format_phone(guest.phone) if guest.phone else None,
        whatsapp_url=whatsapp_url(guest.phone),
        email=guest.email,
        version=guest.version,
    )


def require_household(guests: GuestRepository, household_id: UUID) -> Household:
    household = guests.get_household(household_id)
    if household is None:
        raise NotFound()
    return household


def require_guest(guests: GuestRepository, guest_id: UUID) -> Guest:
    guest = guests.get_guest(guest_id)
    if guest is None:
        raise NotFound()
    return guest
