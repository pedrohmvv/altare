"""As janelas, o prazo efetivo, os Modos Sem/Com Data e a prévia de mudar a data (F-CRN-05): a
fixture com migration real e a data do casamento pelas Definições Base (`wedding`), sem fake."""

from datetime import UTC, datetime

import pytest
from tests.modules.schedule.catalog import marco_id
from tests.modules.schedule.test_http import (
    BASE,
    classificar,
    classificar_todas,
    concluir,
    cronograma,
    editar,
    marco,
)

DATA = "/api/v1/wedding/baseline/date"
PREVIA = f"{BASE}/date-preview"
DATA_DE_ACEITE = "2027-06-12"  # a data fictícia de F-CRN-05


@pytest.fixture
def api(api_clock):
    return api_clock


def definir_data(client, exact, status="Definido"):
    versao = client.get("/api/v1/wedding/baseline").json()["date"]["version"]
    valor = {"kind": "exata", "exact": exact} if exact else {"kind": "nenhuma"}
    resposta = client.put(
        DATA, json={"value": valor, "status": status, "note": None, "version": versao}
    )
    assert resposta.status_code == 200, resposta.text


def janela(client, codigo, inicio, fim, unidade="meses", *, versao=None):
    atual = versao if versao is not None else marco(cronograma(client), codigo)["version"]
    corpo = {"start_before": inicio, "end_before": fim, "unit": unidade, "version": atual}
    return client.put(f"{BASE}/milestones/{marco_id(codigo)}/window", json=corpo)


def previa(client, exact=None):
    resposta = client.get(PREVIA, params={"exact": exact} if exact else None)
    assert resposta.status_code == 200, resposta.text
    return resposta.json()


# --- contrato --------------------------------------------------------------------------------


def test_operation_ids_estaveis(api):
    caminhos = api.app.openapi()["paths"]
    assert caminhos[f"{BASE}/date-preview"]["get"]["operationId"] == "preview_date_change"
    janela_put = caminhos[f"{BASE}/milestones/{{milestone_id}}/window"]["put"]
    assert janela_put["operationId"] == "update_milestone_window"


def test_o_contrato_de_saida_da_janela_e_da_previa_tem_tudo_obrigatorio_e_sem_padrao(api):
    esquemas = api.app.openapi()["components"]["schemas"]
    for nome in (
        "MilestoneOut",
        "MilestoneWindowOut",
        "DatePreviewOut",
        "DateChangeOut",
        "DateRangeOut",
    ):
        esquema = esquemas[nome]
        assert set(esquema["required"]) == set(esquema["properties"]), nome
        assert not any("default" in p for p in esquema["properties"].values()), nome


def test_o_contrato_diz_que_target_date_e_so_o_prazo_manual(api):
    marco_out = api.app.openapi()["components"]["schemas"]["MilestoneOut"]["properties"]
    descricao = marco_out["target_date"]["description"]
    assert "à mão" in descricao
    assert "effective_target" in descricao
    assert "target_is_manual" not in marco_out


def test_a_unidade_e_o_modo_sao_enums_fechados_no_contrato(api):
    esquemas = api.app.openapi()["components"]["schemas"]
    assert esquemas["WindowUnit"]["enum"] == ["meses", "semanas"]
    assert esquemas["DateMode"]["enum"] == ["sem_data", "com_data"]


def test_a_previa_pede_sessao_e_a_janela_pede_sessao_e_o_header_anti_csrf(api):
    alvo = f"{BASE}/milestones/{marco_id('C06')}/window"
    corpo = {"start_before": 12, "end_before": 8, "unit": "meses", "version": 1}
    assert api.anonimo.get(PREVIA).status_code == 401
    assert api.anonimo.put(alvo, json=corpo).status_code == 401
    sem = api.sem_csrf.put(alvo, json=corpo)
    assert (sem.status_code, sem.json()["code"]) == (403, "csrf_missing")


# --- Modo Com Data e Sem Data (critérios de aceite de F-CRN-05) --------------------------------


