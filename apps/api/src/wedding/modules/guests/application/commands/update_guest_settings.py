from dataclasses import dataclass

from wedding.modules.guests.application.dto import GuestListDto
from wedding.modules.guests.application.list_map import build_guest_list
from wedding.modules.guests.application.ports import GuestsUnitOfWorkFactory
from wedding.modules.guests.domain.age import AgeLimits
from wedding.modules.guests.domain.headcount import Weights
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.errors import VersionConflict


@dataclass(frozen=True)
class WeightsCommand:
    certain_pct: int
    probable_pct: int
    phase_2_pct: int


@dataclass(frozen=True)
class UpdateGuestSettingsCommand:
    version: int
    weights: WeightsCommand | None
    exempt_until_age: int | None
    paying_until_age: int | None


class UpdateGuestSettings:
    def __init__(self, uow_factory: GuestsUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    def execute(self, command: UpdateGuestSettingsCommand, actor: Actor) -> GuestListDto:
        """Os pesos por probabilidade e os limites de idade são decisões do casal, vazias no
        início (`D-030`). Os três pesos andam juntos, e mudar qualquer coisa aqui não toca em
        nenhuma pessoa: o ponderado e a sugestão de faixa são derivados na leitura."""
        weights = (
            Weights(
                command.weights.certain_pct,
                command.weights.probable_pct,
                command.weights.phase_2_pct,
            )
            if command.weights
            else None
        )
        limits = AgeLimits(command.exempt_until_age, command.paying_until_age)
        with self._uow_factory(actor) as uow:
            settings = uow.guests.get_settings()
            if settings.version != command.version:
                raise VersionConflict()
            if settings.update(weights, limits):
                uow.commit()
            return build_guest_list(uow.guests)
