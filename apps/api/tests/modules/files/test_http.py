import hashlib
import sqlite3
from uuid import UUID, uuid4

import pytest

from wedding.modules.files.domain.rules import MAX_FILE_BYTES

PDF = b"%PDF-1.7\n%conteudo de exemplo"
JPEG = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00conteudo"
PNG = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDRconteudo"
WEBP = b"RIFF\x24\x00\x00\x00WEBPVP8 conteudo"
PROBLEM_JSON = "application/problem+json"


def _enviar(client, nome="proposta.pdf", conteudo=PDF, tipo="application/pdf"):
    return client.post("/api/v1/files", files={"file": (nome, conteudo, tipo)})


def _arquivos_em_disco(api):
    return [p for p in api.raiz.rglob("*") if p.is_file()] if api.raiz.exists() else []


class TestUpload:
    def test_envia_um_pdf_e_devolve_os_dados(self, api):
        resposta = _enviar(api.noivo)
        assert resposta.status_code == 201
        corpo = resposta.json()
        assert UUID(corpo["id"])
        assert corpo["name"] == "proposta.pdf"
        assert corpo["content_type"] == "application/pdf"
        assert corpo["size_bytes"] == len(PDF)
        assert corpo["sha256"] == hashlib.sha256(PDF).hexdigest()
        assert set(corpo) == {"id", "name", "content_type", "size_bytes", "sha256"}

    @pytest.mark.parametrize(
        ("conteudo", "tipo"),
        [(PDF, "application/pdf"), (JPEG, "image/jpeg"), (PNG, "image/png"), (WEBP, "image/webp")],
    )
    def test_aceita_os_quatro_tipos(self, api, conteudo, tipo):
        resposta = _enviar(api.noivo, "arquivo", conteudo, "application/octet-stream")
        assert resposta.status_code == 201
        assert resposta.json()["content_type"] == tipo

    def test_o_tipo_vem_da_assinatura_e_nao_do_que_o_cliente_disse(self, api):
        resposta = _enviar(api.noivo, "foto.pdf", PNG, "application/pdf")
        assert resposta.json()["content_type"] == "image/png"

    def test_html_disfarcado_de_pdf_e_recusado_e_nao_deixa_nada(self, api):
        resposta = _enviar(api.noivo, "boleto.pdf", b"<html><script>alert(1)</script></html>")
        assert resposta.status_code == 422
        assert resposta.headers["content-type"].startswith(PROBLEM_JSON)
        assert resposta.json()["code"] == "unsupported_file_type"
        assert _arquivos_em_disco(api) == []

    def test_arquivo_vazio_e_recusado(self, api):
        resposta = _enviar(api.noivo, "vazio.pdf", b"")
        assert (resposta.status_code, resposta.json()["code"]) == (422, "empty_file")

    def test_aceita_exatamente_20_mb_e_recusa_um_byte_a_mais(self, api):
        no_limite = PDF + b"0" * (MAX_FILE_BYTES - len(PDF))
        assert _enviar(api.noivo, "limite.pdf", no_limite).status_code == 201
        acima = no_limite + b"0"
        resposta = _enviar(api.noivo, "acima.pdf", acima)
        assert (resposta.status_code, resposta.json()["code"]) == (422, "file_too_large")

    def test_sem_o_campo_file_devolve_o_campo_para_o_formulario(self, api):
        resposta = api.noivo.post("/api/v1/files", data={"outro": "x"})
        assert resposta.status_code == 422
        assert resposta.json()["code"] == "validation_error"
        assert [e["field"] for e in resposta.json()["errors"]] == ["file"]

    def test_o_nome_enviado_nunca_vira_caminho(self, api):
        resposta = _enviar(api.noivo, "../../../etc/passwd.pdf")
        assert resposta.json()["name"] == "passwd.pdf"
        sha = hashlib.sha256(PDF).hexdigest()
        assert [p.relative_to(api.raiz).as_posix() for p in _arquivos_em_disco(api)] == [
            f"{sha[:2]}/{sha}"
        ]

    def test_o_mesmo_conteudo_duas_vezes_da_dois_registros_e_um_arquivo_em_disco(self, api):
        primeiro = _enviar(api.noivo, "a.pdf").json()
        segundo = _enviar(api.noiva, "b.pdf").json()
        assert primeiro["id"] != segundo["id"]
        assert primeiro["sha256"] == segundo["sha256"]
        assert len(_arquivos_em_disco(api)) == 1

    def test_o_registro_leva_o_autor_da_sessao(self, api):
        _enviar(api.noiva)
        arquivo = api.settings.database_url.removeprefix("sqlite:///")
        with sqlite3.connect(arquivo) as conn:
            (autor,) = conn.execute("SELECT created_by FROM file_assets").fetchone()
            (noiva,) = conn.execute(
                "SELECT id FROM users WHERE username='exemplo.noiva'"
            ).fetchone()
        assert autor == noiva

    def test_sem_sessao_e_nao_autenticado_e_nada_e_guardado(self, api):
        resposta = _enviar(api.anonimo)
        assert (resposta.status_code, resposta.json()["code"]) == (401, "unauthenticated")
        assert _arquivos_em_disco(api) == []

    def test_sem_o_header_anti_csrf_e_recusado(self, api):
        api.sem_csrf.cookies.update(api.noivo.cookies)
        resposta = _enviar(api.sem_csrf)
        assert (resposta.status_code, resposta.json()["code"]) == (403, "csrf_missing")
        assert _arquivos_em_disco(api) == []


