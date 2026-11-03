from datetime import date, timedelta, timezone

from wedding.shared_kernel.clock import Clock

# O Brasil não tem horário de verão desde 2019: Brasília é UTC-3 o ano todo, e o prazo é um dia,
# não um instante. Fixar o deslocamento evita depender do banco de fusos do sistema (como o
# `guests`; na terceira ocorrência a função sobe para o `shared_kernel`).
BRASILIA = timezone(timedelta(hours=-3))


def today_in_brazil(clock: Clock) -> date:
    return clock.now().astimezone(BRASILIA).date()
