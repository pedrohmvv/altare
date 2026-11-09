import re
import unicodedata
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
_HOST_ASCII = re.compile(r"[a-z0-9.-]+")
_UNSAFE_CATEGORIES = ("Cc", "Cf")


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
    com um domínio de verdade. Recusa a barra invertida e os caracteres de controle e de formato na
    URL inteira, e o host (em ASCII; o IDN vira punycode) só tem letras, dígitos, ponto e hífen: o
    domínio mostrado é o indicador de confiança e não pode diferir do que o navegador abre. O
    conteúdo da página nunca é lido (sem *scraping*)."""
    url = raw.strip()
    if not url or len(url) > MAX_URL or any(_is_unsafe(char) for char in url):
        raise InvalidReferenceUrl()
    try:
        parts = urlsplit(url)
        host = parts.hostname
        has_credentials = parts.username is not None or parts.password is not None
    except ValueError as error:
        raise InvalidReferenceUrl() from error
    if parts.scheme.lower() not in _SCHEMES or not host or has_credentials:
        raise InvalidReferenceUrl()
    ascii_host = _ascii_host(host)
    netloc = parts.netloc.lower()
    if ascii_host is None or not netloc.startswith(host) or not _is_domain(ascii_host):
        raise InvalidReferenceUrl()
    # O que sobra do host no `netloc` é a porta, que segue como veio.
    normalized = parts._replace(
        scheme=parts.scheme.lower(), netloc=ascii_host + netloc.removeprefix(host)
    )
    return ParsedLink(url=normalized.geturl(), domain=ascii_host.removeprefix("www."))


def _is_unsafe(char: str) -> bool:
    """Espaço, controle (Cc), formato (Cf, como bidi e largura zero) e a barra invertida, que o
    navegador lê como `/` e faz o domínio mostrado mentir."""
    return char == "\\" or char.isspace() or unicodedata.category(char) in _UNSAFE_CATEGORIES


def _ascii_host(host: str) -> str | None:
    """O host em ASCII: o IDN vira punycode, e o que não codifica não é endereço."""
    if host.isascii():
        return host
    try:
        return host.encode("idna").decode("ascii")
    except UnicodeError:
        return None


def _is_domain(host: str) -> bool:
    return "." in host and _HOST_ASCII.fullmatch(host) is not None


def display_domain(url: str) -> str | None:
    """O domínio que a tela mostra, derivado do endereço guardado. **Total: nunca levanta.** Uma
    referência gravada antes de uma regra mais apertada de `parse_link` não pode derrubar a
    listagem: mostra o que der (o host cru, sem controle nem o que vem depois de `\\`) ou nada.
    Mesma lógica do `display_domain` do `schedule` (cópia: um módulo não importa o outro)."""
    try:
        return parse_link(url).domain
    except InvalidReferenceUrl:
        pass
    try:
        host = urlsplit(url).hostname
    except ValueError:
        return None
    visible = "".join(char for char in (host or "").split("\\")[0] if not _is_unsafe(char))
    return visible.removeprefix("www.") or None


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
        return display_domain(self.url) if self.url else None

    def remove(self, by_profile: ProfileKind, by_user: UUID | None, now: datetime) -> None:
        if by_profile is not self.profile:
            raise Forbidden()
        self.deleted_at, self.deleted_by = now, by_user
