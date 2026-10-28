import pytest

BASE = "/api/v1/wedding/scope"
CATALOGO = 18


def mapa(client):
    return client.get(BASE).json()


def grupo(corpo, nome):
    return next(g for g in corpo["groups"] if g["name"] == nome)


def categoria(corpo, nome):
    return next(c for g in corpo["groups"] for c in g["categories"] if c["name"] == nome)


def post_grupo(client, nome):
    return client.post(f"{BASE}/groups", json={"name": nome})


def post_categoria(client, grupo_id, nome, estimativa=None):
    return client.post(
        f"{BASE}/categories",
        json={"group_id": grupo_id, "name": nome, "estimate_cents": estimativa},
    )


def mudar_status(client, cat, status, motivo=None):
    return client.put(
        f"{BASE}/categories/{cat['id']}/status",
        json={"status": status, "reason": motivo, "version": cat["version"]},
    )


def test_so_com_sessao(api):
    assert api.anonimo.get(BASE).status_code == 401
    assert api.anonimo.post(f"{BASE}/groups", json={"name": "X"}).status_code == 401
    assert api.anonimo.get(f"{BASE}/categories/{'0' * 32}/history").status_code == 401


def test_o_mapa_traz_o_catalogo_com_tudo_vazio_e_a_versao_de_cada_item(api):  # F-PLN-02
    corpo = mapa(api.noivo)
    assert len(corpo["groups"]) == 8
    assert sum(len(g["categories"]) for g in corpo["groups"]) == CATALOGO
    primeira = corpo["groups"][0]["categories"][0]
    assert primeira["name"] == "Cerimônia civil"
    assert primeira["status"] == "Em discussão"
    assert primeira["estimate_cents"] is None
    assert primeira["discard_reason"] is None
    assert primeira["noivo"] == {"priority": None, "note": None, "version": 1}
    assert primeira["noiva"] == {"priority": None, "note": None, "version": 1}
    assert primeira["alignment"] == {"state": "falta", "missing": ["Noivo", "Noiva"]}
    assert (primeira["origin"], primeira["hidden"], primeira["visible"]) == (
        "catalogo",
        False,
        True,
    )
    assert primeira["can_delete"] is False
    assert corpo["progress"] == {"classified": 0, "total": CATALOGO}
    assert corpo["totals"] == {
        "essential_cents": 0,
        "essential_without_estimate": 0,
        "maybe_cents": 0,
        "maybe_without_estimate": 0,
    }


def test_o_contrato_declara_todos_os_campos_de_saida_como_obrigatorios(api):
    esquemas = api.app.openapi()["components"]["schemas"]
    for nome in ("ScopeMapOut", "GroupOut", "CategoryOut", "EvaluationOut", "StatusChangeOut"):
        esquema = esquemas[nome]
        assert set(esquema["required"]) == set(esquema["properties"]), nome


def test_grupos_criar_renomear_ocultar_excluir(api):
    criado = post_grupo(api.noivo, "Grupo Exemplo")
    assert criado.status_code == 201
    g = grupo(criado.json(), "Grupo Exemplo")
    assert (g["origin"], g["can_delete"], g["version"]) == ("casal", True, 1)

    renomeado = api.noiva.put(
        f"{BASE}/groups/{g['id']}", json={"name": "Novo Exemplo", "version": 1}
    )
    assert grupo(renomeado.json(), "Novo Exemplo")["version"] == 2

    oculto = api.noivo.put(
        f"{BASE}/groups/{g['id']}/visibility", json={"hidden": True, "version": 2}
    )
    assert grupo(oculto.json(), "Novo Exemplo")["hidden"] is True

    excluido = api.noivo.delete(f"{BASE}/groups/{g['id']}", params={"version": 3})
    assert excluido.status_code == 200
    assert all(x["name"] != "Novo Exemplo" for x in excluido.json()["groups"])


def test_nome_repetido_sem_diferenciar_caixa_e_409_e_nome_invalido_e_422(api):
    post_grupo(api.noivo, "Pós-festa Exemplo")
    repetido = post_grupo(api.noiva, "  PÓS-FESTA exemplo ")
    assert repetido.status_code == 409
    assert repetido.json()["code"] == "duplicate_scope_name"
    em_branco = post_grupo(api.noivo, "   ")
    assert (em_branco.status_code, em_branco.json()["code"]) == (422, "invalid_scope_value")
    assert api.noivo.post(f"{BASE}/groups", json={}).json()["code"] == "validation_error"


def test_grupo_do_catalogo_nao_se_exclui_e_grupo_com_categoria_tambem_nao(api):
    corpo = mapa(api.noivo)
    catalogo = corpo["groups"][0]
    resposta = api.noivo.delete(f"{BASE}/groups/{catalogo['id']}", params={"version": 1})
    assert (resposta.status_code, resposta.json()["code"]) == (422, "catalog_item_not_deletable")

    g = grupo(post_grupo(api.noivo, "Com Frente Exemplo").json(), "Com Frente Exemplo")
    post_categoria(api.noivo, g["id"], "Frente Exemplo")
    resposta = api.noivo.delete(f"{BASE}/groups/{g['id']}", params={"version": 1})
    assert (resposta.status_code, resposta.json()["code"]) == (422, "group_not_empty")


