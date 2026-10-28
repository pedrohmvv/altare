from uuid import UUID

from wedding.modules.guests.application.fields import GuestFields
from wedding.modules.guests.domain.entities import Guest


def build_guest(
    guest_id: UUID,
    household_id: UUID,
    position: int,
    fields: GuestFields,
    *,
    companion_of_id: UUID | None = None,
) -> Guest:
    """Monta a pessoa a partir do formulário; o domínio valida tudo no construtor."""
    return Guest(
        id=guest_id,
        household_id=household_id,
        position=position,
        name=fields.name,
        band=fields.band,
        age=fields.age,
        probability=fields.probability,
        dietary_restriction=fields.dietary_restriction,
        note=fields.note,
        phone=fields.phone,
        email=fields.email,
        companion_of_id=companion_of_id,
    )
