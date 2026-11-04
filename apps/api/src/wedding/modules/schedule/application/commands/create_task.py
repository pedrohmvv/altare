from dataclasses import dataclass
from datetime import date

from wedding.modules.schedule.application.dto import ScheduleDto
from wedding.modules.schedule.application.ports import ScheduleUnitOfWorkFactory
from wedding.modules.schedule.application.schedule_map import ScheduleReader
from wedding.modules.schedule.domain.entities import Task
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.ids import IdGenerator
from wedding.shared_kernel.profile import ProfileKind


@dataclass(frozen=True)
class CreateTaskCommand:
    title: str
    # `None` é "quem criou": o perfil da sessão, decidido aqui e nunca no cliente.
    responsible: ProfileKind | None
    note: str | None
    target_date: date | None


class CreateTask:
    def __init__(
        self, uow_factory: ScheduleUnitOfWorkFactory, ids: IdGenerator, reader: ScheduleReader
    ) -> None:
        self._uow_factory = uow_factory
        self._ids = ids
        self._reader = reader

    def execute(self, command: CreateTaskCommand, actor: Actor) -> ScheduleDto:
        """Cria uma tarefa avulsa `A fazer` (F-CRN-06). Sem responsável, é de quem criou (o perfil
        da sessão: `Noivo` ou `Noiva`, nunca `Ambos` por padrão); `Ambos` só se vier pedido."""
        with self._uow_factory(actor) as uow:
            uow.schedule.add_task(
                Task(
                    id=self._ids.new_id(),
                    title=command.title,
                    responsible=command.responsible or actor.profile,
                    note=command.note,
                    target_date=command.target_date,
                )
            )
            uow.commit()
            return self._reader.read(uow.schedule, actor)
