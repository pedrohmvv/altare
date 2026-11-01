from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from wedding.modules.wedding.domain.entities import BaselineField
from wedding.modules.wedding.domain.value_objects import (
    VALUE_TYPES,
    BaselineKey,
    BaselineValue,
    CeilingValue,
    CeremonyValue,
    DateValue,
    DefinitionStatus,
    SizeValue,
    TextValue,
)
from wedding.shared_kernel.profile import ProfileKind


@dataclass(frozen=True)
class BaselineFieldDto[V: BaselineValue]:
    status: DefinitionStatus
    value: V | None
    note: str | None
    version: int


@dataclass(frozen=True)
class BaselineDto:
    date: BaselineFieldDto[DateValue]
    city: BaselineFieldDto[TextValue]
    format: BaselineFieldDto[TextValue]
    size: BaselineFieldDto[SizeValue]
    ceiling: BaselineFieldDto[CeilingValue]
    ceremony: BaselineFieldDto[CeremonyValue]
    # Derivado da lista de convidados na hora de ler; a linha `size` nunca o guarda.
    guest_count: int


@dataclass(frozen=True)
class FieldSnapshotDto:
    status: DefinitionStatus
    value: BaselineValue | None
    note: str | None


@dataclass(frozen=True)
class BaselineChangeDto:
    id: UUID
    key: BaselineKey
    before: FieldSnapshotDto
    after: FieldSnapshotDto
    profile: ProfileKind
    changed_at: datetime


def to_snapshot_dto(key: BaselineKey, snapshot: dict[str, Any]) -> FieldSnapshotDto:
    raw = snapshot["value"]
    return FieldSnapshotDto(
        status=DefinitionStatus(snapshot["status"]),
        value=VALUE_TYPES[key].from_json(raw) if raw is not None else None,
        note=snapshot["note"],
    )


def _field_dto[V: BaselineValue](
    field: BaselineField, parse: Callable[[dict[str, Any]], V]
) -> BaselineFieldDto[V]:
    return BaselineFieldDto(
        status=field.status,
        value=parse(field.value) if field.value is not None else None,
        note=field.note,
        version=field.version,
    )


def to_baseline_dto(fields: Iterable[BaselineField], guest_count: int) -> BaselineDto:
    by_key = {field.key: field for field in fields}
    missing = set(BaselineKey) - by_key.keys()
    if missing:
        # A semente vem da migration: faltar linha é um banco mal migrado, não um erro de uso.
        raise RuntimeError("Definições Base sem semente; rode `make migrate`")
    return BaselineDto(
        date=_field_dto(by_key[BaselineKey.DATE], DateValue.from_json),
        city=_field_dto(by_key[BaselineKey.CITY], TextValue.from_json),
        format=_field_dto(by_key[BaselineKey.FORMAT], TextValue.from_json),
        size=_field_dto(by_key[BaselineKey.SIZE], SizeValue.from_json),
        ceiling=_field_dto(by_key[BaselineKey.CEILING], CeilingValue.from_json),
        ceremony=_field_dto(by_key[BaselineKey.CEREMONY], CeremonyValue.from_json),
        guest_count=guest_count,
    )
