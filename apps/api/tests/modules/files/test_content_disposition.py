import pytest

from wedding.modules.files.adapters.http.mappers import content_disposition


def test_traz_o_nome_de_reserva_em_ascii_e_o_nome_real_em_utf8():
    assert content_disposition("Cardápio ção.pdf") == (
        "inline; filename=\"Card_pio __o.pdf\"; filename*=UTF-8''Card%C3%A1pio%20%C3%A7%C3%A3o.pdf"
    )


@pytest.mark.parametrize(
    "nome", ['a"b.pdf', "a\\b.pdf", "a\nb.pdf", 'x"; filename="y.pdf', "a;b.pdf"]
)
def test_aspas_barras_e_quebras_de_linha_nao_escapam_do_cabecalho(nome):
    cabecalho = content_disposition(nome)
    reserva = cabecalho.split('filename="', 1)[1].split('";', 1)[0]
    assert '"' not in reserva
    assert "\\" not in reserva
    assert "\n" not in cabecalho
    assert "\r" not in cabecalho
    assert cabecalho.count('"') == 2
