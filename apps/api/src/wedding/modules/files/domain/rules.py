import os
import unicodedata

from wedding.modules.files.domain.errors import EmptyFile, FileTooLarge, UnsupportedFileType
from wedding.modules.files.domain.value_objects import FileKind

MAX_FILE_BYTES = 20 * 1024 * 1024
MAX_NAME_LENGTH = 120
DEFAULT_NAME = "arquivo"
_MAX_EXTENSION_LENGTH = 10
_DROPPED_CATEGORIES = {"Cc", "Zl", "Zp"}


def detect_file_kind(content: bytes) -> FileKind | None:
    """O tipo vem da assinatura real no começo do arquivo, não da extensão nem do tipo que o
    cliente disse: um HTML renomeado para `.pdf` continua sendo HTML."""
    head = content[:12]
    if head.startswith(b"%PDF-"):
        return FileKind.PDF
    if head.startswith(b"\xff\xd8\xff"):
        return FileKind.JPEG
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return FileKind.PNG
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return FileKind.WEBP
    return None


def inspect_upload(content: bytes) -> FileKind:
    if not content:
        raise EmptyFile()
    if len(content) > MAX_FILE_BYTES:
        raise FileTooLarge()
    kind = detect_file_kind(content)
    if kind is None:
        raise UnsupportedFileType()
    return kind


def sanitize_filename(name: str | None) -> str:
    """Só o nome final, sem pasta, sem caractere de controle e sem ponto no começo. O nome serve
    para exibir e sugerir no download; nunca vira caminho em disco."""
    if name is None:
        return DEFAULT_NAME
    kept = "".join(ch for ch in name if unicodedata.category(ch) not in _DROPPED_CATEGORIES)
    text = unicodedata.normalize("NFC", kept)
    text = text.replace("\\", "/").rsplit("/", 1)[-1]
    text = text.strip().lstrip(".").strip()
    text = _truncate_keeping_extension(text).strip()
    return text or DEFAULT_NAME


def _truncate_keeping_extension(text: str) -> str:
    if len(text) <= MAX_NAME_LENGTH:
        return text
    stem, extension = os.path.splitext(text)
    if not extension or len(extension) > _MAX_EXTENSION_LENGTH:
        return text[:MAX_NAME_LENGTH]
    return stem[: MAX_NAME_LENGTH - len(extension)] + extension
