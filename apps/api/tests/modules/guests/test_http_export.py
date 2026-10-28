import csv
import io
import logging
import re
import zipfile
from uuid import uuid4

from openpyxl import load_workbook

from wedding.modules.guests.application.export_rows import HEADERS

BASE = "/api/v1/guests"
XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
SENTINELA = "Convidado Exemplo Sentinela"


def nucleo(corpo, nome):
    return next(h for h in corpo["households"] if h["name"] == nome)


def lista_de_exemplo(api):
    api.noivo.post(
        f"{BASE}/households",
        json={
            "household": {
                "name": "Família Exemplo",
                "side": "Noiva",
                "street": "Rua Exemplo",
                "number": "100",
            },
            "first_guest": {
                "name": "Convidado Exemplo A",
                "phone": "(11) 91234-5678",
                "note": "=1+1",
                "dietary_restriction": "Sem lactose",
            },
        },
    )
    familia = nucleo(api.noivo.get(BASE).json(), "Família Exemplo")
    api.noivo.post(
        f"{BASE}/households/{familia['id']}/guests",
        json={"name": "Convidado Exemplo B", "band": "Criança pagante", "age": 9},
    )
    api.noivo.post(
        f"{BASE}/households",
        json={
            "household": {"name": "Amigos Exemplo", "side": "Noivo"},
            "first_guest": {"name": "Convidado Exemplo C"},
        },
    )
    return api.noivo.get(BASE).json()


def exportar(client, formato=None, ids=None):
    corpo = {}
    if formato:
        corpo["format"] = formato
    if ids is not None:
        corpo["guest_ids"] = ids
    return client.post(f"{BASE}/exports", json=corpo)


def test_so_com_sessao_e_exige_o_header_anti_csrf(api):
    assert api.anonimo.post(f"{BASE}/exports", json={}).status_code == 401
    resposta = api.sem_csrf.post(f"{BASE}/exports", json={})
    assert (resposta.status_code, resposta.json()["code"]) == (403, "csrf_missing")


def test_o_padrao_e_excel_e_o_arquivo_vem_para_baixar_sem_dado_pessoal_no_nome(api):  # F-CNV-08
    lista_de_exemplo(api)

    resposta = exportar(api.noiva)

    assert resposta.status_code == 200
    assert resposta.headers["content-type"] == XLSX
    disposicao = resposta.headers["content-disposition"]
    assert disposicao.startswith("attachment;")
    assert re.fullmatch(
        r'attachment; filename="lista-de-convidados-\d{4}-\d{2}-\d{2}\.xlsx"', disposicao
    )
    assert "Exemplo" not in disposicao
    assert resposta.headers["cache-control"] == "private, no-store"
    assert resposta.headers["x-content-type-options"] == "nosniff"
    assert zipfile.is_zipfile(io.BytesIO(resposta.content))


def test_o_excel_traz_uma_linha_por_pessoa_e_a_formula_fica_texto(api):  # F-CNV-08
    lista_de_exemplo(api)

    planilha = load_workbook(io.BytesIO(exportar(api.noivo, "xlsx").content)).active
    assert planilha is not None

    assert [c.value for c in planilha[1]] == list(HEADERS)
    assert planilha.max_row == 4
    nomes = sorted(str(planilha.cell(row=r, column=3).value) for r in range(2, 5))
    assert nomes == ["Convidado Exemplo A", "Convidado Exemplo B", "Convidado Exemplo C"]
    observacao = next(
        planilha.cell(row=r, column=HEADERS.index("Observação") + 1)
        for r in range(2, 5)
        if planilha.cell(row=r, column=3).value == "Convidado Exemplo A"
    )
    assert (observacao.value, observacao.data_type) == ("=1+1", "s")


def test_o_csv_vem_em_utf8_com_bom_e_ponto_e_virgula_e_neutraliza_a_formula(api):  # F-CNV-08
    lista_de_exemplo(api)

    resposta = exportar(api.noivo, "csv")

    assert resposta.headers["content-type"] == "text/csv; charset=utf-8"
    assert resposta.headers["content-disposition"].endswith('.csv"')
    assert resposta.content.startswith(b"\xef\xbb\xbf")
    tabela = list(csv.reader(io.StringIO(resposta.content.decode("utf-8-sig")), delimiter=";"))
    assert tabela[0] == list(HEADERS)
    assert len(tabela) == 4
    titular = dict(
        zip(HEADERS, next(r for r in tabela[1:] if r[2] == "Convidado Exemplo A"), strict=True)
    )
    assert titular["Observação"] == "'=1+1"
    assert titular["Telefone"] == "(11) 91234-5678"
    assert titular["Endereço do núcleo"] == "Rua Exemplo, 100"
    assert titular["Núcleo"] == "Família Exemplo"


def test_so_leva_as_pessoas_que_estao_na_tela(api):  # F-CNV-08, critério do filtro "Lado Noiva"
    lista = lista_de_exemplo(api)
    da_noiva = [g["id"] for g in nucleo(lista, "Família Exemplo")["guests"]]

    resposta = exportar(api.noivo, "csv", da_noiva)

    tabela = list(csv.reader(io.StringIO(resposta.content.decode("utf-8-sig")), delimiter=";"))
    assert len(tabela) == 3
    assert {r[0] for r in tabela[1:]} == {"Família Exemplo"}


def test_pessoa_desconhecida_e_recusada_para_a_contagem_da_tela_nao_divergir(api):
    lista_de_exemplo(api)

    resposta = exportar(api.noivo, "xlsx", [str(uuid4())])

    assert (resposta.status_code, resposta.json()["code"]) == (404, "not_found")


def test_lista_vazia_de_ids_leva_so_o_cabecalho(api):
    lista_de_exemplo(api)

    tabela = list(
        csv.reader(
            io.StringIO(exportar(api.noivo, "csv", []).content.decode("utf-8-sig")), delimiter=";"
        )
    )

    assert tabela == [list(HEADERS)]


def test_formato_desconhecido_da_422(api):
    resposta = api.noivo.post(f"{BASE}/exports", json={"format": "pdf"})

    assert (resposta.status_code, resposta.json()["code"]) == (422, "validation_error")


def test_nenhum_registro_de_log_leva_dado_pessoal_na_exportacao(api, caplog):
    caplog.set_level(logging.DEBUG)
    api.noivo.post(
        f"{BASE}/households",
        json={
            "household": {"name": SENTINELA, "side": "Comum"},
            "first_guest": {"name": SENTINELA, "email": "sentinela@exemplo.invalid"},
        },
    )

    exportar(api.noivo, "xlsx")
    exportar(api.noivo, "csv")
    exportar(api.noivo, "csv", [str(uuid4())])

    texto = "\n".join(f"{r.getMessage()} {r.args!r}" for r in caplog.records)
    assert SENTINELA not in texto
    assert "sentinela@exemplo.invalid" not in texto


def test_a_exportacao_nao_tem_query_e_o_contrato_declara_o_arquivo(api):
    operacao = api.app.openapi()["paths"][f"{BASE}/exports"]["post"]

    assert operacao["operationId"] == "export_guests"
    assert not [p for p in operacao.get("parameters", []) if p["in"] == "query"]
    conteudo = operacao["responses"]["200"]["content"]
    assert XLSX in conteudo
    assert "text/csv; charset=utf-8" in conteudo
