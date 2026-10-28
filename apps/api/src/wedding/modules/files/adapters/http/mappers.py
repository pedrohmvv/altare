import re
from urllib.parse import quote

from wedding.modules.files.adapters.http.schemas import FileAssetOut
from wedding.modules.files.application.dto import FileAssetDto


def to_file_asset_out(file: FileAssetDto) -> FileAssetOut:
    return FileAssetOut.model_validate(
        {
            "id": file.id,
            "name": file.name,
            "content_type": file.content_type,
            "size_bytes": file.size_bytes,
            "sha256": file.sha256,
        }
    )


def content_disposition(name: str) -> str:
    """`inline` com o nome sugerido: um nome ASCII de reserva e o nome real em UTF-8 (RFC 5987), sem
    deixar aspas ou barras do nome escaparem do cabeçalho."""
    fallback = re.sub(r"[^A-Za-z0-9._ -]", "_", name)
    return f"inline; filename=\"{fallback}\"; filename*=UTF-8''{quote(name, safe='')}"