class TestDownload:
    def test_devolve_o_conteudo_e_os_cabecalhos_de_seguranca(self, api):
        enviado = _enviar(api.noivo).json()
        resposta = api.noivo.get(f"/api/v1/files/{enviado['id']}")
        assert resposta.status_code == 200
        assert resposta.content == PDF
        assert resposta.headers["content-type"] == "application/pdf"
        assert resposta.headers["content-length"] == str(len(PDF))
        assert resposta.headers["x-content-type-options"] == "nosniff"
        assert resposta.headers["cache-control"] == "private, no-store"
        assert resposta.headers["content-disposition"].startswith("inline;")

    def test_o_tipo_servido_e_o_validado_mesmo_com_um_nome_enganoso(self, api):
        enviado = _enviar(api.noivo, "pagina.html", PNG, "text/html").json()
        resposta = api.noivo.get(f"/api/v1/files/{enviado['id']}")
        assert resposta.headers["content-type"] == "image/png"

    def test_o_nome_sugerido_aguenta_acento_e_espaco(self, api):
        enviado = _enviar(api.noivo, "Cardápio novo.pdf").json()
        disposicao = api.noivo.get(f"/api/v1/files/{enviado['id']}").headers["content-disposition"]
        assert "filename*=UTF-8''Card%C3%A1pio%20novo.pdf" in disposicao
        assert 'filename="Card_pio novo.pdf"' in disposicao

    def test_o_casal_le_os_arquivos_um_do_outro(self, api):
        enviado = _enviar(api.noivo).json()
        assert api.noiva.get(f"/api/v1/files/{enviado['id']}").content == PDF

    def test_arquivo_que_nao_existe_nao_e_encontrado(self, api):
        resposta = api.noivo.get(f"/api/v1/files/{uuid4()}")
        assert (resposta.status_code, resposta.json()["code"]) == (404, "not_found")
        assert resposta.headers["content-type"].startswith(PROBLEM_JSON)

    def test_id_que_nao_e_um_uuid_e_validacao(self, api):
        resposta = api.noivo.get("/api/v1/files/nao-e-um-uuid")
        assert resposta.status_code == 422
        assert resposta.json()["code"] == "validation_error"

    def test_caminho_com_barras_nao_chega_a_nenhum_arquivo(self, api):
        enviado = _enviar(api.noivo).json()
        resposta = api.noivo.get(f"/api/v1/files/{enviado['id']}/../../../etc/passwd")
        assert resposta.status_code == 404
        assert b"root:" not in resposta.content

    def test_sem_sessao_nao_baixa_nada(self, api):
        enviado = _enviar(api.noivo).json()
        resposta = api.anonimo.get(f"/api/v1/files/{enviado['id']}")
        assert (resposta.status_code, resposta.json()["code"]) == (401, "unauthenticated")

    def test_registro_sem_o_conteudo_em_disco_nao_e_encontrado(self, api):
        enviado = _enviar(api.noivo).json()
        for arquivo in _arquivos_em_disco(api):
            arquivo.unlink()
        assert api.noivo.get(f"/api/v1/files/{enviado['id']}").status_code == 404


class TestContrato:
    def test_o_openapi_documenta_as_duas_rotas(self, api):
        esquema = api.app.openapi()
        envio = esquema["paths"]["/api/v1/files"]["post"]
        leitura = esquema["paths"]["/api/v1/files/{file_id}"]["get"]
        assert envio["operationId"] == "upload_file"
        assert leitura["operationId"] == "download_file"
        assert "multipart/form-data" in envio["requestBody"]["content"]
        for status in ("401", "403", "422"):
            assert list(envio["responses"][status]["content"]) == [PROBLEM_JSON]
        for status in ("401", "404", "422"):
            assert list(leitura["responses"][status]["content"]) == [PROBLEM_JSON]

    def test_o_download_documenta_os_quatro_tipos_de_conteudo(self, api):
        resposta = api.app.openapi()["paths"]["/api/v1/files/{file_id}"]["get"]["responses"]["200"]
        assert set(resposta["content"]) == {
            "application/pdf",
            "image/jpeg",
            "image/png",
            "image/webp",
        }

    def test_o_registro_do_envio_expoe_o_tipo_como_enum_fechado(self, api):
        saida = api.app.openapi()["components"]["schemas"]["FileAssetOut"]
        assert saida["properties"]["content_type"]["$ref"].endswith("/FileKind")
        assert api.app.openapi()["components"]["schemas"]["FileKind"]["enum"] == [
            "application/pdf",
            "image/jpeg",
            "image/png",
            "image/webp",
        ]
