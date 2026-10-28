from uuid import UUID

from pydantic import BaseModel

from wedding.modules.files.domain.value_objects import FileKind


class FileAssetOut(BaseModel):
    id: UUID
    name: str
    content_type: FileKind
    size_bytes: int
    sha256: str
