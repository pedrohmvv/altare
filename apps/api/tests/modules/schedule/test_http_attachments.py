"""Os anexos (F-CRN-08) de marcos e de avulsas pela API, contra o banco migrado de verdade e o
upload real do `files`, com os dois perfis: autoria vinda da sessão, CSRF, 401, 403 só o autor,
404 do dono excluído, 422 do endereço e do arquivo, o anexo que some e volta com o dono."""

import logging
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from tests.modules.schedule.catalog import marco_id

BASE = "/api/v1/schedule"
PDF = b"%PDF-1.7\n%conteudo de exemplo"
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32
SEM_ID = "00000000-0000-0000-0000-000000000000"
MARCO = "C06"


@pytest.fixture
def api(api_clock):
    return api_clock


def cronograma(client):
    resposta = client.get(BASE)
    assert resposta.status_code == 200
    return resposta.json()


def marco(corpo, codigo=MARCO):
    return next(
        m for f in corpo["phases"] for m in f["milestones"] if m["id"] == str(marco_id(codigo))
    )


def avulsa(corpo, tarefa):
    return next(t for t in corpo["tasks"] if t["id"] == tarefa)


def nova_avulsa(client, titulo="Avulsa Exemplo"):
    resposta = client.post(f"{BASE}/tasks", json={"title": titulo})
    assert resposta.status_code == 201
    return next(t for t in resposta.json()["tasks"] if t["title"] == titulo)["id"]


def enviar(client, conteudo=PDF, nome="contrato-exemplo.pdf", tipo="application/pdf"):
    resposta = client.post("/api/v1/files", files={"file": (nome, conteudo, tipo)})
    assert resposta.status_code == 201
    return resposta.json()["id"]


def link(client, dono=None, tipo="milestones", url="https://exemplo.com/mesa", **extra):
    dono = dono or marco_id(MARCO)
    return client.post(
        f"{BASE}/{tipo}/{dono}/attachments/links",
        json={"url": url, "title": None, "comment": None, **extra},
    )


def arquivo(client, file_id, dono=None, tipo="milestones", **extra):
    dono = dono or marco_id(MARCO)
    return client.post(
        f"{BASE}/{tipo}/{dono}/attachments/files",
        json={"file_id": file_id, "title": None, "comment": None, **extra},
    )


def anexos(client, codigo=MARCO):
    return marco(cronograma(client), codigo)["attachments"]


def erro(resposta, status, code):
    assert (resposta.status_code, resposta.json()["code"]) == (status, code), resposta.text


def linhas(api, sql):
    engine = create_engine(api.url)
    try:
        with engine.connect() as conn:
            return list(conn.execute(text(sql)))
    finally:
        engine.dispose()


# --- contrato ---------------------------------------------------------------------------------


def test_operation_ids_e_rotas_estaveis(api):
    caminhos = api.app.openapi()["paths"]
    links = caminhos[f"{BASE}/{{owner_kind}}/{{owner_id}}/attachments/links"]["post"]
    arquivos = caminhos[f"{BASE}/{{owner_kind}}/{{owner_id}}/attachments/files"]["post"]
    remover = caminhos[f"{BASE}/attachments/{{attachment_id}}"]["delete"]
    assert links["operationId"] == "add_link_attachment"
    assert arquivos["operationId"] == "add_file_attachment"
    assert remover["operationId"] == "remove_attachment"
    assert set(remover["responses"]) >= {"200", "401", "403", "404", "409"}
    assert set(links["responses"]) >= {"201", "401", "404", "422"}


def test_o_contrato_declara_todos_os_campos_de_saida_dos_anexos_como_obrigatorios(api):
    esquemas = api.app.openapi()["components"]["schemas"]
    for nome in ("AttachmentOut", "AttachmentFileOut"):
        assert set(esquemas[nome]["required"]) == set(esquemas[nome]["properties"]), nome
    assert set(esquemas["AttachmentOut"]["properties"]) == {
        "id",
        "kind",
        "title",
        "comment",
        "url",
        "domain",
        "file",
        "by",
        "at",
        "can_remove",
    }
    assert set(esquemas["AttachmentFileOut"]["properties"]) == {
        "id",
        "name",
        "content_type",
        "size_bytes",
    }
    for nome in ("MilestoneOut", "TaskOut"):
        assert "attachments" in esquemas[nome]["required"], nome


