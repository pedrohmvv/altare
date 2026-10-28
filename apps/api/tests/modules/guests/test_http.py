import logging
from uuid import uuid4

import pytest

BASE = "/api/v1/guests"
# Valores que fazem as vezes de dado pessoal de convidado: nenhum pode ir para log nem para URL.
SENTINELA_NOME = "Convidado Exemplo Sentinela"
SENTINELA_FONE = "(11) 98888-7777"
SENTINELA_EMAIL = "sentinela@exemplo.invalid"


def nucleo(corpo, nome):
    return next(h for h in corpo["households"] if h["name"] == nome)


def pessoa(corpo, nome):
    return next(g for h in corpo["households"] for g in h["guests"] if g["name"] == nome)


def post_nucleo(client, nome="Família Exemplo", primeira="Convidado Exemplo A", **extra):
    return client.post(
        f"{BASE}/households",
        json={
            "household": {"name": nome, "side": "Comum", **extra},
            "first_guest": {"name": primeira},
        },
    )


def post_pessoa(client, household, nome, **campos):
    return client.post(f"{BASE}/households/{household['id']}/guests", json={"name": nome, **campos})


def mudar_status(client, guest, status, motivo=None):
    return client.put(
        f"{BASE}/people/{guest['id']}/status",
        json={"status": status, "reason": motivo, "version": guest["version"]},
    )


def test_so_com_sessao(api):
    assert api.anonimo.get(BASE).status_code == 401
    assert api.anonimo.post(f"{BASE}/households", json={}).status_code == 401
    assert api.anonimo.get(f"{BASE}/people/{uuid4()}/history").status_code == 401


def test_mutacao_sem_o_header_anti_csrf_e_recusada(api):
    resposta = api.sem_csrf.post(f"{BASE}/households", json={})
    assert (resposta.status_code, resposta.json()["code"]) == (403, "csrf_missing")


def test_a_lista_comeca_vazia_com_contadores_zerados_e_configuracoes_vazias(api):
    corpo = api.noivo.get(BASE).json()

    assert corpo["households"] == []
    assert corpo["headcount"]["total_nominal"] == {
        "adults": 0,
        "paying_children": 0,
        "exempt_children": 0,
        "total": 0,
    }
    assert corpo["headcount"]["weighted_rounded_up"] is None
    assert corpo["settings"] == {
        "weights": None,
        "exempt_until_age": None,
        "paying_until_age": None,
        "version": 1,
    }


def test_criar_o_nucleo_com_a_primeira_pessoa_devolve_a_lista(api):  # F-CNV-01
    resposta = post_nucleo(
        api.noivo, street="Rua Exemplo", number="100", state="SP", postal_code="00000-000"
    )

    assert resposta.status_code == 201
    corpo = resposta.json()
    familia = nucleo(corpo, "Família Exemplo")
    assert (familia["side"], familia["street"], familia["postal_code"]) == (
        "Comum",
        "Rua Exemplo",
        "00000-000",
    )
    assert [g["name"] for g in familia["guests"]] == ["Convidado Exemplo A"]
    assert familia["summary"] == {
        "total": 1,
        "confirmed": 0,
        "invited": 0,
        "draft": 1,
        "declined": 0,
    }
    assert (familia["version"], familia["guests"][0]["version"]) == (1, 1)


def test_o_cadastro_rapido_em_sequencia_e_o_telefone_vira_link(api):  # F-CNV-01
    familia = nucleo(post_nucleo(api.noivo).json(), "Família Exemplo")

    resposta = post_pessoa(api.noiva, familia, "Convidado Exemplo B", phone="(11) 91234-5678")

    assert resposta.status_code == 201
    segunda = pessoa(resposta.json(), "Convidado Exemplo B")
    assert segunda["phone"] == "(11) 91234-5678"
    assert segunda["whatsapp_url"] == "https://wa.me/5511912345678"
    assert len(nucleo(resposta.json(), "Família Exemplo")["guests"]) == 2


