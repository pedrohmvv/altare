"""O anexo de um marco ou de uma avulsa (F-CRN-08): um link ou um arquivo já enviado ao módulo
`files`, com título e comentário opcionais e o perfil de quem anexou.

`parse_link` é uma cópia de `wedding/domain/reference.py` (F-PLN-06): o `schedule` não importa outro
módulo, e as duas cópias levam o mesmo corpus de testes (inclusive a regra de `\\`, Cc, Cf e IDN).
Promover para o `shared_kernel` no terceiro uso (contatos)."""

import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from urllib.parse import urlsplit
from uuid import UUID

from wedding.modules.schedule.domain.errors import (
    AttachmentFileNotAllowed,
    InvalidAttachmentUrl,
    InvalidScheduleValue,
)
from wedding.modules.schedule.domain.values import OwnerKind
from wedding.shared_kernel.errors import Forbidden
from wedding.shared_kernel.profile import ProfileKind

MAX_URL = 2000
MAX_ATTACHMENT_TITLE = 120
MAX_ATTACHMENT_COMMENT = 500
_SCHEMES = ("http", "https")
_HOST_ASCII = re.compile(r"[a-z0-9.-]+")
_UNSAFE_CATEGORIES = ("Cc", "Cf")
_ATTACHABLE_TYPES = frozenset({"application/pdf", "image/jpeg", "image/png", "image/webp"})


class AttachmentKind(StrEnum):
    LINK = "link"
    FILE = "file"


@dataclass(frozen=True)
class ParsedLink:
    url: str
    domain: str


@dataclass(frozen=True)
class AttachedFile:
    """O que o anexo guarda do arquivo enviado: o id e a cópia do nome, do tipo e do tamanho no
    instante de anexar. É seguro copiar porque o arquivo enviado é imutável (`file_assets`)."""

    file_id: UUID
    name: str
    content_type: str
    size_bytes: int


def parse_link(raw: str) -> ParsedLink:
    """Valida um endereço colado. Só `http` e `https` valem (nada de `javascript:` nem `data:`, que
    virariam código ao abrir o link), sem espaços, sem usuário e senha no endereço e com um domínio
    de verdade. Recusa a barra invertida e os caracteres de controle e de formato na URL inteira, e
    o host (em ASCII; o IDN vira punycode) só tem letras, dígitos, ponto e hífen: o domínio mostrado
    é o indicador de confiança e não pode diferir do que o navegador abre. O domínio mostrado é
    derivado do endereço; o conteúdo da página nunca é lido."""
    url = raw.strip()
    if not url or len(url) > MAX_URL or any(_is_unsafe(char) for char in url):
        raise InvalidAttachmentUrl()
    try:
        parts = urlsplit(url)
        host = parts.hostname
        has_credentials = parts.username is not None or parts.password is not None
    except ValueError as error:
        raise InvalidAttachmentUrl() from error
    if parts.scheme.lower() not in _SCHEMES or not host or has_credentials:
        raise InvalidAttachmentUrl()
    ascii_host = _ascii_host(host)
    netloc = parts.netloc.lower()
    if ascii_host is None or not netloc.startswith(host) or not _is_domain(ascii_host):
        raise InvalidAttachmentUrl()
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
    linha gravada antes de uma regra mais apertada de `parse_link` não pode derrubar a leitura do
    cronograma inteiro: mostra o que der (o host cru, sem controle nem o que vem depois de `\\`) ou
    nada."""
    try:
        return parse_link(url).domain
    except InvalidAttachmentUrl:
        pass
    try:
        host = urlsplit(url).hostname
    except ValueError:
        return None
    visible = "".join(char for char in (host or "").split("\\")[0] if not _is_unsafe(char))
    return visible.removeprefix("www.") or None


def is_attachable_content_type(content_type: str) -> bool:
    """Só PDF, JPEG, PNG e WebP: a lista fechada que o módulo `files` aceita receber (`D-063`).
    Sem `image/*`: SVG, por exemplo, é imagem que executa script."""
    return content_type in _ATTACHABLE_TYPES


def _clean(text: str | None, limit: int) -> str | None:
    """Apara o texto; em branco vira ausência. Passar do limite é erro, não corte silencioso."""
    cleaned = (text or "").strip()
    if len(cleaned) > limit:
        raise InvalidScheduleValue()
    return cleaned or None


@dataclass
class Attachment:
    """Um anexo de um marco ou de uma avulsa: exatamente um link (`url`) ou um arquivo (`file_id`
    e a cópia de nome, tipo e tamanho). O dono vive em outra tabela e não é tocado: anexar e remover
    nunca mudam a `version` dele. A remoção é lógica, só do autor, e não tem volta pela tela.
    `created_at` é o instante em que foi anexado; o histórico básico o grava ao salvar."""

    id: UUID
    owner_kind: OwnerKind
    owner_id: UUID
    kind: AttachmentKind
    profile: ProfileKind
    url: str | None = None
    file_id: UUID | None = None
    file_name: str | None = None
    content_type: str | None = None
    size_bytes: int | None = None
    title: str | None = None
    comment: str | None = None
    deleted_at: datetime | None = None
    deleted_by: UUID | None = None
    version: int = 0
    created_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.profile is ProfileKind.AMBOS:
            raise ValueError("Ambos não é um perfil de login: o anexo tem um autor")

    @classmethod
    def new_link(
        cls,
        *,
        id: UUID,
        owner_kind: OwnerKind,
        owner_id: UUID,
        profile: ProfileKind,
        url: str,
        title: str | None,
        comment: str | None,
    ) -> "Attachment":
        return cls(
            id,
            owner_kind,
            owner_id,
            AttachmentKind.LINK,
            profile,
            url=parse_link(url).url,
            title=_clean(title, MAX_ATTACHMENT_TITLE),
            comment=_clean(comment, MAX_ATTACHMENT_COMMENT),
        )

    @classmethod
    def new_file(
        cls,
        *,
        id: UUID,
        owner_kind: OwnerKind,
        owner_id: UUID,
        profile: ProfileKind,
        file: AttachedFile,
        title: str | None,
        comment: str | None,
    ) -> "Attachment":
        if not is_attachable_content_type(file.content_type):
            raise AttachmentFileNotAllowed()
        return cls(
            id,
            owner_kind,
            owner_id,
            AttachmentKind.FILE,
            profile,
            file_id=file.file_id,
            file_name=file.name,
            content_type=file.content_type,
            size_bytes=file.size_bytes,
            title=_clean(title, MAX_ATTACHMENT_TITLE),
            comment=_clean(comment, MAX_ATTACHMENT_COMMENT),
        )

    @property
    def domain(self) -> str | None:
        return display_domain(self.url) if self.url else None

    @property
    def file(self) -> AttachedFile | None:
        if self.file_id is None or self.file_name is None:
            return None
        if self.content_type is None or self.size_bytes is None:
            return None
        return AttachedFile(self.file_id, self.file_name, self.content_type, self.size_bytes)

    def remove(self, by_profile: ProfileKind, by_user: UUID | None, now: datetime) -> None:
        if by_profile is not self.profile:
            raise Forbidden()
        self.deleted_at, self.deleted_by = now, by_user
