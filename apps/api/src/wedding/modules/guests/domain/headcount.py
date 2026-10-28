from collections.abc import Iterable
from dataclasses import dataclass

from wedding.modules.guests.domain.errors import InvalidWeights
from wedding.modules.guests.domain.values import AgeBand, GuestStatus, Probability

MAX_PERCENT = 100


@dataclass(frozen=True)
class Weights:
    """O peso de cada probabilidade no Estimado Ponderado, em percentual inteiro de 0 a 100
    (F-CNV-06). São uma decisão do casal: o Altare nunca presume nenhum valor."""

    certain_pct: int
    probable_pct: int
    phase_2_pct: int

    def __post_init__(self) -> None:
        for pct in (self.certain_pct, self.probable_pct, self.phase_2_pct):
            if isinstance(pct, bool) or not isinstance(pct, int) or not 0 <= pct <= MAX_PERCENT:
                raise InvalidWeights()

    def of(self, probability: Probability) -> int:
        return {
            Probability.CERTAIN: self.certain_pct,
            Probability.PROBABLE: self.probable_pct,
            Probability.PHASE_2: self.phase_2_pct,
        }[probability]


@dataclass(frozen=True)
class GuestFacts:
    """O que a contagem precisa saber de uma pessoa: nada de nome nem de contato."""

    band: AgeBand
    probability: Probability
    status: GuestStatus


@dataclass(frozen=True)
class BandCounts:
    adults: int = 0
    paying_children: int = 0
    exempt_children: int = 0

    @property
    def total(self) -> int:
        return self.adults + self.paying_children + self.exempt_children


@dataclass(frozen=True)
class Headcount:
    """Os contadores derivados da lista, nunca gravados (`architecture.md` §5). O ponderado é a soma
    dos pesos em centésimos de pessoa (100 = uma pessoa), exata e sem `float`; fica nulo enquanto os
    pesos não existem."""

    total_nominal: BandCounts
    confirmed: BandCounts
    not_attending: BandCounts
    certain_or_confirmed: BandCounts
    weighted_adults_hundredths: int | None
    weighted_paying_children_hundredths: int | None

    @property
    def weighted_rounded_up(self) -> int | None:
        """O número do cabeçalho do cenário: nunca subestima o custo (`D-032`, `F-ORC-03`)."""
        if (
            self.weighted_adults_hundredths is None
            or self.weighted_paying_children_hundredths is None
        ):
            return None
        hundredths = self.weighted_adults_hundredths + self.weighted_paying_children_hundredths
        return -(-hundredths // 100)


def _counts(facts: Iterable[GuestFacts]) -> BandCounts:
    adults = paying = exempt = 0
    for fact in facts:
        if fact.band is AgeBand.ADULT:
            adults += 1
        elif fact.band is AgeBand.PAYING_CHILD:
            paying += 1
        else:
            exempt += 1
    return BandCounts(adults, paying, exempt)


def compute_headcount(facts: Iterable[GuestFacts], weights: Weights | None) -> Headcount:
    """Total Nominal (todos, menos `Não irá`), Confirmados, Não irão, a base "só Certeza e
    Confirmados" e o Estimado Ponderado (F-CNV-06). Criança isenta e `Não irá` ficam fora do
    ponderado; quem está `Confirmado` conta 100%, qualquer que seja a probabilidade."""
    everyone = list(facts)
    attending = [f for f in everyone if f.status is not GuestStatus.DECLINED]
    weighted_adults: int | None = None
    weighted_children: int | None = None
    if weights is not None:
        weighted_adults = weighted_children = 0
        for fact in attending:
            if fact.band is AgeBand.EXEMPT_CHILD:
                continue
            pct = 100 if fact.status is GuestStatus.CONFIRMED else weights.of(fact.probability)
            if fact.band is AgeBand.ADULT:
                weighted_adults += pct
            else:
                weighted_children += pct
    return Headcount(
        total_nominal=_counts(attending),
        confirmed=_counts(f for f in attending if f.status is GuestStatus.CONFIRMED),
        not_attending=_counts(f for f in everyone if f.status is GuestStatus.DECLINED),
        certain_or_confirmed=_counts(
            f
            for f in attending
            if f.probability is Probability.CERTAIN or f.status is GuestStatus.CONFIRMED
        ),
        weighted_adults_hundredths=weighted_adults,
        weighted_paying_children_hundredths=weighted_children,
    )