def test_nome_repetido_de_nucleo_da_409_com_mensagem_acionavel(api):  # F-CNV-01
    post_nucleo(api.noivo, "Família Exemplo")

    resposta = post_nucleo(api.noiva, " FAMÍLIA  exemplo ")

    corpo = resposta.json()
    assert (resposta.status_code, corpo["code"]) == (409, "duplicate_household_name")
    assert "Escolham outro" in corpo["detail"]


def test_telefone_invalido_da_422_sem_repetir_o_valor(api):
    familia = nucleo(post_nucleo(api.noivo).json(), "Família Exemplo")

    resposta = post_pessoa(api.noivo, familia, "Convidado Exemplo B", phone="12345")

    corpo = resposta.json()
    assert (resposta.status_code, corpo["code"]) == (422, "invalid_phone")
    assert "12345" not in corpo["detail"]


def test_editar_com_versao_velha_da_409_e_nao_grava(api):
    familia = nucleo(post_nucleo(api.noivo).json(), "Família Exemplo")
    corpo = {"name": "Família Exemplo", "side": "Noiva", "version": familia["version"]}
    api.noivo.put(f"{BASE}/households/{familia['id']}", json=corpo)

    resposta = api.noiva.put(f"{BASE}/households/{familia['id']}", json=corpo)

    assert (resposta.status_code, resposta.json()["code"]) == (409, "version_conflict")


def test_status_motivo_e_historico_com_o_perfil_da_sessao(api):  # F-CNV-04
    corpo = post_nucleo(api.noivo).json()
    guest = pessoa(corpo, "Convidado Exemplo A")

    resposta = mudar_status(api.noiva, guest, "Não irá", "Viagem")

    atual = pessoa(resposta.json(), "Convidado Exemplo A")
    assert (atual["status"], atual["decline_reason"]) == ("Não irá", "Viagem")
    historico = api.noivo.get(f"{BASE}/people/{guest['id']}/history").json()
    assert [(h["from_status"], h["to_status"], h["reason"], h["profile"]) for h in historico] == [
        ("Rascunho", "Não irá", "Viagem", "Noiva")
    ]


def test_motivo_com_outro_status_da_422(api):
    guest = pessoa(post_nucleo(api.noivo).json(), "Convidado Exemplo A")

    resposta = mudar_status(api.noivo, guest, "Confirmado", "Viagem")

    assert (resposta.status_code, resposta.json()["code"]) == (422, "invalid_guest_value")


def test_acompanhante_mover_excluir_e_restaurar(api):
    a = nucleo(post_nucleo(api.noivo, "Família Exemplo A").json(), "Família Exemplo A")
    post_pessoa(api.noivo, a, "Convidado Exemplo B")
    b = nucleo(
        post_nucleo(api.noivo, "Família Exemplo B", "Convidado Exemplo C").json(),
        "Família Exemplo B",
    )
    titular = pessoa(api.noivo.get(BASE).json(), "Convidado Exemplo A")
    comp = api.noivo.post(f"{BASE}/people/{titular['id']}/companion", json={"name": None})
    assert comp.status_code == 201

    movido = api.noivo.put(
        f"{BASE}/people/{titular['id']}/household",
        json={"household_id": b["id"], "version": titular["version"]},
    )
    nomes = [g["name"] for g in nucleo(movido.json(), "Família Exemplo B")["guests"]]
    assert nomes == ["Convidado Exemplo C", "Convidado Exemplo A", None]

    atual = pessoa(movido.json(), "Convidado Exemplo A")
    sem_escolha = api.noivo.delete(
        f"{BASE}/people/{atual['id']}", params={"version": atual["version"]}
    )
    assert (sem_escolha.status_code, sem_escolha.json()["code"]) == (
        422,
        "companion_choice_required",
    )
    excluido = api.noivo.delete(
        f"{BASE}/people/{atual['id']}", params={"version": atual["version"], "companion": "delete"}
    )
    assert [g["name"] for g in nucleo(excluido.json(), "Família Exemplo B")["guests"]] == [
        "Convidado Exemplo C"
    ]
    restaurado = api.noivo.post(f"{BASE}/people/{atual['id']}/restore")
    assert len(nucleo(restaurado.json(), "Família Exemplo B")["guests"]) == 3


