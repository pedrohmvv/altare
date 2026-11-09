from datetime import date
from typing import NamedTuple
from uuid import UUID

from wedding.modules.schedule.domain.entities import Task
from wedding.modules.schedule.domain.values import TaskState


class TaskDeadline(NamedTuple):
    overdue: bool
    days_left: int | None


def task_deadline(target_date: date | None, done: bool, today: date) -> TaskDeadline:
    """A mesma regra do prazo do marco (`derive`), para a avulsa, que nunca passa por ela (entraria
    em "libera" e nos bloqueios): vencida e não concluída é `Atrasada`; `days_left` é de hoje ao
    prazo (negativo é passado, 0 é hoje) e nulo se a avulsa está concluída ou sem prazo."""
    if target_date is None or done:
        return TaskDeadline(False, None)
    days_left = (target_date - today).days
    return TaskDeadline(days_left < 0, days_left)


def task_order_key(task: Task) -> tuple[bool, bool, date, str, UUID]:
    """A ordem da lista de avulsas: concluídas por último, sem prazo por último, prazo, título e id
    (o id só desempata, para a ordem ser sempre a mesma)."""
    return (
        task.state is TaskState.DONE,
        task.target_date is None,
        task.target_date or date.min,
        task.title,
        task.id,
    )
