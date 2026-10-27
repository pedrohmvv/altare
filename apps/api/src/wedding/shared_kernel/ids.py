import uuid
from typing import Protocol
from uuid import UUID


class IdGenerator(Protocol):
    def new_id(self) -> UUID: ...


def new_id() -> UUID:
    """UUID v7 quando a biblioteca padrão o oferece; senão v4 (stack.md §4, regra 5)."""
    uuid7 = getattr(uuid, "uuid7", None)
    return uuid7() if uuid7 else uuid.uuid4()


class UuidGenerator:
    def new_id(self) -> UUID:
        return new_id()
