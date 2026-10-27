import sqlite3

from fastapi.testclient import TestClient

from wedding.shared_kernel.profile import ProfileKind


def _entrar(client, world, username="exemplo.noivo", password=None):
    return client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password or world.password},
    )


def _errar(api, vezes, username="exemplo.noivo"):
    for _ in range(vezes):
        assert _entrar(api.client, api.world, username, "senha-errada-123").status_code == 401


def test_fixacao_de_sessao_o_token_muda_a_cada_login_e_o_antigo_morre(api):
    api.criar_usuario()
    _entrar(api.client, api.world)
    antigo = api.client.cookies.get("altare_session")
    _entrar(api.client, api.world)
    novo = api.client.cookies.get("altare_session")
    assert novo != antigo
    outro = TestClient(api.app, base_url="https://testserver", cookies={"altare_session": antigo})
    assert outro.get("/api/v1/auth/me").status_code == 401
    assert api.client.get("/api/v1/auth/me").status_code == 200


def test_trocar_de_usuario_no_mesmo_computador_encerra_a_sessao_anterior(api):
    api.criar_usuario("exemplo.noivo", ProfileKind.NOIVO)
    api.criar_usuario("exemplo.noiva", ProfileKind.NOIVA)
    _entrar(api.client, api.world, "exemplo.noivo")
    do_noivo = api.client.cookies.get("altare_session")
    _entrar(api.client, api.world, "exemplo.noiva")
    assert api.client.get("/api/v1/auth/me").json()["profile"] == "Noiva"
    outro = TestClient(api.app, base_url="https://testserver", cookies={"altare_session": do_noivo})
    assert outro.get("/api/v1/auth/me").status_code == 401


def test_csrf_login_e_logout_sem_o_header_sao_recusados(api):
    api.criar_usuario()
    sem_header = TestClient(api.app, base_url="https://testserver")
    corpo = {"username": "exemplo.noivo", "password": api.world.password}
    login = sem_header.post("/api/v1/auth/login", json=corpo)
    logout = sem_header.post("/api/v1/auth/logout")
    assert (login.status_code, login.json()["code"]) == (403, "csrf_missing")
    assert (logout.status_code, logout.json()["code"]) == (403, "csrf_missing")
    assert "set-cookie" not in login.headers


def test_csrf_com_sessao_valida_o_logout_sem_header_nao_derruba_a_sessao(api):
    api.criar_usuario()
    _entrar(api.client, api.world)
    forjado = TestClient(
        api.app,
        base_url="https://testserver",
        cookies={"altare_session": api.client.cookies.get("altare_session")},
    )
    assert forjado.post("/api/v1/auth/logout").status_code == 403
    assert api.client.get("/api/v1/auth/me").status_code == 200


def test_rate_limit_a_sexta_falha_recebe_429_com_retry_after(api):
    api.criar_usuario()
    _errar(api, 5)
    resposta = _entrar(api.client, api.world, password="senha-errada-123")
    assert resposta.status_code == 429
    assert resposta.headers["retry-after"] == "900"
    assert resposta.json()["code"] == "too_many_attempts"
    assert resposta.headers["content-type"].startswith("application/problem+json")


def test_rate_limit_durante_o_bloqueio_ate_a_senha_certa_e_recusada(api):
    api.criar_usuario()
    _errar(api, 5)
    assert _entrar(api.client, api.world).status_code == 429
    assert "altare_session" not in api.client.cookies


def test_rate_limit_depois_de_15_minutos_o_login_volta(api):
    api.criar_usuario()
    _errar(api, 5)
    api.world.clock.advance(minutes=15)
    assert _entrar(api.client, api.world).status_code == 200


def test_rate_limit_so_afeta_quem_errou(api):
    api.criar_usuario("exemplo.noivo", ProfileKind.NOIVO)
    api.criar_usuario("exemplo.noiva", ProfileKind.NOIVA)
    _errar(api, 5, "exemplo.noivo")
    assert _entrar(api.client, api.world, "exemplo.noiva").status_code == 200


def test_enumeracao_senha_errada_e_usuario_inexistente_sao_indistinguiveis(api):
    api.criar_usuario()
    errada = _entrar(api.client, api.world, "exemplo.noivo", "senha-errada-123")
    inexistente = _entrar(api.client, api.world, "ninguem.aqui", "senha-errada-123")
    assert errada.status_code == inexistente.status_code == 401
    assert errada.json() == inexistente.json()
    assert errada.headers["content-type"] == inexistente.headers["content-type"]
    assert api.world.hasher.unknown_user_calls == 1
    assert api.world.hasher.verify_calls == 1


def test_expiracao_por_inatividade_aos_30_dias(api):
    api.criar_usuario()
    _entrar(api.client, api.world)
    api.world.clock.advance(days=29, hours=23)
    assert api.client.get("/api/v1/auth/me").status_code == 200
    api.world.clock.advance(days=30)
    assert api.client.get("/api/v1/auth/me").status_code == 401


def test_expiracao_absoluta_aos_90_dias_mesmo_com_uso_constante(api):
    api.criar_usuario()
    _entrar(api.client, api.world)
    for _ in range(4):
        api.world.clock.advance(days=20)
        assert api.client.get("/api/v1/auth/me").status_code == 200
    api.world.clock.advance(days=10)
    assert api.client.get("/api/v1/auth/me").status_code == 401


def test_o_banco_guarda_so_o_hash_do_token_e_a_senha_so_em_hash(api):
    api.criar_usuario()
    _entrar(api.client, api.world)
    token = api.client.cookies.get("altare_session")
    arquivo = api.settings.database_url.removeprefix("sqlite:///")
    with sqlite3.connect(arquivo) as conn:
        (guardado,) = conn.execute("SELECT token_hash FROM user_sessions").fetchone()
        (senha,) = conn.execute("SELECT password_hash FROM users").fetchone()
    assert guardado != token
    assert len(guardado) == 64
    # o hasher falso do teste devolve `hash::<senha>`; o Argon2 real é coberto em test_infra_argon2
    assert senha == api.world.hasher.hash(api.world.password)
    assert senha != api.world.password


def test_a_resposta_do_login_e_do_me_nao_vaza_hash_nem_token(api):
    api.criar_usuario()
    login = _entrar(api.client, api.world)
    me = api.client.get("/api/v1/auth/me")
    for resposta in (login, me):
        assert set(resposta.json()) == {"user_id", "username", "profile"}
        assert api.client.cookies.get("altare_session") not in resposta.text
