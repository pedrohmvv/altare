"""A única superfície do módulo `guests` que outros módulos podem importar (`architecture.md` §4).

O Orçamento (Bloco 2.1) lê a contagem por aqui, por uma porta que o `bootstrap` liga, e nunca a
guarda; o Porte das Definições Base (`wedding`) lê o Total Nominal do mesmo jeito. Os valores são
inteiros: pesos em percentual e o ponderado em centésimos de pessoa (100 = uma pessoa), para nenhum
`float` cruzar a fronteira. Mudar estes campos é mudar um contrato e pede uma decisão `D-xxx`.
"""

from wedding.modules.guests.application.queries.get_guest_headcount import GetGuestHeadcount
from wedding.modules.guests.domain.headcount import BandCounts
from wedding.modules.guests.domain.headcount import Headcount as GuestHeadcount

__all__ = ["BandCounts", "GetGuestHeadcount", "GuestHeadcount"]
