from collections.abc import Iterator
from dataclasses import dataclass
from uuid import UUID

from wedding.modules.files.domain.entities import FileAsset


@dataclass(frozen=True)
class FileAssetDto:
    id: UUID
    name: str
    content_type: str
    size_bytes: int
    sha256: str


@dataclass(frozen=True)
class FileContent:
    file: FileAssetDto
    chunks: Iterator[bytes]


def to_dto(file: FileAsset) -> FileAssetDto:
    return FileAssetDto(
        id=file.id,
        name=file.original_name,
        content_type=file.kind.value,
        size_bytes=file.size_bytes,
        sha256=file.sha256,
    )
