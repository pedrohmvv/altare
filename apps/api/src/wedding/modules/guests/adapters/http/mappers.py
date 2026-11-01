from wedding.modules.guests.adapters.http.schemas import (
    BandCountsOut,
    GuestFieldsIn,
    GuestListOut,
    GuestOut,
    GuestSettingsOut,
    GuestStatusChangeOut,
    HeadcountOut,
    HouseholdFieldsIn,
    HouseholdOut,
    HouseholdSummaryOut,
    WeightsOut,
)
from wedding.modules.guests.application.dto import (
    GuestDto,
    GuestListDto,
    GuestStatusChangeDto,
    HouseholdDto,
    SettingsDto,
)
from wedding.modules.guests.application.fields import GuestFields, HouseholdFields
from wedding.modules.guests.domain.headcount import BandCounts, Headcount


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
            "suggested_band": dto.suggested_band,
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


def _band_counts(counts: BandCounts) -> BandCountsOut:
    return BandCountsOut.model_validate(
        {
            "adults": counts.adults,
            "paying_children": counts.paying_children,
            "exempt_children": counts.exempt_children,
            "total": counts.total,
        }
    )


def _headcount(headcount: Headcount) -> HeadcountOut:
    return HeadcountOut.model_validate(
        {
            "total_nominal": _band_counts(headcount.total_nominal),
            "confirmed": _band_counts(headcount.confirmed),
            "not_attending": _band_counts(headcount.not_attending),
            "certain_or_confirmed": _band_counts(headcount.certain_or_confirmed),
            "weighted_adults_hundredths": headcount.weighted_adults_hundredths,
            "weighted_paying_children_hundredths": headcount.weighted_paying_children_hundredths,
            "weighted_rounded_up": headcount.weighted_rounded_up,
        }
    )


def _settings(dto: SettingsDto) -> GuestSettingsOut:
    weights = dto.weights
    return GuestSettingsOut.model_validate(
        {
            "weights": WeightsOut.model_validate(
                {
                    "certain_pct": weights.certain_pct,
                    "probable_pct": weights.probable_pct,
                    "phase_2_pct": weights.phase_2_pct,
                }
            )
            if weights
            else None,
            "exempt_until_age": dto.age_limits.exempt_until,
            "paying_until_age": dto.age_limits.paying_until,
            "version": dto.version,
        }
    )


def to_guest_list_out(dto: GuestListDto) -> GuestListOut:
    return GuestListOut.model_validate(
        {
            "households": [_household(h) for h in dto.households],
            "headcount": _headcount(dto.headcount),
            "settings": _settings(dto.settings),
        }
    )


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