def test_excluir_exige_a_versao_na_query(api):
    g = grupo(post_grupo(api.noivo, "Grupo Exemplo").json(), "Grupo Exemplo")
    sem = api.noivo.delete(f"{BASE}/groups/{g['id']}")
    assert (sem.status_code, sem.json()["code"]) == (422, "validation_error")


def test_categoria_criar_com_estimativa_e_o_par_de_avaliacoes(api):
    g = grupo(post_grupo(api.noivo, "Grupo Exemplo").json(), "Grupo Exemplo")
    criada = post_categoria(api.noiva, g["id"], "Frente Exemplo", 2_800_000)
    assert criada.status_code == 201
    c = categoria(criada.json(), "Frente Exemplo")
    assert (c["estimate_cents"], c["origin"], c["can_delete"]) == (2_800_000, "casal", True)
    assert (c["noivo"]["version"], c["noiva"]["version"]) == (1, 1)


def test_categoria_em_grupo_inexistente_404_e_nome_repetido_em_outro_grupo_409(api):
    g = grupo(post_grupo(api.noivo, "Grupo Exemplo").json(), "Grupo Exemplo")
    assert post_categoria(api.noivo, "00000000-0000-0000-0000-000000000000", "X").status_code == 404
    repetido = post_categoria(api.noivo, g["id"], "fotografia")  # já existe no catálogo
    assert (repetido.status_code, repetido.json()["code"]) == (409, "duplicate_scope_name")


def test_categoria_atualizar_ocultar_e_excluir(api):
    g = grupo(post_grupo(api.noivo, "Grupo Exemplo").json(), "Grupo Exemplo")
    c = categoria(post_categoria(api.noivo, g["id"], "Frente Exemplo").json(), "Frente Exemplo")
    atualizada = api.noiva.put(
        f"{BASE}/categories/{c['id']}",
        json={"name": "Frente Nova", "group_id": g["id"], "estimate_cents": 150_000, "version": 1},
    )
    c = categoria(atualizada.json(), "Frente Nova")
    assert (c["estimate_cents"], c["version"]) == (150_000, 2)

    oculta = api.noivo.put(
        f"{BASE}/categories/{c['id']}/visibility", json={"hidden": True, "version": 2}
    )
    c = categoria(oculta.json(), "Frente Nova")
    assert (c["hidden"], c["visible"]) == (True, False)
    assert oculta.json()["progress"]["total"] == CATALOGO

    excluida = api.noivo.delete(f"{BASE}/categories/{c['id']}", params={"version": 3})
    assert excluida.status_code == 200
    assert all(
        x["name"] != "Frente Nova" for g_ in excluida.json()["groups"] for x in g_["categories"]
    )


def test_categoria_do_catalogo_nao_se_exclui(api):
    c = categoria(mapa(api.noivo), "Buffet")
    resposta = api.noivo.delete(f"{BASE}/categories/{c['id']}", params={"version": 1})
    assert (resposta.status_code, resposta.json()["code"]) == (422, "catalog_item_not_deletable")


def test_estimativa_zero_e_negativa_sao_422(api):
    c = categoria(mapa(api.noivo), "Buffet")
    for valor in (0, -5):
        resposta = api.noivo.put(
            f"{BASE}/categories/{c['id']}",
            json={
                "name": "Buffet",
                "group_id": c["group_id"],
                "estimate_cents": valor,
                "version": 1,
            },
        )
        assert (resposta.status_code, resposta.json()["code"]) == (422, "invalid_scope_value")


def test_status_fica_de_fora_exige_motivo_e_o_historico_o_guarda(api):  # F-PLN-03
    c = categoria(mapa(api.noivo), "Fotografia")
    sem = mudar_status(api.noivo, c, "Fica de fora")
    assert (sem.status_code, sem.json()["code"]) == (422, "discard_reason_required")
    assert categoria(mapa(api.noivo), "Fotografia")["version"] == 1

    ok = mudar_status(api.noiva, c, "Fica de fora", "fora do teto")
    c = categoria(ok.json(), "Fotografia")
    assert (c["status"], c["discard_reason"], c["version"]) == ("Fica de fora", "fora do teto", 2)
    assert ok.json()["progress"] == {"classified": 1, "total": CATALOGO}

    reaberta = categoria(mudar_status(api.noivo, c, "Em discussão").json(), "Fotografia")
    assert (reaberta["status"], reaberta["discard_reason"]) == ("Em discussão", "fora do teto")

    historico = api.noivo.get(f"{BASE}/categories/{c['id']}/history").json()
    assert [(h["from_status"], h["to_status"], h["by"]) for h in historico] == [
        ("Fica de fora", "Em discussão", "Noivo"),
        ("Em discussão", "Fica de fora", "Noiva"),
    ]
    assert historico[1]["reason"] == "fora do teto"


