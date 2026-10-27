from datetime import UTC, datetime, timedelta

import pytest


class FixedClock:
    """Relógio de teste: o instante só muda quando o teste pede."""

    def __init__(self, now: datetime) -> None:
        self._now = now

    def now(self) -> datetime:
        return self._now

    def advance(self, **delta: float) -> None:
        self._now += timedelta(**delta)


@pytest.fixture
def clock() -> FixedClock:
    return FixedClock(datetime(2026, 10, 27, 12, 0, tzinfo=UTC))