def test_sem_data_a_janela_sugerida_vem_em_deslocamentos_e_nenhuma_data_e_calculada(api):
    c06 = marco(cronograma(api.noivo), "C06")
    assert c06["window"] == {
        "start_before": 14,
        "end_before": 10,
        "unit": "meses",
        "is_suggestion": True,
    }
    assert (c06["window_start"], c06["window_end"]) == (None, None)
    assert (c06["target_date"], c06["effective_target"], c06["days_left"]) == (None, None, None)
    assert marco(cronograma(api.noivo), "C01")["window"] is None


def test_com_data_fechar_o_espaco_tem_a_janela_e_o_prazo_efetivo_da_data_de_aceite(api):
    definir_data(api.noivo, DATA_DE_ACEITE)
    c06 = marco(cronograma(api.noivo), "C06")
    assert (c06["window_start"], c06["window_end"]) == ("2026-04-12", "2026-08-12")
    assert c06["effective_target"] == "2026-08-12"
    assert c06["target_date"] is None


def test_prazo_manual_vira_o_efetivo_e_limpa_lo_volta_a_sugestao(api):
    definir_data(api.noivo, DATA_DE_ACEITE)
    manual = editar(api.noivo, "C06", target_date="2026-07-30").json()
    c06 = marco(manual, "C06")
    assert (c06["target_date"], c06["effective_target"]) == ("2026-07-30", "2026-07-30")
    assert c06["window_end"] == "2026-08-12"
    limpo = marco(editar(api.noivo, "C06", target_date=None).json(), "C06")
    assert (limpo["target_date"], limpo["effective_target"]) == (None, "2026-08-12")


def test_voltar_ao_modo_sem_data_apaga_as_datas_e_mantem_o_prazo_manual(api):
    definir_data(api.noivo, DATA_DE_ACEITE)
    editar(api.noivo, "C06", target_date="2026-07-30")
    definir_data(api.noivo, DATA_DE_ACEITE, status="Em definição")
    c06 = marco(cronograma(api.noivo), "C06")
    assert (c06["window_start"], c06["window_end"]) == (None, None)
    assert (c06["target_date"], c06["effective_target"]) == ("2026-07-30", "2026-07-30")
    assert c06["days_left"] == (datetime(2026, 7, 30).date() - datetime(2026, 10, 27).date()).days


def test_o_fim_da_janela_vencido_atrasa_o_marco_e_a_contagem_e_negativa(api):
    classificar_todas(api.noivo)
    definir_data(api.noivo, DATA_DE_ACEITE)
    c06 = marco(cronograma(api.noivo), "C06")
    assert (c06["overdue"], c06["days_left"]) == (True, -76)
    concluir(api.noivo, "C01", "C02", "C03", "C04", "C05", "C06")
    concluido = marco(cronograma(api.noivo), "C06")
    assert (concluido["overdue"], concluido["days_left"]) == (False, None)


def test_a_contagem_regressiva_usa_o_dia_de_brasilia(api):
    editar(api.noivo, "C01", target_date="2026-10-27")
    api.clock._now = datetime(2026, 10, 27, 2, 0, tzinfo=UTC)  # 23:00 de 26/10 em Brasília
    assert marco(cronograma(api.noivo), "C01")["days_left"] == 1
    api.clock._now = datetime(2026, 10, 27, 3, 0, tzinfo=UTC)
    assert marco(cronograma(api.noivo), "C01")["days_left"] == 0


def test_data_fora_do_calendario_nao_derruba_a_leitura_e_nao_calcula_janela(api):
    # O módulo `wedding` não valida o ano da data exata: o cronograma tem de aguentar o extremo.
    definir_data(api.noivo, "0001-01-05")
    corpo = cronograma(api.noivo)
    assert corpo["has_exact_date"] is True
    c06 = marco(corpo, "C06")
    assert (c06["window_start"], c06["window_end"], c06["effective_target"]) == (None, None, None)
    assert c06["window"] is not None


# --- editar a janela --------------------------------------------------------------------------


def test_editar_a_janela_devolve_o_cronograma_inteiro_e_deixa_de_ser_sugestao(api):
    definir_data(api.noivo, DATA_DE_ACEITE)
    resposta = janela(api.noiva, "C06", 12, 8)
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert len(corpo["phases"]) == 5
    c06 = marco(corpo, "C06")
    assert c06["window"] == {
        "start_before": 12,
        "end_before": 8,
        "unit": "meses",
        "is_suggestion": False,
    }
    assert (c06["window_start"], c06["window_end"]) == ("2026-06-12", "2026-10-12")
    assert (c06["target_date"], c06["effective_target"]) == (None, "2026-10-12")
    assert c06["version"] == 2


