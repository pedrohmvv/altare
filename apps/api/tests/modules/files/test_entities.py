from uuid import uuid4

import pytest

from wedding.modules.files.domain.entities import FileAsset
from wedding.modules.files.domain.errors import EmptyFile
from wedding.modules.files.domain.value_objects import FileKind


def test_arquivo_guarda_nome_tipo_tamanho_e_hash():
    arquivo = FileAsset(
        id=uuid4(), original_name="proposta.pdf", kind=FileKind.PDF, size_bytes=10, sha256="a" * 64
    )
    assert (arquivo.original_name, arquivo.kind, arquivo.size_bytes) == (
        "proposta.pdf",
        FileKind.PDF,
        10,
    )


def test_arquivo_sem_conteudo_nao_existe():
    with pytest.raises(EmptyFile):
        FileAsset(
            id=uuid4(), original_name="x.pdf", kind=FileKind.PDF, size_bytes=0, sha256="a" * 64
        )
