from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from typing import Any, Self

from wedding.modules.wedding.domain.errors import InvalidBaselineValue

MIN_YEAR = 2000
MAX_YEAR = 2100
MAX_LABEL = 60
MAX_TEXT = 80
MAX_GUESTS = 10_000
MAX_CEILING_CENTS = 10**12
MAX_DETAIL = 200


class BaselineKey(StrEnum):
    DATE = "date"
    CITY = "city"
    FORMAT = "format"
    SIZE = "size"
    CEILING = "ceiling"
    CEREMONY = "ceremony"


class DefinitionStatus(StrEnum):
    IN_DEFINITION = "Em definição"
    DEFINED = "Definido"


class DateKind(StrEnum):
    NONE = "nenhuma"
    WINDOW = "janela"
    EXACT = "exata"


class CeremonyKind(StrEnum):
    RELIGIOUS = "Religiosa"
    CIVIL = "Civil"
    SYMBOLIC = "Simbólica"


def _is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _clean_optional(text: str | None, limit: int) -> str | None:
    """Apara o texto; em branco vira ausência. Passar do limite é erro, não corte silencioso."""
    cleaned = (text or "").strip()
    if len(cleaned) > limit:
        raise InvalidBaselineValue()
    return cleaned or None


@dataclass(frozen=True)
class MonthYear:
    year: int
    month: int

    def __post_init__(self) -> None:
        if not (_is_int(self.year) and _is_int(self.month)):
            raise InvalidBaselineValue()
        if not MIN_YEAR <= self.year <= MAX_YEAR or not 1 <= self.month <= 12:
            raise InvalidBaselineValue()

    def to_json(self) -> dict[str, int]:
        return {"year": self.year, "month": self.month}

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> Self:
        return cls(year=raw["year"], month=raw["month"])


@dataclass(frozen=True)
class DateValue:
    """Janela (mês e ano, início e fim) ou data exata. "Nenhuma" não é um valor: é o campo vazio."""

    kind: DateKind
    window_start: MonthYear | None = None
    window_end: MonthYear | None = None
    label: str | None = None
    exact: date | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "label", _clean_optional(self.label, MAX_LABEL))
        match self.kind:
            case DateKind.WINDOW:
                if self.exact is not None or self.window_start is None or self.window_end is None:
                    raise InvalidBaselineValue()
                if (self.window_end.year, self.window_end.month) < (
                    self.window_start.year,
                    self.window_start.month,
                ):
                    raise InvalidBaselineValue()
            case DateKind.EXACT:
                if self.exact is None or self.window_start or self.window_end or self.label:
                    raise InvalidBaselineValue()
            case DateKind.NONE:
                raise InvalidBaselineValue()

    def to_json(self) -> dict[str, Any]:
        if self.kind is DateKind.EXACT and self.exact is not None:
            return {"kind": self.kind.value, "exact": self.exact.isoformat()}
        assert self.window_start is not None
        assert self.window_end is not None
        return {
            "kind": self.kind.value,
            "window_start": self.window_start.to_json(),
            "window_end": self.window_end.to_json(),
            "label": self.label,
        }

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> Self:
        if raw["kind"] == DateKind.EXACT:
            return cls(kind=DateKind.EXACT, exact=date.fromisoformat(raw["exact"]))
        return cls(
            kind=DateKind.WINDOW,
            window_start=MonthYear.from_json(raw["window_start"]),
            window_end=MonthYear.from_json(raw["window_end"]),
            label=raw.get("label"),
        )


@dataclass(frozen=True)
class TextValue:
    """Texto curto e livre (cidade ou região, formato): nenhuma sugestão pré-carregada."""

    text: str

    def __post_init__(self) -> None:
        cleaned = _clean_optional(self.text, MAX_TEXT)
        if cleaned is None:
            raise InvalidBaselineValue()
        object.__setattr__(self, "text", cleaned)

    def to_json(self) -> dict[str, Any]:
        return {"text": self.text}

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> Self:
        return cls(raw["text"])


@dataclass(frozen=True)
class SizeValue:
    """Faixa de convidados que o casal imagina; não é a lista nominal (Bloco 1.2)."""

    minimum: int
    maximum: int

    def __post_init__(self) -> None:
        if not (_is_int(self.minimum) and _is_int(self.maximum)):
            raise InvalidBaselineValue()
        if not 1 <= self.minimum <= self.maximum <= MAX_GUESTS:
            raise InvalidBaselineValue()

    def to_json(self) -> dict[str, Any]:
        return {"minimum": self.minimum, "maximum": self.maximum}

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> Self:
        return cls(raw["minimum"], raw["maximum"])


@dataclass(frozen=True)
class CeilingValue:
    """Teto macro, em centavos (stack.md §4). Os tetos reais ficam nos cenários do Bloco 2.1."""

    cents: int

    def __post_init__(self) -> None:
        if not _is_int(self.cents) or not 0 < self.cents <= MAX_CEILING_CENTS:
            raise InvalidBaselineValue()

    def to_json(self) -> dict[str, Any]:
        return {"cents": self.cents}

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> Self:
        return cls(raw["cents"])


@dataclass(frozen=True)
class CeremonyValue:
    """Tipo de cerimônia: dado do casal, nunca presumido (D-026)."""

    kinds: frozenset[CeremonyKind]
    detail: str | None = None

    def __post_init__(self) -> None:
        if not self.kinds:
            raise InvalidBaselineValue()
        object.__setattr__(self, "detail", _clean_optional(self.detail, MAX_DETAIL))

    def to_json(self) -> dict[str, Any]:
        # Ordenado, para o mesmo valor dar sempre o mesmo JSON e a comparação não acusar mudança.
        return {"kinds": sorted(kind.value for kind in self.kinds), "detail": self.detail}

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> Self:
        return cls(
            kinds=frozenset(CeremonyKind(kind) for kind in raw["kinds"]), detail=raw.get("detail")
        )


BaselineValue = DateValue | TextValue | SizeValue | CeilingValue | CeremonyValue

VALUE_TYPES: dict[BaselineKey, type[BaselineValue]] = {
    BaselineKey.DATE: DateValue,
    BaselineKey.CITY: TextValue,
    BaselineKey.FORMAT: TextValue,
    BaselineKey.SIZE: SizeValue,
    BaselineKey.CEILING: CeilingValue,
    BaselineKey.CEREMONY: CeremonyValue,
}
