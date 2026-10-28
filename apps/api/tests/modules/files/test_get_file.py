import pytest

from wedding.modules.files.application.commands.upload_file import UploadFileCommand
from wedding.shared_kernel.errors import NotFound

PDF = b"%PDF-1.7\n%conteudo de exemplo"


def _enviar(world):
    return world.use_cases().upload_file.execute(
        UploadFileCommand("proposta.pdf", PDF), world.actor
    )


def test_devolve_os_dados_e_o_conteudo_em_pedacos(world):
    enviado = _enviar(world)
    conteudo = world.use_cases().get_file.execute(enviado.id, world.actor)
    assert conteudo.file == enviado
    pedacos = list(conteudo.chunks)
    assert len(pedacos) > 1
    assert b"".join(pedacos) == PDF


def test_arquivo_que_nao_existe_nao_e_encontrado(world):
    with pytest.raises(NotFound):
        world.use_cases().get_file.execute(world.ids.new_id(), world.actor)


def test_registro_sem_o_conteudo_em_disco_nao_e_encontrado(world):
    enviado = _enviar(world)
    world.storage.blobs.clear()
    with pytest.raises(NotFound):
        world.use_cases().get_file.execute(enviado.id, world.actor)
