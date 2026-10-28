import pytest
from hypothesis import given
from hypothesis import strategies as st

from wedding.modules.files.domain.rules import MAX_NAME_LENGTH, sanitize_filename


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [
        ("proposta.pdf", "proposta.pdf"),
        ("Proposta do Buffet Exemplo.pdf", "Proposta do Buffet Exemplo.pdf"),
        ("cardápio ção.PDF", "cardápio ção.PDF"),
        ("../../etc/passwd", "passwd"),
        ("C:\\Users\\casal\\contrato.pdf", "contrato.pdf"),
        ("/var/www/shell.php", "shell.php"),
        ("pasta/sub/foto.png", "foto.png"),
        ("  .oculto.pdf  ", "oculto.pdf"),
        ("linha\nquebrada\r.pdf", "linhaquebrada.pdf"),
        ("nulo\x00.pdf", "nulo.pdf"),
    ],
)
def test_so_o_nome_final_sobrevive_e_sem_caractere_perigoso(entrada, esperado):
    assert sanitize_filename(entrada) == esperado


@pytest.mark.parametrize("entrada", [None, "", "   ", "...", "/", "\\", "../", "\x00\x01"])
def test_sem_nome_aproveitavel_usa_um_nome_padrao(entrada):
    assert sanitize_filename(entrada) == "arquivo"


def test_nome_comprido_e_cortado_mas_mantem_a_extensao():
    nome = sanitize_filename("a" * 500 + ".pdf")
    assert len(nome) == MAX_NAME_LENGTH
    assert nome.endswith(".pdf")


@given(entrada=st.one_of(st.none(), st.text(max_size=400)))
def test_o_resultado_e_sempre_um_nome_seguro(entrada):
    nome = sanitize_filename(entrada)
    assert 1 <= len(nome) <= MAX_NAME_LENGTH
    assert "/" not in nome
    assert "\\" not in nome
    assert not nome.startswith(".")
    assert all(ord(c) >= 0x20 and ord(c) != 0x7F for c in nome)
    assert nome == nome.strip()


@given(entrada=st.text(max_size=400))
def test_sanear_duas_vezes_da_o_mesmo_resultado(entrada):
    assert sanitize_filename(sanitize_filename(entrada)) == sanitize_filename(entrada)