def test_os_corpos_de_entrada_nao_tem_campo_de_autoria(api):
    esquemas = api.app.openapi()["components"]["schemas"]
    assert set(esquemas["AttachmentLinkIn"]["properties"]) == {"url", "title", "comment"}
    assert set(esquemas["AttachmentFileIn"]["properties"]) == {"file_id", "title", "comment"}


def test_o_dono_so_aceita_marco_ou_avulsa(api):
    for tipo in ("phases", "checklist", "milestone"):
        erro(link(api.noivo, marco_id(MARCO), tipo), 422, "validation_error")
        erro(arquivo(api.noivo, SEM_ID, marco_id(MARCO), tipo), 422, "validation_error")


def test_so_com_sessao_e_com_o_header_anti_csrf(api):
    alvo = f"{BASE}/milestones/{marco_id(MARCO)}/attachments"
    corpo_link = {"url": "https://exemplo.com", "title": None, "comment": None}
    corpo_arquivo = {"file_id": SEM_ID, "title": None, "comment": None}
    remover = f"{BASE}/attachments/{SEM_ID}"
    assert api.anonimo.post(f"{alvo}/links", json=corpo_link).status_code == 401
    assert api.anonimo.post(f"{alvo}/files", json=corpo_arquivo).status_code == 401
    assert api.anonimo.delete(remover).status_code == 401
    for resposta in (
        api.sem_csrf.post(f"{alvo}/links", json=corpo_link),
        api.sem_csrf.post(f"{alvo}/files", json=corpo_arquivo),
        api.sem_csrf.delete(remover),
    ):
        assert (resposta.status_code, resposta.json()["code"]) == (403, "csrf_missing")
    assert anexos(api.noivo) == []


# --- anexar link ------------------------------------------------------------------------------


def test_o_link_aparece_no_marco_com_o_dominio_derivado_e_a_autoria_da_sessao(api):  # F-CRN-08
    resposta = link(
        api.noivo, url=" HTTPS://www.Exemplo.com/mesa ", title=" Mesa ", comment=" gostamos "
    )
    assert resposta.status_code == 201
    (anexo,) = marco(resposta.json())["attachments"]
    assert anexo["kind"] == "link"
    assert (anexo["url"], anexo["domain"]) == ("https://www.exemplo.com/mesa", "exemplo.com")
    assert (anexo["title"], anexo["comment"], anexo["file"]) == ("Mesa", "gostamos", None)
    assert anexo["by"] == "Noivo"
    assert anexo["at"].startswith("2026-10-27T12:00")
    assert anexo["can_remove"] is True


def test_a_autoria_vem_da_sessao_mesmo_com_by_e_profile_no_corpo(api):
    resposta = link(
        api.noivo,
        by="Noiva",
        profile="Noiva",
        created_by=str(uuid4()),
        by_profile="Noiva",
    )
    assert resposta.status_code == 201
    (anexo,) = marco(resposta.json())["attachments"]
    assert anexo["by"] == "Noivo"
    perfis = linhas(api, "SELECT profile FROM attachments")
    assert perfis == [("Noivo",)]
    resposta = link(api.noiva, by="Noivo", profile="Noivo")
    # O relógio do teste é fixo: os dois têm o mesmo instante, e a ordem entre eles não importa.
    assert sorted(a["by"] for a in marco(resposta.json())["attachments"]) == ["Noiva", "Noivo"]


def test_o_link_vai_para_a_avulsa(api):
    tarefa = nova_avulsa(api.noiva)
    resposta = link(api.noiva, tarefa, "tasks", title="Referência")
    assert resposta.status_code == 201
    (anexo,) = avulsa(resposta.json(), tarefa)["attachments"]
    assert (anexo["title"], anexo["by"]) == ("Referência", "Noiva")
    assert all(not m["attachments"] for f in resposta.json()["phases"] for m in f["milestones"])


