import calendar
from dataclasses import dataclass
from datetime import date, timedelta
from enum import StrEnum

from wedding.modules.schedule.domain.errors import InvalidMilestoneWindow

MAX_WINDOW_MONTHS = 120
MAX_WINDOW_WEEKS = 520


class WindowUnit(StrEnum):
    MONTHS = "meses"
    WEEKS = "semanas"


_MAX_BY_UNIT = {WindowUnit.MONTHS: MAX_WINDOW_MONTHS, WindowUnit.WEEKS: MAX_WINDOW_WEEKS}


@dataclass(frozen=True)
class Window:
    """A janela de um marco em deslocamentos antes da data do casamento (F-CRN-05): do início
    (`start_before`) ao fim (`end_before`), na unidade dada."""

    start_before: int
    end_before: int
    unit: WindowUnit


def subtract_months(day: date, months: int) -> date:
    """Meses respeitam o fim do mês: 31/05 menos 3 meses é 28/02 (ou 29/02 em ano bissexto)."""
    total = day.year * 12 + (day.month - 1) - months
    year, month_index = divmod(total, 12)
    month = month_index + 1
    return date(year, month, min(day.day, calendar.monthrange(year, month)[1]))


def subtract_weeks(day: date, weeks: int) -> date:
    return day - timedelta(days=7 * weeks)


def _subtract(day: date, amount: int, unit: WindowUnit) -> date:
    if unit is WindowUnit.MONTHS:
        return subtract_months(day, amount)
    return subtract_weeks(day, amount)


def window_dates(
    exact: date, start_before: int, end_before: int, unit: WindowUnit
) -> tuple[date, date] | None:
    """O início e o fim da janela para a data exata do casamento. A data não tem o ano validado
    no módulo `wedding`, então uma data que estoura o calendário (antes do ano 1) não calcula: a
    função é total e devolve `None`, em vez de derrubar a leitura do cronograma."""
    try:
        return _subtract(exact, start_before, unit), _subtract(exact, end_before, unit)
    except (ValueError, OverflowError):
        return None


def validate_window(start_before: int, end_before: int, unit: WindowUnit) -> None:
    """O início não vem depois do fim, nenhum deslocamento é negativo e há um teto por unidade
    (120 meses ou 520 semanas, dez anos). `0` e `0` vale: a janela é o dia do casamento."""
    if not 0 <= end_before <= start_before <= _MAX_BY_UNIT[unit]:
        raise InvalidMilestoneWindow()
