from sqlalchemy import inspect

from wedding.modules.files.domain.entities import FileAsset
from wedding.modules.files.infrastructure.tables import file_assets
from wedding.platform.db.metadata import mapper_registry


def start_mappers() -> None:
    """Liga a dataclass do domínio à tabela; pode ser chamada mais de uma vez."""
    if inspect(FileAsset, raiseerr=False) is None:
        mapper_registry.map_imperatively(
            FileAsset,
            file_assets,
            version_id_col=file_assets.c.version,
            # O domínio chama de `kind`; a coluna descreve o que ela guarda.
            properties={"kind": file_assets.c.content_type},
        )
