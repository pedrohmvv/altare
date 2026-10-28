import os
import re
import tempfile
from collections.abc import Iterator
from pathlib import Path

_KEY = re.compile(r"[0-9a-f]{64}")
CHUNK_SIZE = 64 * 1024


class LocalFileStorage:
    """Arquivos em disco, endereçados pelo conteúdo (stack.md §3).

    O nome em disco é só o SHA-256, em duas pastas (`ab/ab12…`): o nome que a pessoa deu ao arquivo
    nunca vira caminho, e a chave que não for um SHA-256 é recusada, o que fecha a porta para
    `../../`. Gravar o mesmo conteúdo de novo não faz nada.
    """

    def __init__(self, root: Path) -> None:
        self._root = root

    def put(self, key: str, data: bytes) -> None:
        path = self._path(key)
        if path.exists():
            return
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        # Grava num temporário da mesma pasta e troca de nome: ninguém lê um arquivo pela metade.
        descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix=".tmp-")
        try:
            with os.fdopen(descriptor, "wb") as file:
                file.write(data)
            os.replace(temporary, path)
        except BaseException:
            Path(temporary).unlink(missing_ok=True)
            raise

    def exists(self, key: str) -> bool:
        return self._path(key).is_file()

    def read(self, key: str) -> Iterator[bytes]:
        return self._chunks(self._path(key))

    def _path(self, key: str) -> Path:
        if _KEY.fullmatch(key) is None:
            raise ValueError("A chave de um arquivo é o seu SHA-256, em hexadecimal minúsculo")
        return self._root / key[:2] / key

    @staticmethod
    def _chunks(path: Path) -> Iterator[bytes]:
        with path.open("rb") as file:
            while chunk := file.read(CHUNK_SIZE):
                yield chunk