def test_repetir_a_janela_ja_editada_nao_sobe_a_version(api):
    janela(api.noivo, "C06", 12, 8)
    repetida = janela(api.noivo, "C06", 12, 8)
    assert marco(repetida.json(), "C06")["version"] == 2


def test_a_janela_vale_sem_data_do_casamento_em_semanas_e_em_marco_sem_janela(api):
    semanas = janela(api.noivo, "C06", 6, 2, "semanas")
    assert marco(semanas.json(), "C06")["window"]["unit"] == "semanas"
    nova = marco(janela(api.noivo, "C01", 3, 1).json(), "C01")
    assert nova["window"] == {
        "start_before": 3,
        "end_before": 1,
        "unit": "meses",
        "is_suggestion": False,
    }


def test_marco_arquivado_pode_ter_a_janela_editada(api):
    classificar_todas(api.noivo)
    classificar(api.noivo, "Espaço", "Fica de fora", "Sem espaço")
    c06 = marco(janela(api.noivo, "C06", 12, 8).json(), "C06")
    assert c06["archived"] is True
    assert c06["window"]["start_before"] == 12


def test_a_janela_com_version_velha_e_conflito_409(api):
    janela(api.noivo, "C06", 12, 8)
    velha = janela(api.noiva, "C06", 6, 2, versao=1)
    assert (velha.status_code, velha.json()["code"]) == (409, "version_conflict")


def test_a_janela_de_marco_inexistente_ou_excluido_e_404(api):
    inexistente = api.noivo.put(
        f"{BASE}/milestones/00000000-0000-0000-0000-000000000099/window",
        json={"start_before": 3, "end_before": 1, "unit": "meses", "version": 1},
    )
    assert (inexistente.status_code, inexistente.json()["code"]) == (404, "not_found")
    version = marco(cronograma(api.noivo), "C06")["version"]
    api.noivo.delete(f"{BASE}/milestones/{marco_id('C06')}", params={"version": version})
    excluido = janela(api.noivo, "C06", 12, 8, versao=version)
    assert (excluido.status_code, excluido.json()["code"]) == (404, "not_found")


@pytest.mark.parametrize(
    ("inicio", "fim", "unidade"),
    [
        (3, 4, "meses"),
        (3, -1, "meses"),
        (-1, -2, "semanas"),
        (121, 0, "meses"),
        (521, 0, "semanas"),
    ],
)
def test_janela_invalida_e_422_invalid_window_com_mensagem_em_portugues(api, inicio, fim, unidade):
    resposta = janela(api.noivo, "C06", inicio, fim, unidade)
    corpo = resposta.json()
    assert (resposta.status_code, corpo["code"]) == (422, "invalid_window")
    assert "Confiram a janela" in corpo["detail"]
    assert marco(cronograma(api.noivo), "C06")["version"] == 1


def test_o_limite_exato_e_o_zero_a_zero_sao_aceitos(api):
    assert janela(api.noivo, "C06", 120, 0).status_code == 200
    assert janela(api.noivo, "C07", 520, 520, "semanas").status_code == 200
    zero = marco(janela(api.noivo, "C08", 0, 0).json(), "C08")
    assert zero["window"]["start_before"] == zero["window"]["end_before"] == 0


def test_unidade_desconhecida_e_422_de_validacao_do_pydantic(api):
    resposta = janela(api.noivo, "C06", 3, 1, "dias")
    assert (resposta.status_code, resposta.json()["code"]) == (422, "validation_error")
    sem_versao = api.noivo.put(
        f"{BASE}/milestones/{marco_id('C06')}/window",
        json={"start_before": 3, "end_before": 1, "unit": "meses"},
    )
    assert (sem_versao.status_code, sem_versao.json()["code"]) == (422, "validation_error")


# --- a prévia de mudar a data -----------------------------------------------------------------