def test_excluir_o_nucleo_e_restaurar(api):  # F-CNV-01
    familia = nucleo(post_nucleo(api.noivo).json(), "Família Exemplo")

    excluida = api.noivo.delete(
        f"{BASE}/households/{familia['id']}", params={"version": familia["version"]}
    )
    assert excluida.json()["households"] == []
    restaurada = api.noivo.post(f"{BASE}/households/{familia['id']}/restore")
    assert [h["name"] for h in restaurada.json()["households"]] == ["Família Exemplo"]


def test_a_ultima_pessoa_nao_sai(api):
    guest = pessoa(post_nucleo(api.noivo).json(), "Convidado Exemplo A")

    resposta = api.noivo.delete(
        f"{BASE}/people/{guest['id']}", params={"version": guest["version"]}
    )

    assert (resposta.status_code, resposta.json()["code"]) == (422, "last_guest_in_household")


def test_o_contrato_declara_todos_os_campos_de_saida_como_obrigatorios(api):
    esquemas = api.app.openapi()["components"]["schemas"]
    for nome in (
        "GuestListOut",
        "HouseholdOut",
        "HouseholdSummaryOut",
        "GuestOut",
        "GuestStatusChangeOut",
        "HeadcountOut",
        "BandCountsOut",
        "GuestSettingsOut",
        "WeightsOut",
    ):
        esquema = esquemas[nome]
        assert set(esquema["required"]) == set(esquema["properties"]), nome


def test_operation_ids_estaveis(api):
    ids = {
        op["operationId"]
        for caminho, metodos in api.app.openapi()["paths"].items()
        if caminho.startswith(BASE)
        for op in metodos.values()
    }
    assert ids == {
        "read_guest_list",
        "create_household",
        "update_household",
        "delete_household",
        "restore_household",
        "add_guest",
        "add_companion",
        "update_guest",
        "change_guest_status",
        "move_guest",
        "delete_guest",
        "restore_guest",
        "list_guest_status_history",
        "update_guest_settings",
        "record_household_invite",
        "clear_household_invite",
        "export_guests",
    }


def test_nenhuma_rota_leva_dado_pessoal_na_query(api):
    # O log de acesso grava a query string: só a versão e a escolha do acompanhante podem ir nela.
    permitidos = {"version", "companion"}
    for caminho, metodos in api.app.openapi()["paths"].items():
        if not caminho.startswith(BASE):
            continue
        for operacao in metodos.values():
            em_query = {p["name"] for p in operacao.get("parameters", []) if p["in"] == "query"}
            assert em_query <= permitidos, caminho


def test_as_respostas_com_dado_pessoal_nao_podem_ser_guardadas_em_cache(api):
    leitura = api.noivo.get(BASE)
    escrita = post_nucleo(api.noivo)

    assert leitura.headers["cache-control"] == "private, no-store"
    assert escrita.headers["cache-control"] == "private, no-store"


def test_nenhum_registro_de_log_leva_dado_pessoal(api, caplog):
    caplog.set_level(logging.DEBUG)
    familia = nucleo(
        post_nucleo(api.noivo, SENTINELA_NOME, SENTINELA_NOME, note=SENTINELA_NOME).json(),
        SENTINELA_NOME,
    )
    post_pessoa(
        api.noiva,
        familia,
        "Convidado Exemplo B",
        phone=SENTINELA_FONE,
        email=SENTINELA_EMAIL,
        dietary_restriction=SENTINELA_NOME,
    )
    post_nucleo(api.noivo, SENTINELA_NOME)  # 409
    post_pessoa(api.noivo, familia, SENTINELA_NOME, phone="123")  # 422
    api.noivo.put(
        f"{BASE}/households/{uuid4()}", json={"name": SENTINELA_NOME, "side": "Comum", "version": 1}
    )
    guest = pessoa(api.noivo.get(BASE).json(), SENTINELA_NOME)
    mudar_status(api.noiva, guest, "Não irá", SENTINELA_NOME)
    api.noivo.delete(f"{BASE}/people/{guest['id']}", params={"version": guest["version"]})

    texto = "\n".join(f"{r.getMessage()} {r.args!r}" for r in caplog.records)
    for sentinela in (SENTINELA_NOME, "98888", SENTINELA_EMAIL):
        assert sentinela not in texto


