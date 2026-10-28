import datetime as dt
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from wedding.modules.wedding.domain.scope_rules import AlignmentState
from wedding.modules.wedding.domain.scope_values import Origin, Priority, ScopeStatus
from wedding.shared_kernel.profile import ProfileKind

LoginProfile = Literal[ProfileKind.NOIVO, ProfileKind.NOIVA]
_VERSION = Field(ge=1, description="A versão que a tela viu; divergir dá 409.")


# Entrada: nenhum campo de autoria nem de perfil; os dois vêm sempre da sessão.
class GroupCreateIn(BaseModel):
    name: str


class GroupRenameIn(BaseModel):
    name: str
    version: int = _VERSION


class VisibilityIn(BaseModel):
    hidden: bool
    version: int = _VERSION


class CategoryCreateIn(BaseModel):
    group_id: UUID
    name: str
    estimate_cents: int | None = None


class CategoryUpdateIn(BaseModel):
    name: str
    group_id: UUID
    estimate_cents: int | None = None
    version: int = _VERSION


class StatusIn(BaseModel):
    status: ScopeStatus
    reason: str | None = None
    version: int = _VERSION


class EvaluationIn(BaseModel):
    priority: Priority | None = None
    note: str | None = None
    version: int = _VERSION


# Saída: nenhum valor padrão, para o contrato declarar todos os campos como obrigatórios.
class EvaluationOut(BaseModel):
    priority: Priority | None
    note: str | None
    version: int


class AlignmentOut(BaseModel):
    state: AlignmentState
    missing: list[LoginProfile]


class CategoryOut(BaseModel):
    id: UUID
    group_id: UUID
    name: str
    position: int
    origin: Origin
    hidden: bool
    visible: bool
    status: ScopeStatus
    estimate_cents: int | None
    discard_reason: str | None
    noivo: EvaluationOut
    noiva: EvaluationOut
    alignment: AlignmentOut
    can_delete: bool
    version: int


class GroupOut(BaseModel):
    id: UUID
    name: str
    position: int
    origin: Origin
    hidden: bool
    can_delete: bool
    version: int
    categories: list[CategoryOut]


class ProgressOut(BaseModel):
    classified: int
    total: int


class TotalsOut(BaseModel):
    essential_cents: int
    essential_without_estimate: int
    maybe_cents: int
    maybe_without_estimate: int


class ScopeMapOut(BaseModel):
    groups: list[GroupOut]
    progress: ProgressOut
    totals: TotalsOut


class StatusChangeOut(BaseModel):
    id: UUID
    from_status: ScopeStatus
    to_status: ScopeStatus
    reason: str | None
    by: LoginProfile
    at: dt.datetime
