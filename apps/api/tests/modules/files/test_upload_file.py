import hashlib

import pytest

from wedding.modules.files.application.commands.upload_file import UploadFileCommand
from wedding.modules.files.domain.errors import EmptyFile, FileTooLarge, UnsupportedFileType
from wedding.modules.files.domain.rules import MAX_FILE_BYTES

PDF = b"%PDF-1.7\n%conteudo de exemplo"
PNG = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDRconteudo"


def _enviar(world, nome: str | None = "proposta.pdf", conteudo=PDF):
    return world.use_cases().upload_file.execute(UploadFileCommand(nome, conteudo), world.actor)


def test_guarda_o_conteudo_e_o_registro_e_devolve_os_dados(world):
    enviado = _enviar(world)
    sha = hashlib.sha256(PDF).hexdigest()
    assert (enviado.name, enviado.content_type, enviado.size_bytes, enviado.sha256) == (
        "proposta.pdf",
        "application/pdf",
        len(PDF),
        sha,
    )
    assert world.storage.blobs == {sha: PDF}
    assert list(world.files) == [enviado.id]


def test_o_registro_nasce_no_nome_do_ator_da_sessao(world):
    _enviar(world)
    assert world.actors == [world.actor]


def test_o_nome_enviado_e_saneado_e_nunca_vira_caminho(world):
    enviado = _enviar(world, nome="../../etc/passwd.pdf")
    assert enviado.name == "passwd.pdf"
    assert all("/" not in chave and "." not in chave for chave in world.storage.blobs)


def test_o_tipo_vem_da_assinatura_e_nao_do_nome(world):
    enviado = _enviar(world, nome="foto.pdf", conteudo=PNG)
    assert enviado.content_type == "image/png"


def test_sem_nome_usa_um_nome_padrao(world):
    assert _enviar(world, nome=None).name == "arquivo"


@pytest.mark.parametrize(
    ("conteudo", "erro"),
    [
        (b"<html></html>", UnsupportedFileType),
        (b"", EmptyFile),
        (PDF + b"0" * MAX_FILE_BYTES, FileTooLarge),
    ],
)
def test_arquivo_recusado_nao_deixa_nada_para_tras(world, conteudo, erro):
    with pytest.raises(erro):
        _enviar(world, conteudo=conteudo)
    assert world.storage.blobs == {}
    assert world.files == {}


def test_o_mesmo_conteudo_enviado_duas_vezes_fica_uma_vez_no_disco_com_dois_registros(world):
    primeiro = _enviar(world, nome="proposta.pdf")
    segundo = _enviar(world, nome="proposta-final.pdf")
    assert primeiro.id != segundo.id
    assert primeiro.sha256 == segundo.sha256
    assert len(world.storage.blobs) == 1
    assert {f.original_name for f in world.files.values()} == {"proposta.pdf", "proposta-final.pdf"}
