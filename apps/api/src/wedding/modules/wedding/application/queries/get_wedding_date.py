from wedding.modules.wedding.application.dto import WeddingDateDto
from wedding.modules.wedding.application.ports import WeddingUnitOfWorkFactory
from wedding.modules.wedding.domain.entities import BaselineField
from wedding.modules.wedding.domain.value_objects import BaselineKey, DateValue
from wedding.shared_kernel.actor import Actor


class GetWeddingDate:
    """Leitura mínima para outro módulo (`application/public.py`): só a data do casamento, sem a
    contagem de convidados que o quadro inteiro das Definições Base pede."""

    def __init__(self, uow_factory: WeddingUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    def execute(self, actor: Actor) -> WeddingDateDto:
        with self._uow_factory(actor) as uow:
            field = uow.baseline.get(BaselineKey.DATE)
            if field is None:
                # A semente vem da migration: faltar linha é um banco mal migrado, não erro de uso.
                raise RuntimeError("Definições Base sem semente; rode `make migrate`")
            return _to_dto(field)


def _to_dto(field: BaselineField) -> WeddingDateDto:
    if field.value is None:
        return WeddingDateDto(field.status, None, None)
    value = DateValue.from_json(field.value)
    return WeddingDateDto(field.status, value.kind, value.exact)
