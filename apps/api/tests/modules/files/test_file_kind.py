import pytest
from hypothesis import given
from hypothesis import strategies as st

from wedding.modules.files.domain.errors import EmptyFile, FileTooLarge, UnsupportedFileType
from wedding.modules.files.domain.rules import MAX_FILE_BYTES, detect_file_kind, inspect_upload
from wedding.modules.files.domain.value_objects import FileKind

PDF = b"%PDF-1.7\n%conteudo de exemplo"
JPEG = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00conteudo"
PNG = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDRconteudo"
WEBP = b"RIFF\x24\x00\x00\x00WEBPVP8 conteudo"


@pytest.mark.parametrize(
    ("conteudo", "tipo"),
    [
        (PDF, FileKind.PDF),
        (JPEG, FileKind.JPEG),
        (PNG, FileKind.PNG),
        (WEBP, FileKind.WEBP),
    ],
)
def test_reconhece_o_tipo_pela_assinatura_real(conteudo, tipo):
    assert detect_file_kind(conteudo) is tipo


def test_os_tipos_carregam_o_mime_que_o_navegador_entende():
    assert [t.value for t in FileKind] == [
        "application/pdf",
        "image/jpeg",
        "image/png",
        "image/webp",
    ]


@pytest.mark.parametrize(
    "conteudo",
    [
        b"<html><script>alert(1)</script></html>",
        b"MZ\x90\x00 executavel",
        b"PK\x03\x04 zip ou docx",
        b"GIF89a imagem que nao aceitamos",
        b"RIFF\x24\x00\x00\x00WAVEfmt  audio, nao imagem",
        b"%PD",
        b"\xff\xd8",
        b"\x89PNG\r\n",
        b"",
        b"texto simples com extensao .pdf",
    ],
)
def test_recusa_o_que_nao_tem_assinatura_conhecida(conteudo):
    assert detect_file_kind(conteudo) is None


def test_a_assinatura_precisa_estar_no_comeco_e_nao_em_qualquer_lugar():
    assert detect_file_kind(b"lixo antes " + PDF) is None


@given(conteudo=st.binary(max_size=64))
def test_detectar_nunca_quebra_com_bytes_quaisquer(conteudo):
    assert detect_file_kind(conteudo) in {None, *FileKind}


def test_aceita_o_conteudo_valido_e_devolve_o_tipo():
    assert inspect_upload(PDF) is FileKind.PDF


def test_aceita_exatamente_20_mb():
    conteudo = PDF + b"0" * (MAX_FILE_BYTES - len(PDF))
    assert len(conteudo) == MAX_FILE_BYTES == 20 * 1024 * 1024
    assert inspect_upload(conteudo) is FileKind.PDF


def test_recusa_um_byte_acima_de_20_mb():
    conteudo = PDF + b"0" * (MAX_FILE_BYTES - len(PDF) + 1)
    with pytest.raises(FileTooLarge) as erro:
        inspect_upload(conteudo)
    assert erro.value.code == "file_too_large"


def test_recusa_arquivo_vazio_com_um_code_proprio():
    with pytest.raises(EmptyFile) as erro:
        inspect_upload(b"")
    assert erro.value.code == "empty_file"


def test_recusa_tipo_nao_aceito_com_um_code_proprio():
    with pytest.raises(UnsupportedFileType) as erro:
        inspect_upload(b"<html></html>")
    assert erro.value.code == "unsupported_file_type"


def test_o_tamanho_e_conferido_antes_do_tipo():
    grande_e_invalido = b"x" * (MAX_FILE_BYTES + 1)
    with pytest.raises(FileTooLarge):
        inspect_upload(grande_e_invalido)