@pytest.mark.parametrize(
    "url",
    [
        "javascript:alert(1)",
        "data:text/html,<script>alert(1)</script>",
        "ftp://exemplo.com/arquivo",
        "https:///sem-host",
        "http://",
        "exemplo.com",
        "https://usuario:senha@exemplo.com",
        "https://banco-exemplo.com\\.gov.br/x",
        "https://exemplo\u202e.com",
        "https://exemplo\u200b.com",
        "https://ex_emplo.com",
        "",
    ],
)
def test_endereco_que_nao_e_http_ou_sem_host_e_recusado_com_422(api, url):  # F-CRN-08
    erro(link(api.noivo, url=url), 422, "invalid_attachment_url")
    assert anexos(api.noivo) == []
    assert linhas(api, "SELECT COUNT(*) FROM attachments") == [(0,)]


def test_o_idn_e_guardado_e_exibido_em_punycode(api):
    resposta = link(api.noivo, url="https://www.München.de/Bahn")
    (anexo,) = marco(resposta.json())["attachments"]
    assert anexo["url"] == "https://www.xn--mnchen-3ya.de/Bahn"
    assert anexo["domain"] == "xn--mnchen-3ya.de"


def test_o_limite_de_tamanho_do_corpo_fica_no_dominio_com_a_mensagem_do_casal(api):
    """Sem `max_length` no Pydantic: o 422 genérico diria só "Valor inválido." e o do domínio diz
    qual é o limite. O 422 não ecoa o texto enviado."""
    longo = "sentinela-" + "x" * 130
    resposta = link(api.noivo, title=longo)
    erro(resposta, 422, "invalid_schedule_value")
    assert "sentinela" not in resposta.text
    assert "120" in resposta.json()["detail"]


def test_titulo_ou_comentario_longos_sao_422_e_nao_cortados(api):
    erro(link(api.noivo, title="x" * 121), 422, "invalid_schedule_value")
    erro(link(api.noivo, comment="x" * 501), 422, "invalid_schedule_value")
    assert link(api.noivo, title="x" * 120, comment="y" * 500).status_code == 201


def test_o_corpo_sem_url_e_422_de_validacao(api):
    resposta = api.noivo.post(f"{BASE}/milestones/{marco_id(MARCO)}/attachments/links", json={})
    erro(resposta, 422, "validation_error")


def test_nao_ha_limite_de_anexos_por_item(api):
    for numero in range(55):
        assert link(api.noivo, url=f"https://exemplo.com/{numero}").status_code == 201
    assert len(anexos(api.noivo)) == 55


def test_anexar_nao_muda_a_version_nem_o_estado_do_dono(api):
    antes = marco(cronograma(api.noivo))
    link(api.noivo)
    arquivo(api.noiva, enviar(api.noiva))
    depois = marco(cronograma(api.noivo))
    assert (depois["version"], depois["state"]) == (antes["version"], antes["state"])
    assert len(depois["attachments"]) == 2


# --- anexar arquivo ---------------------------------------------------------------------------


def test_o_pdf_enviado_vira_anexo_com_nome_tipo_e_tamanho_copiados(api):  # F-CRN-08
    file_id = enviar(api.noivo, PDF, "planta-exemplo.pdf")
    resposta = arquivo(api.noivo, file_id, title="Planta", comment="Versão final")
    assert resposta.status_code == 201
    (anexo,) = marco(resposta.json())["attachments"]
    assert anexo["kind"] == "file"
    assert (anexo["url"], anexo["domain"]) == (None, None)
    assert anexo["file"] == {
        "id": file_id,
        "name": "planta-exemplo.pdf",
        "content_type": "application/pdf",
        "size_bytes": len(PDF),
    }
    assert (anexo["title"], anexo["comment"], anexo["by"]) == ("Planta", "Versão final", "Noivo")
    # O outro perfil baixa pelo `GET /files`, que é do módulo `files`.
    assert api.noiva.get(f"/api/v1/files/{file_id}").content == PDF


def test_a_imagem_enviada_vira_anexo_da_avulsa(api):
    tarefa = nova_avulsa(api.noivo)
    file_id = enviar(api.noivo, PNG, "foto-exemplo.png", "image/png")
    resposta = arquivo(api.noivo, file_id, tarefa, "tasks")
    assert resposta.status_code == 201
    (anexo,) = avulsa(resposta.json(), tarefa)["attachments"]
    assert anexo["file"]["content_type"] == "image/png"  # type: ignore[index]