@pytest.mark.parametrize(("metodo", "caminho"), [("get", ""), ("post", "/households")])
def test_o_servidor_nao_ecoa_o_corpo_na_validacao(api, metodo, caminho):
    resposta = getattr(api.noivo, metodo)(
        f"{BASE}{caminho}", **({"json": {"x": SENTINELA_NOME}} if metodo == "post" else {})
    )
    assert SENTINELA_NOME not in resposta.text


def put_configuracoes(client, versao, pesos=None, isenta=None, pagante=None):
    return client.put(
        f"{BASE}/settings",
        json={
            "weights": pesos,
            "exempt_until_age": isenta,
            "paying_until_age": pagante,
            "version": versao,
        },
    )


SPEC_WEIGHTS = {
    "certain_pct": 100,
    "probable_pct": 70,
    "phase_2_pct": 30,
}  # os da spec, não do casal


def test_o_ponderado_vem_em_centesimos_e_arredondado_para_cima(api):  # F-CNV-06
    corpo = post_nucleo(api.noivo, primeira="Convidado Exemplo 1").json()
    familia = nucleo(corpo, "Família Exemplo")
    for nome, prob in (("Convidado Exemplo 2", "Certeza"), ("Convidado Exemplo 3", "Provável")):
        post_pessoa(api.noivo, familia, nome, probability=prob)
    post_pessoa(api.noivo, familia, "Convidado Exemplo 4", probability="Provável")
    lista = post_pessoa(api.noivo, familia, "Convidado Exemplo 5", probability="Fase 2").json()
    assert lista["headcount"]["weighted_rounded_up"] is None  # "defina os pesos"

    resposta = put_configuracoes(api.noiva, lista["settings"]["version"], SPEC_WEIGHTS)

    assert resposta.status_code == 200
    contagem = resposta.json()["headcount"]
    # 1 Provável (padrão) + Certeza + 2 Provável + Fase 2 = 0,7 + 1 + 0,7 + 0,7 + 0,3
    assert contagem["weighted_adults_hundredths"] == 340
    assert contagem["weighted_rounded_up"] == 4
    assert resposta.json()["settings"]["weights"] == SPEC_WEIGHTS
    assert resposta.json()["settings"]["version"] == 2


def test_confirmar_alguem_atualiza_os_contadores_na_mesma_resposta(api):  # F-CNV-06
    familia = nucleo(post_nucleo(api.noivo).json(), "Família Exemplo")
    lista = post_pessoa(api.noivo, familia, "Convidado Exemplo B").json()
    put_configuracoes(api.noivo, lista["settings"]["version"], SPEC_WEIGHTS)
    guest = pessoa(api.noivo.get(BASE).json(), "Convidado Exemplo B")

    corpo = mudar_status(api.noiva, guest, "Confirmado").json()

    assert corpo["headcount"]["confirmed"]["adults"] == 1
    assert corpo["headcount"]["weighted_adults_hundredths"] == 170  # 0,7 + 100% do confirmado


def test_peso_fora_de_0_a_100_e_limites_incoerentes_dao_422(api):
    sem_peso = put_configuracoes(api.noivo, 1, {**SPEC_WEIGHTS, "probable_pct": 101})
    sem_limite = put_configuracoes(api.noivo, 1, isenta=8, pagante=5)

    assert (sem_peso.status_code, sem_peso.json()["code"]) == (422, "invalid_weights")
    assert (sem_limite.status_code, sem_limite.json()["code"]) == (422, "invalid_age_limits")


def test_pesos_incompletos_nao_passam_pelo_contrato(api):
    resposta = put_configuracoes(api.noivo, 1, {"certain_pct": 100})

    assert (resposta.status_code, resposta.json()["code"]) == (422, "validation_error")


def test_configuracoes_com_versao_velha_dao_409(api):
    put_configuracoes(api.noivo, 1, SPEC_WEIGHTS)

    resposta = put_configuracoes(api.noiva, 1, SPEC_WEIGHTS)

    assert (resposta.status_code, resposta.json()["code"]) == (409, "version_conflict")


