import json
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from wedding.platform.bootstrap.app import build_app
from wedding.platform.http.errors import status_for
from wedding.platform.http.messages import MESSAGES, message_for
from wedding.shared_kernel.errors import (
    Conflict,
    DomainError,
    DomainRuleViolated,
    Forbidden,
    NotFound,
    TooManyAttempts,
    Unauthenticated,
    VersionConflict,
)

PROBLEM_JSON = "application/problem+json"
SNAPSHOT = Path(__file__).parents[2] / "openapi.json"


def _com_rotas_de_teste() -> FastAPI:
    app = build_app()

    @app.get("/api/v1/_teste/erro/{nome}", include_in_schema=False)
    def levanta(nome: str):
        erros = {
            "nao-encontrado": NotFound(),
            "proibido": Forbidden(),
            "sem-sessao": Unauthenticated(),
            "regra": DomainRuleViolated("proposal_already_decided"),
            "conflito": Conflict("duplicate_contact"),
            "versao": VersionConflict(),
            "excesso": TooManyAttempts(retry_after=120),
        }
        if nome == "inesperado":
            raise RuntimeError("segredo interno: SELECT * FROM users")
        raise erros[nome]

    @app.get("/api/v1/_teste/paginado", include_in_schema=False)
    def paginado(limit: int = 10):
        return {"limit": limit}

    return app


@pytest.fixture
def client() -> TestClient:
    return TestClient(_com_rotas_de_teste(), raise_server_exceptions=False)


def test_health_responde_ok_sem_autenticacao(client):
    resposta = client.get("/api/v1/health")
    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_health_so_existe_sob_api_v1(client):
    assert client.get("/health").status_code == 404


@pytest.mark.parametrize(
    ("rota", "status", "code"),
    [
        ("nao-encontrado", 404, "not_found"),
        ("proibido", 403, "forbidden"),
        ("sem-sessao", 401, "unauthenticated"),
        ("regra", 422, "proposal_already_decided"),
        ("conflito", 409, "duplicate_contact"),
        ("versao", 409, "version_conflict"),
        ("excesso", 429, "too_many_attempts"),
    ],
)
def test_erro_de_dominio_vira_problem_json_com_status_e_code(client, rota, status, code):
    resposta = client.get(f"/api/v1/_teste/erro/{rota}")
    assert resposta.status_code == status
    assert resposta.headers["content-type"].startswith(PROBLEM_JSON)
    corpo = resposta.json()
    assert corpo["code"] == code
    assert corpo["status"] == status
    assert corpo["type"] == "about:blank"
    assert corpo["title"]
    assert corpo["detail"]


def test_excesso_de_tentativas_diz_em_quantos_segundos_tentar_de_novo(client):
    resposta = client.get("/api/v1/_teste/erro/excesso")
    assert resposta.headers["retry-after"] == "120"


def _erros_concretos(base=DomainError):
    for erro in base.__subclasses__():
        yield erro
        yield from _erros_concretos(erro)


def test_todo_erro_de_dominio_tem_status_http_e_mensagem_em_portugues():
    import wedding.modules.files.domain.errors
    import wedding.modules.guests.domain.errors
    import wedding.modules.identity.domain.errors
    import wedding.modules.wedding.domain.errors  # noqa: F401

    erros = [e for e in _erros_concretos() if e.default_code is not None]
    assert len(erros) >= 8
    for erro in erros:
        assert status_for(erro) is not None, erro.__name__
        assert erro.default_code in MESSAGES, erro.__name__


def test_detail_de_conflito_de_versao_diz_o_que_fazer(client):
    detail = client.get("/api/v1/_teste/erro/versao").json()["detail"]
    assert "Recarregue" in detail


def test_code_sem_mensagem_cadastrada_usa_texto_generico(client):
    corpo = client.get("/api/v1/_teste/erro/regra").json()
    assert corpo["detail"] == message_for("codigo_que_nao_existe").detail


def test_rota_inexistente_vira_problem_json(client):
    resposta = client.get("/api/v1/nao-existe")
    assert resposta.status_code == 404
    assert resposta.headers["content-type"].startswith(PROBLEM_JSON)
    assert resposta.json()["code"] == "not_found"


def test_metodo_nao_permitido_vira_problem_json(client):
    resposta = client.post("/api/v1/health", headers={"X-Altare-CSRF": "1"})
    assert resposta.status_code == 405
    assert resposta.json()["code"] == "method_not_allowed"


def test_validacao_devolve_o_campo_para_o_formulario(client):
    resposta = client.get("/api/v1/_teste/paginado", params={"limit": "abc"})
    assert resposta.status_code == 422
    assert resposta.headers["content-type"].startswith(PROBLEM_JSON)
    corpo = resposta.json()
    assert corpo["code"] == "validation_error"
    assert [e["field"] for e in corpo["errors"]] == ["limit"]
    assert corpo["errors"][0]["message"]


def test_erro_inesperado_nao_vaza_detalhe_interno(client):
    resposta = client.get("/api/v1/_teste/erro/inesperado")
    assert resposta.status_code == 500
    assert resposta.json()["code"] == "internal_error"
    assert "SELECT" not in resposta.text
    assert "segredo" not in resposta.text


def test_todo_code_conhecido_tem_mensagem_em_portugues():
    conhecidos = {
        "not_found",
        "forbidden",
        "unauthenticated",
        "version_conflict",
        "validation_error",
        "method_not_allowed",
        "internal_error",
        "csrf_missing",
        "invalid_credentials",
        "too_many_attempts",
    }
    assert conhecidos <= MESSAGES.keys()
    assert all(m.title and m.detail for m in MESSAGES.values())


def test_openapi_expoe_o_health_com_operation_id_estavel():
    esquema = build_app().openapi()
    assert esquema["paths"]["/api/v1/health"]["get"]["operationId"] == "health_check"


def test_openapi_fica_sob_api_v1():
    client = TestClient(build_app())
    assert client.get("/api/v1/openapi.json").status_code == 200


def test_snapshot_do_openapi_esta_em_dia():
    assert SNAPSHOT.exists(), "Gere o snapshot com: uv run wedding export-openapi"
    versionado = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    assert versionado == build_app().openapi(), "OpenAPI mudou: rode uv run wedding export-openapi"


def test_main_expoe_o_app_asgi():
    from wedding.main import app

    assert TestClient(app).get("/api/v1/health").status_code == 200
