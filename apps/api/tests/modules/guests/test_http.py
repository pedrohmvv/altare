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


def test_a_lista_comeca_vazia(api):
    assert api.noivo.get(BASE).json() == {"households": []}


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
    assert excluida.json() == {"households": []}
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