def test_arquivo_que_nao_e_pdf_nem_imagem_e_recusado_ja_no_envio_e_nao_vira_anexo(api):
    html = api.noivo.post(
        "/api/v1/files", files={"file": ("pagina.html", b"<html>oi</html>", "text/html")}
    )
    erro(html, 422, "unsupported_file_type")
    assert anexos(api.noivo) == []


def test_arquivo_com_extensao_trocada_e_recusado_no_envio(api):  # F-CRN-08
    trocado = api.noivo.post(
        "/api/v1/files",
        files={"file": ("contrato.pdf", b"<html>isto nao e um pdf</html>", "application/pdf")},
    )
    erro(trocado, 422, "unsupported_file_type")
    assert anexos(api.noivo) == []


def test_arquivo_inexistente_e_404_e_nada_e_gravado(api):
    erro(arquivo(api.noivo, SEM_ID), 404, "not_found")
    assert linhas(api, "SELECT COUNT(*) FROM attachments") == [(0,)]


def test_o_dono_inexistente_ou_do_outro_tipo_e_404(api):
    file_id = enviar(api.noivo)
    erro(link(api.noivo, SEM_ID), 404, "not_found")
    erro(arquivo(api.noivo, file_id, SEM_ID), 404, "not_found")
    erro(link(api.noivo, marco_id(MARCO), "tasks"), 404, "not_found")
    erro(arquivo(api.noivo, file_id, marco_id(MARCO), "tasks"), 404, "not_found")


def test_o_corpo_do_arquivo_com_id_invalido_e_422_de_validacao(api):
    erro(arquivo(api.noivo, "nao-e-um-uuid"), 422, "validation_error")


# --- dono excluído ----------------------------------------------------------------------------


def excluir_marco(client, codigo=MARCO):
    versao = marco(cronograma(client), codigo)["version"]
    resposta = client.delete(f"{BASE}/milestones/{marco_id(codigo)}", params={"version": versao})
    assert resposta.status_code == 200, resposta.text


def test_excluir_o_marco_esconde_os_anexos_e_restaurar_os_traz_de_volta(api):  # F-CRN-08
    link(api.noivo)
    arquivo(api.noiva, enviar(api.noiva))
    antes = anexos(api.noivo)
    assert len(antes) == 2
    excluir_marco(api.noivo)
    assert all(
        m["id"] != str(marco_id(MARCO))
        for f in cronograma(api.noivo)["phases"]
        for m in f["milestones"]
    )
    assert linhas(api, "SELECT COUNT(*) FROM attachments WHERE deleted_at IS NULL") == [(2,)]
    restaurado = api.noivo.post(f"{BASE}/milestones/{marco_id(MARCO)}/restore")
    assert restaurado.status_code == 200
    assert anexos(api.noivo) == antes


def test_excluir_a_avulsa_esconde_os_anexos_e_restaurar_os_traz_de_volta(api):
    tarefa = nova_avulsa(api.noivo)
    link(api.noivo, tarefa, "tasks")
    antes = avulsa(cronograma(api.noivo), tarefa)["attachments"]
    assert len(antes) == 1
    versao = avulsa(cronograma(api.noivo), tarefa)["version"]
    assert api.noivo.delete(f"{BASE}/tasks/{tarefa}", params={"version": versao}).status_code == 200
    assert cronograma(api.noivo)["tasks"] == []
    assert api.noivo.post(f"{BASE}/tasks/{tarefa}/restore").status_code == 200
    assert avulsa(cronograma(api.noivo), tarefa)["attachments"] == antes


def test_com_o_dono_excluido_anexar_e_remover_dao_404(api):
    link(api.noivo)
    (anexo,) = anexos(api.noivo)
    excluir_marco(api.noivo)
    erro(link(api.noivo), 404, "not_found")
    erro(arquivo(api.noivo, enviar(api.noivo)), 404, "not_found")
    erro(api.noivo.delete(f"{BASE}/attachments/{anexo['id']}"), 404, "not_found")


