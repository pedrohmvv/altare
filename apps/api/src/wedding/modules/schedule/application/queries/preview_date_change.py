from dataclasses import dataclass
from datetime import date
from uuid import UUID

from wedding.modules.schedule.application.dto import (
    DateChangeDto,
    DateMode,
    DatePreviewDto,
    DateRangeDto,
)
from wedding.modules.schedule.application.ports import ScheduleUnitOfWorkFactory
from wedding.modules.schedule.application.schedule_map import ScheduleReader
from wedding.modules.schedule.domain.derivation import Derived, MilestoneFacts, derive
from wedding.modules.schedule.domain.errors import InvalidPreviewDate
from wedding.modules.schedule.domain.values import MAX_YEAR, MIN_YEAR, ManualState
from wedding.shared_kernel.actor import Actor


@dataclass(frozen=True)
class PreviewDateChangeCommand:
    # A data exata que o casamento passaria a ter, já `Definida`; `None` é o cenário Sem Data.
    exact: date | None


class PreviewDateChange:
    def __init__(self, uow_factory: ScheduleUnitOfWorkFactory, reader: ScheduleReader) -> None:
        self._uow_factory = uow_factory
        self._reader = reader

    def execute(self, command: PreviewDateChangeCommand, actor: Actor) -> DatePreviewDto:
        """O que mudaria no cronograma se a data do casamento fosse outra (F-CRN-05, regra 4), sem
        gravar nada: deriva o cronograma com a data de hoje e com a hipotética e compara. Só os
        marcos ativos e não concluídos entram. A data hipotética tem o mesmo limite de ano do prazo
        (2000 a 2100, `invalid_preview_date`); a atual não é validada aqui."""
        if command.exact is not None and not MIN_YEAR <= command.exact.year <= MAX_YEAR:
            raise InvalidPreviewDate()
        with self._uow_factory(actor) as uow:
            facts = self._reader.facts(uow.schedule, actor)
            titles = {item.id: item.title for item in uow.schedule.list_milestones()}
            return _preview(
                facts,
                titles,
                self._reader.today(),
                current=self._reader.exact_wedding_date(actor),
                hypothetical=command.exact,
            )


def _range(derived: Derived) -> DateRangeDto | None:
    if derived.window_start is None or derived.window_end is None:
        return None
    return DateRangeDto(derived.window_start, derived.window_end)


def _mode(exact: date | None) -> DateMode:
    return DateMode.NO_DATE if exact is None else DateMode.WITH_DATE


def _preview(
    facts: list[MilestoneFacts],
    titles: dict[UUID, str],
    today: date,
    *,
    current: date | None,
    hypothetical: date | None,
) -> DatePreviewDto:
    before = derive(facts, today, current)
    after = derive(facts, today, hypothetical)
    changes: list[DateChangeDto] = []
    manual_kept = newly_overdue = 0
    for item in facts:
        now, then = before[item.id], after[item.id]
        if now.archived or item.manual_state is ManualState.DONE:
            continue
        newly_overdue += then.overdue and not now.overdue
        if item.window is None:
            continue
        if item.target_date is not None:
            manual_kept += 1
        elif _range(now) != _range(then):
            changes.append(
                DateChangeDto(
                    id=item.id,
                    title=titles[item.id],
                    window_before=_range(now),
                    window_after=_range(then),
                    target_before=now.effective_target,
                    target_after=then.effective_target,
                )
            )
    return DatePreviewDto(
        mode_before=_mode(current),
        mode_after=_mode(hypothetical),
        changes=tuple(changes),
        manual_kept=manual_kept,
        newly_overdue=newly_overdue,
    )