def test_previa_com_para_com_lista_o_que_muda_e_mantem_o_de_prazo_manual(api):  # F-CRN-05, regra 4
    definir_data(api.noivo, DATA_DE_ACEITE)
    editar(api.noivo, "C07", target_date="2026-12-01")
    corpo = previa(api.noivo, "2027-07-12")
    assert (corpo["mode_before"], corpo["mode_after"]) == ("com_data", "com_data")
    c06 = next(c for c in corpo["changes"] if c["id"] == str(marco_id("C06")))
    assert c06 == {
        "id": str(marco_id("C06")),
        "title": "Fechar o Espaço",
        "window_before": {"start": "2026-04-12", "end": "2026-08-12"},
        "window_after": {"start": "2026-05-12", "end": "2026-09-12"},
        "target_before": "2026-08-12",
        "target_after": "2026-09-12",
    }
    assert str(marco_id("C07")) not in {c["id"] for c in corpo["changes"]}
    assert (len(corpo["changes"]), corpo["manual_kept"]) == (23, 1)


def test_previa_de_sem_data_para_com_data_traz_a_janela_antes_nula(api):
    corpo = previa(api.noivo, DATA_DE_ACEITE)
    assert (corpo["mode_before"], corpo["mode_after"]) == ("sem_data", "com_data")
    c06 = next(c for c in corpo["changes"] if c["id"] == str(marco_id("C06")))
    assert (c06["window_before"], c06["target_before"]) == (None, None)
    assert c06["window_after"] == {"start": "2026-04-12", "end": "2026-08-12"}
    assert c06["target_after"] == "2026-08-12"
    assert corpo["newly_overdue"] > 0


def test_previa_de_com_data_para_sem_data_traz_a_janela_depois_nula(api):
    definir_data(api.noivo, DATA_DE_ACEITE)
    corpo = previa(api.noivo)
    assert (corpo["mode_before"], corpo["mode_after"]) == ("com_data", "sem_data")
    c06 = next(c for c in corpo["changes"] if c["id"] == str(marco_id("C06")))
    assert (c06["window_after"], c06["target_after"]) == (None, None)
    assert c06["target_before"] == "2026-08-12"


def test_previa_da_mesma_data_ou_de_sem_data_para_sem_data_e_vazia(api):
    assert previa(api.noivo)["changes"] == []
    definir_data(api.noivo, DATA_DE_ACEITE)
    assert previa(api.noivo, DATA_DE_ACEITE)["changes"] == []


def test_previa_deixa_de_fora_os_concluidos_e_os_arquivados(api):
    classificar_todas(api.noivo)
    classificar(api.noivo, "Fotografia", "Fica de fora", "Sem foto")
    concluir(api.noivo, "C01", "C02", "C03", "C04", "C05", "C06")
    ids = {c["id"] for c in previa(api.noivo, DATA_DE_ACEITE)["changes"]}
    assert str(marco_id("C06")) not in ids
    assert str(marco_id("C08")) not in ids
    assert len(ids) == 22


def test_previa_so_le_nada_e_gravado(api):
    antes = (cronograma(api.noivo), api.noivo.get("/api/v1/wedding/baseline").json())
    previa(api.noivo, DATA_DE_ACEITE)
    previa(api.noivo)
    assert (cronograma(api.noivo), api.noivo.get("/api/v1/wedding/baseline").json()) == antes


@pytest.mark.parametrize("exata", ["1999-12-31", "2101-01-01"])
def test_previa_com_ano_fora_de_2000_a_2100_e_422(api, exata):
    resposta = api.noivo.get(PREVIA, params={"exact": exata})
    corpo = resposta.json()
    assert (resposta.status_code, corpo["code"]) == (422, "invalid_preview_date")
    assert corpo["detail"] == "A data do casamento precisa estar entre os anos 2000 e 2100."


def test_previa_com_data_malformada_e_422_de_validacao(api):
    resposta = api.noivo.get(PREVIA, params={"exact": "12/06/2027"})
    assert (resposta.status_code, resposta.json()["code"]) == (422, "validation_error")


def test_a_previa_nao_e_um_metodo_de_escrita(api):
    assert api.noivo.post(PREVIA).status_code == 405
