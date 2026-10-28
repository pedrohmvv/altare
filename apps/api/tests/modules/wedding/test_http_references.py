SCOPE = "/api/v1/wedding/scope"
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32
PDF = b"%PDF-1.7\n%conteudo de exemplo"
SEM_ID = "00000000-0000-0000-0000-000000000000"


def categoria(client, nome="Fotografia"):
    corpo = client.get(SCOPE).json()
    return next(c for g in corpo["groups"] for c in g["categories"] if c["name"] == nome)["id"]


def enviar(client, conteudo, nome="foto.png", tipo="image/png"):
    resposta = client.post("/api/v1/files", files={"file": (nome, conteudo, tipo)})
    assert resposta.status_code == 201
    return resposta.json()["id"]


def link(client, cat, url="https://exemplo.com/mesa", **extra):
    return client.post(
        f"{SCOPE}/categories/{cat}/references/links",
        json={"url": url, "title": None, "comment": None, **extra},
    )


def imagem(client, cat, file_id, **extra):
    return client.post(
        f"{SCOPE}/categories/{cat}/references/images",
        json={"file_id": file_id, "title": None, "comment": None, **extra},
    )


def test_so_com_sessao(api):
    cat = categoria(api.noivo)
    assert api.anonimo.get(f"{SCOPE}/categories/{cat}/references").status_code == 401
    assert link(api.anonimo, cat).status_code == 401


def test_categoria_nova_nao_tem_referencias(api):
    cat = categoria(api.noivo)
    assert api.noivo.get(f"{SCOPE}/categories/{cat}/references").json() == []


def test_link_com_dominio_titulo_e_o_autor_vindo_da_sessao(api):  # F-PLN-06
    cat = categoria(api.noivo)
    resposta = link(
        api.noiva,
        cat,
        "HTTPS://www.Exemplo.com/mesa",
        title=" Mesa ",
        comment="gostamos",
        profile="Noivo",
        by="Noivo",
    )
    assert resposta.status_code == 201
    (ref,) = resposta.json()
    assert (ref["kind"], ref["url"], ref["domain"], ref["file_id"]) == (
        "link",
        "https://www.exemplo.com/mesa",
        "exemplo.com",
        None,
    )
    assert (ref["title"], ref["comment"], ref["by"], ref["can_remove"]) == (
        "Mesa",
        "gostamos",
        "Noiva",
        True,
    )


def test_endereco_invalido_e_422_com_mensagem_acionavel(api):
    cat = categoria(api.noivo)
    for ruim in (
        "javascript:alert(1)",
        "exemplo.com",
        "ftp://exemplo.com",
        "https://u:p@exemplo.com",
    ):
        resposta = link(api.noivo, cat, ruim)
        assert (resposta.status_code, resposta.json()["code"]) == (422, "invalid_reference_url")
    assert "http://" in resposta.json()["detail"]
    assert api.noivo.get(f"{SCOPE}/categories/{cat}/references").json() == []


def test_imagem_enviada_vira_referencia_e_o_outro_a_ve_e_a_abre(api):
    cat = categoria(api.noivo)
    arquivo = enviar(api.noivo, PNG)
    resposta = imagem(api.noivo, cat, arquivo, title="Salão")
    assert resposta.status_code == 201
    (ref,) = resposta.json()
    assert (ref["kind"], ref["file_id"], ref["url"], ref["domain"], ref["by"]) == (
        "imagem",
        arquivo,
        None,
        None,
        "Noivo",
    )
    (vista,) = api.noiva.get(f"{SCOPE}/categories/{cat}/references").json()
    assert vista["can_remove"] is False
    assert api.noiva.get(f"/api/v1/files/{arquivo}").content == PNG


def test_pdf_nao_entra_como_referencia_e_arquivo_inexistente_e_404(api):
    cat = categoria(api.noivo)
    pdf = enviar(api.noivo, PDF, "a.pdf", "application/pdf")
    resposta = imagem(api.noivo, cat, pdf)
    assert (resposta.status_code, resposta.json()["code"]) == (422, "reference_file_not_image")
    assert imagem(api.noivo, cat, SEM_ID).status_code == 404
    assert api.noivo.get(f"{SCOPE}/categories/{cat}/references").json() == []


def test_arquivo_com_extensao_trocada_e_recusado_no_envio(api):  # F-PLN-06
    resposta = api.noivo.post(
        "/api/v1/files", files={"file": ("foto.png", b"isto nao e uma imagem", "image/png")}
    )
    assert (resposta.status_code, resposta.json()["code"]) == (422, "unsupported_file_type")


def test_so_o_autor_remove_e_o_outro_recebe_403(api):  # F-PLN-06, regra 2
    cat = categoria(api.noivo)
    (ref,) = link(api.noivo, cat).json()
    recusada = api.noiva.delete(f"{SCOPE}/categories/{cat}/references/{ref['id']}")
    assert (recusada.status_code, recusada.json()["code"]) == (403, "forbidden")
    assert len(api.noivo.get(f"{SCOPE}/categories/{cat}/references").json()) == 1

    removida = api.noivo.delete(f"{SCOPE}/categories/{cat}/references/{ref['id']}")
    assert (removida.status_code, removida.json()) == (200, [])
    assert api.noivo.delete(f"{SCOPE}/categories/{cat}/references/{ref['id']}").status_code == 404


def test_categoria_ou_referencia_inexistente_e_404(api):
    cat = categoria(api.noivo)
    assert api.noivo.get(f"{SCOPE}/categories/{SEM_ID}/references").status_code == 404
    assert link(api.noivo, SEM_ID).status_code == 404
    assert api.noivo.delete(f"{SCOPE}/categories/{cat}/references/{SEM_ID}").status_code == 404


def test_sem_limite_fixo_de_referencias(api):
    cat = categoria(api.noivo)
    for numero in range(25):
        link(api.noivo, cat, f"https://exemplo.com/{numero}")
    assert len(api.noivo.get(f"{SCOPE}/categories/{cat}/references").json()) == 25


def test_mutacao_sem_o_header_anti_csrf_e_recusada(api):
    cat = categoria(api.noivo)
    resposta = api.sem_csrf.post(
        f"{SCOPE}/categories/{cat}/references/links", json={"url": "https://exemplo.com"}
    )
    assert resposta.status_code == 403


def test_o_contrato_declara_todos_os_campos_de_saida_como_obrigatorios_e_os_operation_ids(api):
    esquemas = api.app.openapi()["components"]["schemas"]
    assert set(esquemas["ReferenceOut"]["required"]) == set(esquemas["ReferenceOut"]["properties"])
    ids = {
        op["operationId"]
        for caminho, metodos in api.app.openapi()["paths"].items()
        if "/references" in caminho
        for op in metodos.values()
    }
    assert ids == {
        "list_scope_references",
        "add_scope_link_reference",
        "add_scope_image_reference",
        "remove_scope_reference",
    }
