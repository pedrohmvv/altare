from dataclasses import dataclass

from wedding.modules.guests.application.dto import GuestListDto
from wedding.modules.guests.application.fields import GuestFields, HouseholdFields
from wedding.modules.guests.application.list_map import build_guest_list
from wedding.modules.guests.application.new_guest import build_guest
from wedding.modules.guests.application.ports import GuestsUnitOfWorkFactory
from wedding.modules.guests.domain.entities import Household
from wedding.modules.guests.domain.errors import DuplicateHouseholdName
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.ids import IdGenerator


@dataclass(frozen=True)
class CreateHouseholdCommand:
    household: HouseholdFields
    first_guest: GuestFields


class CreateHousehold:
    def __init__(self, uow_factory: GuestsUnitOfWorkFactory, ids: IdGenerator) -> None:
        self._uow_factory = uow_factory
        self._ids = ids

    def execute(self, command: CreateHouseholdCommand, actor: Actor) -> GuestListDto:
        """O núcleo nasce já com a primeira pessoa e nunca fica vazio (F-CNV-01, `D-071`). Nome
        repetido entre os núcleos vivos é recusado, sem diferenciar caixa nem espaços."""
        fields = command.household
        with self._uow_factory(actor) as uow:
            household = Household(
                id=self._ids.new_id(),
                name=fields.name,
                side=fields.side,
                street=fields.street,
                number=fields.number,
                complement=fields.complement,
                district=fields.district,
                city=fields.city,
                state=fields.state,
                postal_code=fields.postal_code,
                note=fields.note,
            )
            first = build_guest(self._ids.new_id(), household.id, 0, command.first_guest)
            if uow.guests.household_name_taken(household.name_key):
                raise DuplicateHouseholdName()
            uow.guests.add_household(household)
            uow.guests.add_guest(first)
            uow.commit()
            return build_guest_list(uow.guests)
