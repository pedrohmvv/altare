from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from wedding.modules.files.domain.entities import FileAsset
from wedding.modules.files.infrastructure.tables import file_assets


class SqlFileRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, file: FileAsset) -> None:
        self._session.add(file)

    def get(self, file_id: UUID) -> FileAsset | None:
        """Lê com a exclusão lógica filtrada (architecture.md §10)."""
        query = select(FileAsset).where(
            file_assets.c.id == file_id, file_assets.c.deleted_at.is_(None)
        )
        return self._session.execute(query).scalar_one_or_none()
