from wedding.modules.schedule.application.dto import ScheduleDto
from wedding.modules.schedule.application.ports import ScheduleUnitOfWorkFactory
from wedding.modules.schedule.application.schedule_map import ScheduleReader
from wedding.shared_kernel.actor import Actor


class ReadSchedule:
    def __init__(self, uow_factory: ScheduleUnitOfWorkFactory, reader: ScheduleReader) -> None:
        self._uow_factory = uow_factory
        self._reader = reader

    def execute(self, actor: Actor) -> ScheduleDto:
        with self._uow_factory(actor) as uow:
            return self._reader.read(uow.schedule, actor)