def test_a_idade_sugere_a_faixa_sem_mudar_a_pessoa(api):  # F-CNV-03
    familia = nucleo(post_nucleo(api.noivo).json(), "Família Exemplo")
    lista = post_pessoa(
        api.noivo, familia, "Convidado Exemplo B", band="Criança pagante", age=4
    ).json()
    assert pessoa(lista, "Convidado Exemplo B")["suggested_band"] is None

    corpo = put_configuracoes(api.noivo, lista["settings"]["version"], isenta=5, pagante=12).json()

    crianca = pessoa(corpo, "Convidado Exemplo B")
    assert (crianca["band"], crianca["suggested_band"]) == ("Criança pagante", "Criança isenta")


def put_envio(client, nucleo, dia="2026-10-20", canal="WhatsApp", mover=False, versao=None):
    return client.put(
        f"{BASE}/households/{nucleo['id']}/invite",
        json={
            "sent_on": dia,
            "channel": canal,
            "move_drafts": mover,
            "version": nucleo["version"] if versao is None else versao,
        },
    )


def test_o_nucleo_novo_nao_tem_convite_enviado(api):  # F-CNV-05
    familia = nucleo(post_nucleo(api.noivo).json(), "Família Exemplo")

    assert (familia["invite_sent_on"], familia["invite_channel"]) == (None, None)


def test_registrar_o_envio_devolve_a_lista_e_aceitar_a_oferta_move_os_rascunhos(api):  # F-CNV-05
    familia = nucleo(post_nucleo(api.noivo).json(), "Família Exemplo")
    post_pessoa(api.noivo, familia, "Convidado Exemplo B")
    familia = nucleo(api.noivo.get(BASE).json(), "Família Exemplo")

    resposta = put_envio(api.noiva, familia, canal="Impresso", mover=True)

    assert resposta.status_code == 200
    enviado = nucleo(resposta.json(), "Família Exemplo")
    assert (enviado["invite_sent_on"], enviado["invite_channel"]) == ("2026-10-20", "Impresso")
    assert {g["status"] for g in enviado["guests"]} == {"Convidado"}
    assert enviado["version"] == familia["version"] + 1


def test_recusar_a_oferta_mantem_os_status(api):  # F-CNV-05, critério de aceite
    familia = nucleo(post_nucleo(api.noivo).json(), "Família Exemplo")

    resposta = put_envio(api.noivo, familia, mover=False)

    assert {g["status"] for g in nucleo(resposta.json(), "Família Exemplo")["guests"]} == {
        "Rascunho"
    }


def test_limpar_o_envio_nao_reverte_status(api):  # F-CNV-05, regra 3
    familia = nucleo(post_nucleo(api.noivo).json(), "Família Exemplo")
    enviado = nucleo(put_envio(api.noivo, familia, mover=True).json(), "Família Exemplo")

    resposta = api.noivo.delete(
        f"{BASE}/households/{enviado['id']}/invite", params={"version": enviado["version"]}
    )

    limpo = nucleo(resposta.json(), "Família Exemplo")
    assert (limpo["invite_sent_on"], limpo["invite_channel"]) == (None, None)
    assert limpo["guests"][0]["status"] == "Convidado"


def test_data_futura_da_422_e_canal_desconhecido_tambem(api):
    familia = nucleo(post_nucleo(api.noivo).json(), "Família Exemplo")

    futura = put_envio(api.noivo, familia, dia="2999-01-01")
    canal = put_envio(api.noivo, familia, canal="Telegrama")

    assert (futura.status_code, futura.json()["code"]) == (422, "invalid_invite")
    assert (canal.status_code, canal.json()["code"]) == (422, "validation_error")


def test_envio_com_versao_velha_da_409(api):
    familia = nucleo(post_nucleo(api.noivo).json(), "Família Exemplo")
    put_envio(api.noivo, familia)

    resposta = put_envio(api.noiva, familia)

    assert (resposta.status_code, resposta.json()["code"]) == (409, "version_conflict")


def test_o_contrato_declara_o_convite_como_obrigatorio_na_saida(api):
    esquema = api.app.openapi()["components"]["schemas"]["HouseholdOut"]

    assert {"invite_sent_on", "invite_channel"} <= set(esquema["required"])
