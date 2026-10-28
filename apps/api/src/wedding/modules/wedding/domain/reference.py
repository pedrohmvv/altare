from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Self
from urllib.parse import urlsplit
from uuid import UUID

from wedding.modules.wedding.domain.errors import InvalidReferenceUrl, InvalidScopeValue
from wedding.shared_kernel.errors import Forbidden
from wedding.shared_kernel.profile import ProfileKind

MAX_URL = 2000
MAX_TITLE = 120
MAX_COMMENT = 500
_SCHEMES = ("http", "https")


class ReferenceKind(StrEnum):
    LINK = "link"
    IMAGE = "imagem"


@dataclass(frozen=True)
class ParsedLink:
    url: str
    domain: str


def parse_link(raw: str) -> ParsedLink:
    """Valida um endereço colado (F-PLN-06). Só `http` e `https` valem (nada de `javascript:` nem
    `data:`, que virariam código ao abrir o link), sem espaços, sem usuário e senha no endereço e
    com um domínio de verdade. O conteúdo da página nunca é lido (sem *scraping*)."""
    url = raw.strip()
    if not url or len(url) > MAX_URL or any(char.isspace() or ord(char) < 32 for char in url):
        raise InvalidReferenceUrl()
    try:
        parts = urlsplit(url)
        host = parts.hostname
        has_credentials = parts.username is not None or parts.password is not None
    except ValueError as error:
        raise InvalidReferenceUrl() from error
    if parts.scheme.lower() not in _SCHEMES or not host or "." not in host or has_credentials:
        raise InvalidReferenceUrl()
    normalized = parts._replace(scheme=parts.scheme.lower(), netloc=parts.netloc.lower())
    return ParsedLink(url=normalized.geturl(), domain=host.lower().removeprefix("www."))


def _clean(text: str | None, limit: int) -> str | None:
    cleaned = (text or "").strip()
    if len(cleaned) > limit:
        raise InvalidScopeValue()
    return cleaned or None


@dataclass
class ScopeReference:
    """Uma inspiração guardada numa frente: um link ou uma imagem (F-PLN-06). O perfil de quem
    adicionou fica na linha (rótulo), e só ele remove a sua; a remoção é lógica."""

    id: UUID
    category_id: UUID
    kind: ReferenceKind
    profile: ProfileKind
    url: str | None = None
    file_id: UUID | None = None
    title: str | None = None
    comment: str | None = None
    deleted_at: datetime | None = None
    deleted_by: UUID | None = None
    version: int = 0
    # Instante em que foi adicionada; o histórico básico o grava ao salvar.
    created_at: datetime | None = None

    @classmethod
    def new_link(
        cls,
        *,
        id: UUID,
        category_id: UUID,
        profile: ProfileKind,
        url: str,
        title: str | None,
        comment: str | None,
    ) -> Self:
        return cls(
            id=id,
            category_id=category_id,
            kind=ReferenceKind.LINK,
            profile=profile,
            url=parse_link(url).url,
            title=_clean(title, MAX_TITLE),
            comment=_clean(comment, MAX_COMMENT),
        )

    @classmethod
    def new_image(
        cls,
        *,
        id: UUID,
        category_id: UUID,
        profile: ProfileKind,
        file_id: UUID,
        title: str | None,
        comment: str | None,
    ) -> Self:
        return cls(
            id=id,
            category_id=category_id,
            kind=ReferenceKind.IMAGE,
            profile=profile,
            file_id=file_id,
            title=_clean(title, MAX_TITLE),
            comment=_clean(comment, MAX_COMMENT),
        )

    @property
    def domain(self) -> str | None:
        return parse_link(self.url).domain if self.url else None

    def remove(self, by_profile: ProfileKind, by_user: UUID | None, now: datetime) -> None:
        if by_profile is not self.profile:
            raise Forbidden()
        self.deleted_at, self.deleted_by = now, by_user
