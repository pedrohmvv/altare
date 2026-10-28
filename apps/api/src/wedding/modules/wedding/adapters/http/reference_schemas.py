import datetime as dt
from uuid import UUID

from pydantic import BaseModel

from wedding.modules.wedding.adapters.http.scope_schemas import LoginProfile
from wedding.modules.wedding.domain.reference import ReferenceKind


# Entrada: nenhum campo de autoria; o perfil de quem adiciona vem sempre da sessão.
class LinkReferenceIn(BaseModel):
    url: str
    title: str | None = None
    comment: str | None = None


class ImageReferenceIn(BaseModel):
    file_id: UUID
    title: str | None = None
    comment: str | None = None


# Saída: nenhum valor padrão, para o contrato declarar todos os campos como obrigatórios.
class ReferenceOut(BaseModel):
    id: UUID
    kind: ReferenceKind
    url: str | None
    domain: str | None
    file_id: UUID | None
    title: str | None
    comment: str | None
    by: LoginProfile
    at: dt.datetime
    can_remove: bool
