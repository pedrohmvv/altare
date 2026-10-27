from dataclasses import dataclass

type Cents = int


@dataclass(frozen=True, slots=True, order=True)
class Money:
    """Dinheiro em centavos inteiros; nunca float (stack.md §4)."""

    cents: Cents

    def __post_init__(self) -> None:
        if type(self.cents) is not int:
            raise TypeError("Money exige centavos inteiros")

    def __add__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        return Money(self.cents + other.cents)

    def __sub__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        return Money(self.cents - other.cents)

    def __mul__(self, factor: int) -> "Money":
        if type(factor) is not int:
            return NotImplemented
        return Money(self.cents * factor)

    __rmul__ = __mul__

    def __neg__(self) -> "Money":
        return Money(-self.cents)

    def split(self, parts: int) -> tuple["Money", ...]:
        """Parcelas iguais, arredondadas para baixo; o resto vai para a última."""
        if parts < 1:
            raise ValueError("A divisão exige ao menos uma parcela")
        if self.cents < 0:
            raise ValueError("A divisão não aceita valor negativo")
        base, remainder = divmod(self.cents, parts)
        return (*(Money(base) for _ in range(parts - 1)), Money(base + remainder))
