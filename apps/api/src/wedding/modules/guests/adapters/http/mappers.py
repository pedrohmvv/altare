from wedding.modules.guests.adapters.http.schemas import (
    GuestFieldsIn,
    GuestListOut,
    GuestOut,
    GuestStatusChangeOut,
    HouseholdFieldsIn,
    HouseholdOut,
    HouseholdSummaryOut,
)
from wedding.modules.guests.application.dto import (
    GuestDto,
    GuestListDto,
    GuestStatusChangeDto,
    HouseholdDto,
)
from wedding.modules.guests.application.fields import GuestFields, HouseholdFields


def to_household_fields(body: HouseholdFieldsIn) -> HouseholdFields:
    return HouseholdFields(
        name=body.name,
        side=body.side,
        street=body.street,
        number=body.number,
        complement=body.complement,
        district=body.district,
        city=body.city,
        state=body.state,
        postal_code=body.postal_code,
        note=body.note,
    )


def to_guest_fields(body: GuestFieldsIn) -> GuestFields:
    return GuestFields(
        name=body.name,
        band=body.band,
        age=body.age,
        probability=body.probability,
        dietary_restriction=body.dietary_restriction,
        note=body.note,
        phone=body.phone,
        email=body.email,
    )


def _guest(dto: GuestDto) -> GuestOut:
    return GuestOut.model_validate(
        {
            "id": dto.id,
            "household_id": dto.household_id,
            "name": dto.name,
            "companion_of_id": dto.companion_of_id,
            "holder_name": dto.holder_name,
            "band": dto.band,
            "age": dto.age,
            "probability": dto.probability,
            "status": dto.status,
            "decline_reason": dto.decline_reason,
            "dietary_restriction": dto.dietary_restriction,
            "note": dto.note,
            "phone": dto.phone,
            "whatsapp_url": dto.whatsapp_url,
            "email": dto.email,
            "version": dto.version,
        }
    )


def _household(dto: HouseholdDto) -> HouseholdOut:
    summary = dto.summary
    return HouseholdOut.model_validate(
        {
            "id": dto.id,
            "name": dto.name,
            "side": dto.side,
            "street": dto.street,
            "number": dto.number,
            "complement": dto.complement,
            "district": dto.district,
            "city": dto.city,
            "state": dto.state,
            "postal_code": dto.postal_code,
            "note": dto.note,
            "summary": HouseholdSummaryOut.model_validate(
                {
                    "total": summary.total,
                    "confirmed": summary.confirmed,
                    "invited": summary.invited,
                    "draft": summary.draft,
                    "declined": summary.declined,
                }
            ),
            "guests": [_guest(guest) for guest in dto.guests],
            "version": dto.version,
        }
    )


def to_guest_list_out(dto: GuestListDto) -> GuestListOut:
    return GuestListOut.model_validate({"households": [_household(h) for h in dto.households]})


def to_status_change_out(dto: GuestStatusChangeDto) -> GuestStatusChangeOut:
    return GuestStatusChangeOut.model_validate(
        {
            "id": dto.id,
            "from_status": dto.from_status,
            "to_status": dto.to_status,
            "reason": dto.reason,
            "profile": dto.profile,
            "changed_at": dto.changed_at,
        }
    )
