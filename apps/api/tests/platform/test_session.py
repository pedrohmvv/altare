from typing import Annotated
from uuid import uuid4

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from wedding.platform.http.app import create_app
from wedding.platform.http.session import current_actor
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.profile import ProfileKind

ATOR = Actor(user_id=uuid4(), profile=ProfileKind.NOIVA)


def _app(resolver) -> FastAPI:
    app = create_app(actor_resolver=resolver)

    @app.get("/api/v1/_teste/quem", include_in_schema=False)
    def quem(ator: Annotated[Actor, Depends(current_actor)]):
        return {"user_id": str(ator.user_id), "profile": ator.profile.value}

    return app


def test_cookie_valido_vira_o_ator_da_requisicao():
    recebidos: list[str] = []

    def resolver(token: str) -> Actor | None:
        recebidos.append(token)
        return ATOR

    client = TestClient(_app(resolver), cookies={"altare_session": "token-a"})
    resposta = client.get("/api/v1/_teste/quem")
    assert resposta.status_code == 200
    assert resposta.json() == {"user_id": str(ATOR.user_id), "profile": "Noiva"}
    assert recebidos == ["token-a"]


@pytest.mark.parametrize("cookies", [{}, {"altare_session": "token-a"}])
def test_sem_cookie_ou_com_sessao_que_nao_vale_e_nao_autenticado(cookies):
    client = TestClient(_app(lambda token: None), cookies=cookies)
    resposta = client.get("/api/v1/_teste/quem")
    assert resposta.status_code == 401
    assert resposta.json()["code"] == "unauthenticated"
    assert resposta.headers["content-type"].startswith("application/problem+json")


def test_o_resolvedor_nem_e_chamado_sem_cookie():
    chamado = []
    client = TestClient(_app(lambda token: chamado.append(token)))
    client.get("/api/v1/_teste/quem")
    assert chamado == []


def test_sem_resolvedor_configurado_ninguem_esta_autenticado():
    client = TestClient(_app(None), cookies={"altare_session": "token-a"})
    assert client.get("/api/v1/_teste/quem").status_code == 401
