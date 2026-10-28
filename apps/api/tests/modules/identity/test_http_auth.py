from fastapi.testclient import TestClient

from wedding.shared_kernel.profile import ProfileKind

PROBLEM_JSON = "application/problem+json"


def _entrar(api, username="exemplo.noivo", password=None):
    return api.client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password or api.world.password},
    )


def test_login_correto_devolve_o_usuario_sem_dado_sensivel(api):
    criado = api.criar_usuario()
    resposta = _entrar(api)
    assert resposta.status_code == 200
    assert resposta.json() == {
        "user_id": str(criado.user_id),
        "username": "exemplo.noivo",
        "profile": "Noivo",
    }


def test_login_aceita_o_usuario_com_maiusculas_e_espacos(api):
    api.criar_usuario()
    assert _entrar(api, username="  EXEMPLO.Noivo ").status_code == 200


def test_login_entrega_o_cookie_da_sessao_com_todos_os_atributos(api):
    api.criar_usuario()
    cookie = _entrar(api).headers["set-cookie"].lower()
    assert cookie.startswith("altare_session=")
    for atributo in ("httponly", "samesite=lax", "path=/api", "max-age=7776000", "secure"):
        assert atributo in cookie, atributo


def test_o_cookie_nao_e_seguro_quando_o_desenvolvimento_local_o_desliga(api, world):
    from wedding.platform.bootstrap.app import build_app
    from wedding.platform.config import Settings

    settings = Settings(database_url=api.settings.database_url, session_cookie_secure=False)
    app = build_app(settings, clock=world.clock, hasher=world.hasher)
    client = TestClient(app, headers={"X-Altare-CSRF": "1"})
    api.criar_usuario()
    cookie = client.post(
        "/api/v1/auth/login", json={"username": "exemplo.noivo", "password": world.password}
    ).headers["set-cookie"]
    assert "secure" not in cookie.lower()


def test_me_devolve_o_usuario_da_sessao(api):
    api.criar_usuario("exemplo.noiva", ProfileKind.NOIVA)
    _entrar(api, "exemplo.noiva")
    resposta = api.client.get("/api/v1/auth/me")
    assert resposta.status_code == 200
    assert resposta.json()["profile"] == "Noiva"


def test_me_sem_sessao_nao_esta_autenticado(api):
    resposta = api.client.get("/api/v1/auth/me")
    assert resposta.status_code == 401
    assert resposta.headers["content-type"].startswith(PROBLEM_JSON)
    assert resposta.json()["code"] == "unauthenticated"


def test_senha_errada_e_um_problema_com_code_estavel(api):
    api.criar_usuario()
    resposta = _entrar(api, password="senha-errada-123")
    assert resposta.status_code == 401
    assert resposta.headers["content-type"].startswith(PROBLEM_JSON)
    assert resposta.json()["code"] == "invalid_credentials"
    assert "set-cookie" not in resposta.headers


def test_corpo_vazio_devolve_o_campo_para_o_formulario(api):
    resposta = api.client.post("/api/v1/auth/login", json={"username": "", "password": "x"})
    assert resposta.status_code == 422
    corpo = resposta.json()
    assert corpo["code"] == "validation_error"
    assert [e["field"] for e in corpo["errors"]] == ["username"]


def test_senha_gigante_e_recusada_antes_de_chegar_ao_argon2(api):
    resposta = _entrar(api, password="x" * 1025)
    assert resposta.status_code == 422


def test_usuario_fora_da_politica_da_conta_da_o_mesmo_401_e_nao_um_422(api):
    api.criar_usuario()
    resposta = _entrar(api, username="ab")
    assert resposta.status_code == 401
    assert resposta.json()["code"] == "invalid_credentials"


def test_logout_encerra_a_sessao_e_limpa_o_cookie(api):
    api.criar_usuario()
    _entrar(api)
    token = api.client.cookies.get("altare_session")
    resposta = api.client.post("/api/v1/auth/logout")
    assert resposta.status_code == 204
    assert resposta.content == b""
    assert "altare_session" not in api.client.cookies
    cookie = resposta.headers["set-cookie"].lower()
    assert "path=/api" in cookie
    assert "max-age=0" in cookie
    # o servidor também esqueceu: reenviar o token antigo não vale mais
    api.client.cookies.set("altare_session", token, path="/api")
    assert api.client.get("/api/v1/auth/me").status_code == 401


def test_logout_sem_sessao_nao_e_erro(api):
    assert api.client.post("/api/v1/auth/logout").status_code == 204


def test_o_openapi_documenta_as_tres_rotas_e_os_erros_como_problem_json(api):
    esquema = api.app.openapi()
    operacoes = {
        (caminho, metodo): dados["operationId"]
        for caminho, item in esquema["paths"].items()
        for metodo, dados in item.items()
    }
    assert operacoes[("/api/v1/auth/login", "post")] == "login"
    assert operacoes[("/api/v1/auth/logout", "post")] == "logout"
    assert operacoes[("/api/v1/auth/me", "get")] == "read_current_user"
    login = esquema["paths"]["/api/v1/auth/login"]["post"]["responses"]
    for status in ("401", "403", "422", "429"):
        assert list(login[status]["content"]) == ["application/problem+json"]
    assert esquema["components"]["schemas"]["CurrentUserOut"]["properties"]["profile"]["enum"] == [
        "Noivo",
        "Noiva",
    ]