def test_status_com_versao_velha_e_409_e_nao_muda_nada(api):
    c = categoria(mapa(api.noivo), "Espaço")
    mudar_status(api.noivo, c, "Entra (Essencial)")
    resposta = mudar_status(api.noiva, c, "Talvez (Se couber)")  # `c` ainda é a versão 1
    assert (resposta.status_code, resposta.json()["code"]) == (409, "version_conflict")
    assert categoria(mapa(api.noiva), "Espaço")["status"] == "Entra (Essencial)"


def test_status_desconhecido_e_422_e_categoria_inexistente_e_404(api):
    c = categoria(mapa(api.noivo), "Espaço")
    assert mudar_status(api.noivo, c, "Talvez").json()["code"] == "validation_error"
    fantasma = {"id": "00000000-0000-0000-0000-000000000000", "version": 1}
    assert mudar_status(api.noivo, fantasma, "Entra (Essencial)").status_code == 404


def avaliar(client, cat, perfil, prioridade, nota=None, **extra):
    versao = cat[perfil]["version"]
    return client.put(
        f"{BASE}/categories/{cat['id']}/my-evaluation",
        json={"priority": prioridade, "note": nota, "version": versao, **extra},
    )


def test_cada_perfil_avalia_so_a_propria_e_o_perfil_nunca_vem_do_corpo(api):  # F-PLN-04
    c = categoria(mapa(api.noivo), "Buffet")
    resposta = avaliar(
        api.noiva, c, "noiva", "Quero muito", "adoramos", profile="Noivo", by="Noivo"
    )
    feita = categoria(resposta.json(), "Buffet")
    assert feita["noiva"] == {"priority": "Quero muito", "note": "adoramos", "version": 2}
    assert feita["noivo"] == {"priority": None, "note": None, "version": 1}
    assert feita["alignment"] == {"state": "falta", "missing": ["Noivo"]}
    assert feita["status"] == "Em discussão"


def test_alinhados_e_divergem(api):
    c = categoria(mapa(api.noivo), "Buffet")
    c = categoria(avaliar(api.noivo, c, "noivo", "Se couber").json(), "Buffet")
    divergem = categoria(avaliar(api.noiva, c, "noiva", "Dispenso").json(), "Buffet")
    assert divergem["alignment"] == {"state": "divergem", "missing": []}
    c = categoria(avaliar(api.noiva, divergem, "noiva", "Se couber").json(), "Buffet")
    assert c["alignment"]["state"] == "alinhados"


def test_avaliacao_com_versao_velha_prioridade_invalida_e_nota_longa(api):
    c = categoria(mapa(api.noivo), "Buffet")
    avaliar(api.noivo, c, "noivo", "Se couber")
    assert avaliar(api.noivo, c, "noivo", "Dispenso").status_code == 409
    assert avaliar(api.noivo, c, "noivo", "Talvez").json()["code"] == "validation_error"
    atual = categoria(mapa(api.noivo), "Buffet")
    assert (
        avaliar(api.noivo, atual, "noivo", None, "x" * 501).json()["code"] == "invalid_scope_value"
    )


def test_progresso_e_totais_da_api(api):  # F-PLN-05, F-PLN-08
    g = grupo(post_grupo(api.noivo, "Grupo Exemplo").json(), "Grupo Exemplo")
    a = categoria(post_categoria(api.noivo, g["id"], "A Exemplo", 100).json(), "A Exemplo")
    b = categoria(post_categoria(api.noivo, g["id"], "B Exemplo").json(), "B Exemplo")
    corpo = mudar_status(api.noivo, a, "Entra (Essencial)").json()
    corpo = mudar_status(api.noivo, b, "Entra (Essencial)").json()
    assert corpo["progress"] == {"classified": 2, "total": CATALOGO + 2}
    assert corpo["totals"]["essential_cents"] == 100
    assert corpo["totals"]["essential_without_estimate"] == 1


def test_mutacao_sem_o_header_anti_csrf_e_recusada(api):
    resposta = api.sem_csrf.post(f"{BASE}/groups", json={"name": "X Exemplo"})
    assert (resposta.status_code, resposta.json()["code"]) == (403, "csrf_missing")


def test_operation_ids_estaveis(api):
    caminhos = api.app.openapi()["paths"]
    ids = {
        op["operationId"]
        for caminho, metodos in caminhos.items()
        if "/wedding/scope" in caminho
        for op in metodos.values()
    }
    assert ids == {
        "read_scope_map",
        "create_scope_group",
        "update_scope_group",
        "set_scope_group_visibility",
        "delete_scope_group",
        "create_scope_category",
        "update_scope_category",
        "set_scope_category_visibility",
        "delete_scope_category",
        "change_scope_status",
        "set_my_evaluation",
        "list_scope_category_history",
    }


@pytest.mark.parametrize("caminho", ["groups", "categories"])
def test_post_aceita_so_json_valido(api, caminho):
    assert api.noivo.post(f"{BASE}/{caminho}", content=b"nao e json").status_code == 422
