from wedding.modules.guests.application.ports import GuestsUnitOfWorkFactory
from wedding.modules.guests.domain.headcount import GuestFacts, Headcount, compute_headcount
from wedding.shared_kernel.actor import Actor


class GetGuestHeadcount:
    """O contrato de contagem que outros módulos leem sem copiar (`D-071`, item 5): é a mesma conta
    da lista, feita na hora da leitura, e nunca fica gravada em outro lugar."""

    def __init__(self, uow_factory: GuestsUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    def execute(self, actor: Actor) -> Headcount:
        with self._uow_factory(actor) as uow:
            facts = (GuestFacts(g.band, g.probability, g.status) for g in uow.guests.list_guests())
            return compute_headcount(facts, uow.guests.get_settings().weights)
