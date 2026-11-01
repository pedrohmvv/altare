from datetime import date, timedelta, timezone

from wedding.shared_kernel.clock import Clock

# O Brasil não tem horário de verão desde 2019: Brasília é UTC-3 o ano todo, e o convite é um dia,
# não um instante. Fixar o deslocamento evita depender do banco de fusos do sistema.
BRASILIA = timezone(timedelta(hours=-3))


def today_in_brazil(clock: Clock) -> date:
    return clock.now().astimezone(BRASILIA).date()
