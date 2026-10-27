from datetime import datetime
from threading import Lock

from wedding.modules.identity.domain.rules import LOGIN_WINDOW


class InMemoryLoginAttempts:
    """Falhas de login em memória: vale para um processo só (D-059; persistência no deploy).

    As rotas síncronas rodam em threads, daí o `Lock`; cada gravação varre as chaves vencidas,
    para tentativas com usuários aleatórios não encherem a memória.
    """

    def __init__(self) -> None:
        self._lock = Lock()
        self._failures: dict[str, list[datetime]] = {}

    def failures(self, key: str, since: datetime) -> list[datetime]:
        with self._lock:
            return [at for at in self._failures.get(key, []) if at >= since]

    def add_failure(self, key: str, at: datetime) -> None:
        with self._lock:
            self._failures.setdefault(key, []).append(at)
            self._sweep(now=at)

    def clear(self, key: str) -> None:
        with self._lock:
            self._failures.pop(key, None)

    def _sweep(self, now: datetime) -> None:
        horizon = now - LOGIN_WINDOW
        for key in list(self._failures):
            kept = [at for at in self._failures[key] if at > horizon]
            if kept:
                self._failures[key] = kept
            else:
                del self._failures[key]
