from dataclasses import dataclass
from uuid import UUID

from wedding.modules.files.domain.errors import EmptyFile
from wedding.modules.files.domain.value_objects import FileKind


@dataclass
class FileAsset:
    """Um arquivo enviado. O conteúdo fica no `FileStorage`, endereçado pelo `sha256`; cada envio
    tem o seu registro, com o nome original, mesmo quando o conteúdo se repete."""

    id: UUID
    original_name: str
    kind: FileKind
    size_bytes: int
    sha256: str

    def __post_init__(self) -> None:
        if self.size_bytes <= 0:
            raise EmptyFile()
