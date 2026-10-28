import pytest

from wedding.modules.files.application.commands.upload_file import UploadFileCommand
from wedding.shared_kernel.errors import NotFound

PDF = b"%PDF-1.7\n%conteudo de exemplo"
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16


def test_devolve_so_os_dados_sem_abrir_o_conteudo(world):
    enviado = world.use_cases().upload_file.execute(UploadFileCommand("foto.png", PNG), world.actor)
    info = world.use_cases().get_file_info.execute(enviado.id, world.actor)
    assert info == enviado
    assert info.content_type == "image/png"


def test_distingue_pdf_de_imagem_pelo_tipo_real(world):
    enviado = world.use_cases().upload_file.execute(UploadFileCommand("a.pdf", PDF), world.actor)
    assert world.use_cases().get_file_info.execute(enviado.id, world.actor).content_type == (
        "application/pdf"
    )


def test_arquivo_que_nao_existe_nao_e_encontrado(world):
    with pytest.raises(NotFound):
        world.use_cases().get_file_info.execute(world.ids.new_id(), world.actor)
