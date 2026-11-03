"""A única superfície do módulo `wedding` que outros módulos podem importar (`architecture.md` §4).

O cronograma (Bloco 1.3) lê daqui, por portas que o `bootstrap` liga e nunca copiando: o status e a
visibilidade de cada categoria do Mapa de Escopo (`GetScopeStandings`) e a data do casamento
(`GetWeddingDate`: o status, a forma exata ou janela e o dia exato). Mudar estes campos é mudar um
contrato e pede uma decisão `D-xxx`.
"""

from wedding.modules.wedding.application.dto import WeddingDateDto as WeddingDate
from wedding.modules.wedding.application.queries.get_scope_standings import GetScopeStandings
from wedding.modules.wedding.application.queries.get_wedding_date import GetWeddingDate
from wedding.modules.wedding.application.scope_dto import CategoryStandingDto as CategoryStanding
from wedding.modules.wedding.domain.scope_values import ScopeStatus
from wedding.modules.wedding.domain.value_objects import DateKind, DefinitionStatus

__all__ = [
    "CategoryStanding",
    "DateKind",
    "DefinitionStatus",
    "GetScopeStandings",
    "GetWeddingDate",
    "ScopeStatus",
    "WeddingDate",
]