# --- remover ----------------------------------------------------------------------------------


def test_o_autor_remove_o_seu_e_a_linha_fica_guardada(api):  # F-CRN-08, regra 3
    link(api.noivo)
    (anexo,) = anexos(api.noivo)
    resposta = api.noivo.delete(f"{BASE}/attachments/{anexo['id']}")
    assert resposta.status_code == 200
    assert marco(resposta.json())["attachments"] == []
    assert anexos(api.noiva) == []
    (guardado,) = linhas(api, "SELECT deleted_at, deleted_by FROM attachments")
    assert guardado[0] is not None
    assert guardado[1] is not None


def test_so_o_autor_remove_o_outro_recebe_403_chamando_direto_e_ve_can_remove_falso(api):
    link(api.noiva)
    (visto_pelo_noivo,) = anexos(api.noivo)
    assert visto_pelo_noivo["can_remove"] is False
    assert visto_pelo_noivo["by"] == "Noiva"
    assert anexos(api.noiva)[0]["can_remove"] is True
    erro(api.noivo.delete(f"{BASE}/attachments/{visto_pelo_noivo['id']}"), 403, "forbidden")
    assert len(anexos(api.noiva)) == 1
    assert linhas(api, "SELECT COUNT(*) FROM attachments WHERE deleted_at IS NOT NULL") == [(0,)]
    assert api.noiva.delete(f"{BASE}/attachments/{visto_pelo_noivo['id']}").status_code == 200


def test_remover_o_que_nao_existe_ou_ja_saiu_e_404(api):
    erro(api.noivo.delete(f"{BASE}/attachments/{SEM_ID}"), 404, "not_found")
    link(api.noivo)
    (anexo,) = anexos(api.noivo)
    api.noivo.delete(f"{BASE}/attachments/{anexo['id']}")
    erro(api.noivo.delete(f"{BASE}/attachments/{anexo['id']}"), 404, "not_found")
    erro(api.noivo.delete(f"{BASE}/attachments/nao-e-um-uuid"), 422, "validation_error")


def test_remover_nao_muda_a_version_do_dono_nem_toca_os_outros_anexos(api):
    for numero in range(3):
        link(api.noivo, url=f"https://exemplo.com/{numero}")
    antes = marco(cronograma(api.noivo))
    meio = antes["attachments"][1]
    api.noivo.delete(f"{BASE}/attachments/{meio['id']}")
    depois = marco(cronograma(api.noivo))
    assert depois["version"] == antes["version"]
    assert [a["id"] for a in depois["attachments"]] == [
        a["id"] for a in antes["attachments"] if a["id"] != meio["id"]
    ]


def test_nao_ha_rota_de_restaurar_o_anexo(api):
    link(api.noivo)
    (anexo,) = anexos(api.noivo)
    caminhos = api.app.openapi()["paths"]
    assert not [c for c in caminhos if "attachments" in c and "restore" in c]
    assert api.noivo.post(f"{BASE}/attachments/{anexo['id']}/restore").status_code in (404, 405)


# --- logs -------------------------------------------------------------------------------------


def test_nenhum_registro_de_log_leva_url_nome_de_arquivo_nem_texto_do_anexo(api, caplog):
    caplog.set_level(logging.DEBUG)
    sentinela = "sentinela-secreta-exemplo"
    link(api.noivo, url=f"https://{sentinela}.test/caminho", title=sentinela, comment=sentinela)
    link(api.noivo, url=f"javascript:{sentinela}")  # 422
    file_id = enviar(api.noivo, PDF, f"{sentinela}.pdf")
    arquivo(api.noivo, file_id, title=sentinela)
    arquivo(api.noivo, SEM_ID)  # 404
    api.noivo.post(
        f"{BASE}/milestones/{marco_id(MARCO)}/attachments/links", json={"url": sentinela}
    )
    (primeiro, *_) = anexos(api.noivo)
    api.noivo.delete(f"{BASE}/attachments/{primeiro['id']}")
    texto = "\n".join(f"{r.getMessage()} {r.args!r}" for r in caplog.records)
    assert sentinela not in texto
