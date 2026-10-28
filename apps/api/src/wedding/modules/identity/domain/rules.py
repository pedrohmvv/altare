import math
from datetime import datetime, timedelta

from wedding.modules.identity.domain.entities import UserSession

INACTIVITY_LIMIT = timedelta(days=30)
ABSOLUTE_LIMIT = timedelta(days=90)
TOUCH_INTERVAL = timedelta(hours=1)
LOGIN_MAX_FAILURES = 5
LOGIN_WINDOW = timedelta(minutes=15)


def session_expired(session: UserSession, now: datetime) -> bool:
    return (
        now - session.last_seen_at >= INACTIVITY_LIMIT or now - session.created_at >= ABSOLUTE_LIMIT
    )


def should_touch(session: UserSession, now: datetime) -> bool:
    """Renovar o uso a cada requisição gravaria sem necessidade: no máximo uma vez por hora."""
    return now - session.last_seen_at >= TOUCH_INTERVAL


def login_retry_after(failures: list[datetime], now: datetime) -> int | None:
    """Segundos até poder tentar de novo, ou `None` se o login não está bloqueado.

    Bloqueia com 5 falhas dentro da janela de 15 minutos; libera quando a falha que mantém a
    contagem em 5 sai da janela.
    """
    recent = sorted(at for at in failures if now - at < LOGIN_WINDOW)
    if len(recent) < LOGIN_MAX_FAILURES:
        return None
    unblocks_at = recent[len(recent) - LOGIN_MAX_FAILURES] + LOGIN_WINDOW
    return math.ceil((unblocks_at - now).total_seconds())
