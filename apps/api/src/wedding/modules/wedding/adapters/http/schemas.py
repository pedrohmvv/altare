import datetime as dt
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from wedding.modules.wedding.domain.value_objects import (
    BaselineKey,
    CeremonyKind,
    DateKind,
    DefinitionStatus,
)
from wedding.shared_kernel.profile import ProfileKind


class MonthYearSchema(BaseModel):
    year: int
    month: int


class DateValueSchema(BaseModel):
    """`nenhuma` é o campo vazio: o domínio só guarda janela ou data exata."""

    kind: DateKind
    window_start: MonthYearSchema | None = None
    window_end: MonthYearSchema | None = None
    label: str | None = None
    exact: dt.date | None = None


class SizeValueSchema(BaseModel):
    minimum: int | None = None
    maximum: int | None = None


class CeilingValueSchema(BaseModel):
    cents: int | None = None


class CeremonyValueSchema(BaseModel):
    kinds: list[CeremonyKind] = Field(default_factory=list)
    detail: str | None = None


# Entrada: nenhum campo de autoria, que vem sempre da sessão (altare-backend-api).
class FieldIn(BaseModel):
    status: DefinitionStatus
    note: str | None = None
    version: int = Field(ge=1, description="A versão que a tela viu; divergir dá 409.")


class DateFieldIn(FieldIn):
    value: DateValueSchema


class TextFieldIn(FieldIn):
    value: str | None = None


class SizeFieldIn(FieldIn):
    value: SizeValueSchema


class CeilingFieldIn(FieldIn):
    value: CeilingValueSchema


class CeremonyFieldIn(FieldIn):
    value: CeremonyValueSchema


class FieldOut(BaseModel):
    status: DefinitionStatus
    note: str | None
    version: int


class DateFieldOut(FieldOut):
    value: DateValueSchema


class TextFieldOut(FieldOut):
    value: str | None


class SizeFieldOut(FieldOut):
    value: SizeValueSchema
    # Quantas pessoas a lista tem agora (Total Nominal): derivado, nunca gravado no Porte.
    guest_count: int


class CeilingFieldOut(FieldOut):
    value: CeilingValueSchema


class CeremonyFieldOut(FieldOut):
    value: CeremonyValueSchema


class BaselineOut(BaseModel):
    date: DateFieldOut
    city: TextFieldOut
    format: TextFieldOut
    size: SizeFieldOut
    ceiling: CeilingFieldOut
    ceremony: CeremonyFieldOut


class SnapshotOut(BaseModel):
    status: DefinitionStatus
    note: str | None
    value: DateValueSchema | SizeValueSchema | CeilingValueSchema | CeremonyValueSchema | str | None


class BaselineChangeOut(BaseModel):
    id: UUID
    field: BaselineKey
    before: SnapshotOut
    after: SnapshotOut
    by: Literal[ProfileKind.NOIVO, ProfileKind.NOIVA]
    at: dt.datetime
