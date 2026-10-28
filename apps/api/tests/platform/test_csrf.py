import pytest
from fastapi.testclient import TestClient

from wedding.platform.bootstrap.app import build_app

CSRF = {"X-Altare-CSRF": "1"}


@pytest.fixture
def client() -> TestClient:
    return TestClient(build_app())


@pytest.mark.parametrize("metodo", ["post", "put", "patch", "delete"])
def test_metodo_que_altera_dados_sem_o_header_e_recusado(client, metodo):
    resposta = getattr(client, metodo)("/api/v1/health")
    assert resposta.status_code == 403
    assert resposta.headers["content-type"].startswith("application/problem+json")
    assert resposta.json()["code"] == "csrf_missing"


@pytest.mark.parametrize("valor", ["0", "true", ""])
def test_header_com_valor_diferente_de_1_e_recusado(client, valor):
    resposta = client.post("/api/v1/health", headers={"X-Altare-CSRF": valor})
    assert resposta.status_code == 403


def test_com_o_header_o_pedido_segue_para_a_rota(client):
    # o health só aceita GET: chegar ao 405 prova que passou pelo filtro
    assert client.post("/api/v1/health", headers=CSRF).status_code == 405


@pytest.mark.parametrize("metodo", ["get", "head", "options"])
def test_leitura_nao_exige_o_header(client, metodo):
    assert getattr(client, metodo)("/api/v1/health").status_code != 403


def test_fora_de_api_o_header_nao_e_exigido(client):
    assert client.post("/nao-e-api").status_code == 404
