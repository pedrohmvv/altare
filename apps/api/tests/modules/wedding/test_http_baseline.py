import pytest

BASE = "/api/v1/wedding/baseline"


def _put(client, campo, valor, *, versao=1, status="Definido", nota=None, **extra):
    return client.put(
        f"{BASE}/{campo}",
        json={"value": valor, "status": status, "note": nota, "version": versao, **extra},
    )


def test_so_com_sessao(api):
    assert api.anonimo.get(BASE).status_code == 401
    assert _put(api.anonimo, "city", "Cidade Exemplo").status_code == 401
    assert api.anonimo.get(f"{BASE}/changes").status_code == 401


def test_casamento_novo_mostra_tudo_vazio_e_em_definicao(api):  # F-PLN-01
    resposta = api.noivo.get(BASE)
    assert resposta.status_code == 200
    quadro = resposta.json()
    assert set(quadro) == {"date", "city", "format", "size", "ceiling", "ceremony"}
    for campo in quadro.values():
        assert campo["status"] == "Em definição"
        assert campo["note"] is None
        assert campo["version"] == 1
    assert quadro["date"]["value"]["kind"] == "nenhuma"
    assert quadro["city"]["value"] is None
    assert quadro["size"]["value"] == {"minimum": None, "maximum": None}
    assert quadro["ceiling"]["value"] == {"cents": None}
    assert quadro["ceremony"]["value"] == {"kinds": [], "detail": None}


def test_definir_a_cidade_devolve_o_quadro_com_a_versao_nova(api):
    resposta = _put(api.noivo, "city", "  Cidade Exemplo ", nota="decidimos")
    assert resposta.status_code == 200
    cidade = resposta.json()["city"]
    assert cidade == {
        "status": "Definido",
        "value": "Cidade Exemplo",
        "note": "decidimos",
        "version": 2,
    }
    assert api.noiva.get(BASE).json()["city"]["value"] == "Cidade Exemplo"


def test_teto_em_reais_e_gravado_em_centavos(api):  # F-PLN-01: R$ 28.000,00 → 2800000
    resposta = _put(api.noiva, "ceiling", {"cents": 2_800_000})
    assert resposta.json()["ceiling"]["value"] == {"cents": 2_800_000}


def test_data_exata_e_janela(api):
    exata = _put(api.noivo, "date", {"kind": "exata", "exact": "2027-05-01"})
    assert exata.json()["date"]["value"] == {
        "kind": "exata",
        "window_start": None,
        "window_end": None,
        "label": None,
        "exact": "2027-05-01",
    }
    janela = _put(
        api.noivo,
        "date",
        {
            "kind": "janela",
            "window_start": {"year": 2027, "month": 3},
            "window_end": {"year": 2027, "month": 5},
            "label": "outono",
        },
        versao=2,
    )
    valor = janela.json()["date"]["value"]
    assert valor["kind"] == "janela"
    assert valor["window_end"] == {"year": 2027, "month": 5}
    assert valor["exact"] is None


def test_sem_data_limpa_o_campo_e_volta_a_em_definicao(api):
    _put(api.noivo, "date", {"kind": "exata", "exact": "2027-05-01"})
    resposta = _put(api.noivo, "date", {"kind": "nenhuma"}, versao=2, status="Em definição")
    campo = resposta.json()["date"]
    assert campo["value"]["kind"] == "nenhuma"
    assert campo["status"] == "Em definição"


def test_porte_e_cerimonia(api):
    porte = _put(api.noivo, "size", {"minimum": 80, "maximum": 120})
    assert porte.json()["size"]["value"] == {"minimum": 80, "maximum": 120}
    cerimonia = _put(api.noivo, "ceremony", {"kinds": ["Civil", "Religiosa"], "detail": "detalhe"})
    assert cerimonia.json()["ceremony"]["value"] == {
        "kinds": ["Civil", "Religiosa"],
        "detail": "detalhe",
    }


def test_definido_sem_valor_diz_o_que_fazer(api):  # F-PLN-01: mensagem acionável
    resposta = _put(api.noivo, "city", None)
    assert resposta.status_code == 422
    corpo = resposta.json()
    assert corpo["code"] == "baseline_value_required"
    assert "Preencha o valor" in corpo["detail"]
    assert api.noivo.get(BASE).json()["city"]["version"] == 1


@pytest.mark.parametrize(
    ("campo", "valor"),
    [
        ("city", "x" * 81),
        ("city", "   "),
        ("size", {"minimum": 120, "maximum": 80}),
        ("size", {"minimum": 80, "maximum": None}),
        ("ceiling", {"cents": 0}),
        ("ceiling", {"cents": -5}),
        (
            "date",
            {
                "kind": "janela",
                "window_start": {"year": 2027, "month": 6},
                "window_end": {"year": 2027, "month": 1},
            },
        ),
        ("date", {"kind": "janela"}),
        ("date", {"kind": "exata"}),
    ],
)
def test_valor_fora_das_regras_vira_422_com_code_estavel(api, campo, valor):
    resposta = _put(api.noivo, campo, valor)
    assert resposta.status_code == 422
    assert resposta.json()["code"] in {"invalid_baseline_value", "baseline_value_required"}


def test_tipo_de_cerimonia_desconhecido_e_recusado_com_o_campo(api):
    resposta = _put(api.noivo, "ceremony", {"kinds": ["Outra"]})
    assert resposta.status_code == 422
    assert resposta.json()["code"] == "validation_error"


def test_versao_velha_da_409_e_nao_grava(api):
    _put(api.noivo, "city", "A Exemplo")
    resposta = _put(api.noiva, "city", "B Exemplo", versao=1)
    assert resposta.status_code == 409
    assert resposta.json()["code"] == "version_conflict"
    assert api.noiva.get(BASE).json()["city"]["value"] == "A Exemplo"


def test_versao_e_obrigatoria(api):
    resposta = api.noivo.put(f"{BASE}/city", json={"value": "A Exemplo", "status": "Definido"})
    assert resposta.status_code == 422
    assert resposta.json()["code"] == "validation_error"


def test_mutacao_sem_o_header_anti_csrf_e_recusada(api):
    resposta = api.sem_csrf.put(
        f"{BASE}/city", json={"value": "A", "status": "Definido", "version": 1}
    )
    assert resposta.status_code == 403
    assert resposta.json()["code"] == "csrf_missing"


def test_autoria_vem_da_sessao_e_nunca_do_corpo(api):
    _put(api.noivo, "city", "A Exemplo", profile="Noiva", author="Noiva", by="Noiva")
    historico = api.noiva.get(f"{BASE}/changes").json()
    assert [mudanca["by"] for mudanca in historico] == ["Noivo"]


def test_historico_traz_antes_depois_e_quem_mudou_do_mais_novo_para_o_mais_antigo(api):
    _put(api.noivo, "date", {"kind": "exata", "exact": "2027-05-01"})
    _put(api.noiva, "date", {"kind": "exata", "exact": "2027-06-05"}, versao=2)
    recente, antiga = api.noivo.get(f"{BASE}/changes").json()
    assert recente["field"] == "date"
    assert recente["by"] == "Noiva"
    assert recente["before"]["value"]["exact"] == "2027-05-01"  # o valor anterior fica registrado
    assert recente["after"]["value"]["exact"] == "2027-06-05"
    assert recente["before"]["status"] == antiga["after"]["status"] == "Definido"
    assert antiga["by"] == "Noivo"
    assert antiga["before"]["value"] is None
    assert recente["at"] >= antiga["at"]


def test_historico_aceita_limite_e_recusa_limite_invalido(api):
    for versao, cidade in enumerate(["A Exemplo", "B Exemplo", "C Exemplo"], start=1):
        _put(api.noivo, "city", cidade, versao=versao)
    assert len(api.noivo.get(f"{BASE}/changes", params={"limit": 2}).json()) == 2
    assert api.noivo.get(f"{BASE}/changes", params={"limit": 0}).status_code == 422
    assert api.noivo.get(f"{BASE}/changes", params={"limit": 201}).status_code == 422


def test_operation_ids_estaveis(api):
    caminhos = api.app.openapi()["paths"]
    ids = {
        operacao["operationId"]
        for caminho, metodos in caminhos.items()
        if "/wedding/baseline" in caminho
        for operacao in metodos.values()
    }
    assert ids == {
        "read_baseline",
        "update_baseline_date",
        "update_baseline_city",
        "update_baseline_format",
        "update_baseline_size",
        "update_baseline_ceiling",
        "update_baseline_ceremony",
        "list_baseline_changes",
    }


def test_o_porte_traz_a_contagem_da_lista_de_convidados_sem_copia_la(api):  # F-PLN-01, D-073
    assert api.noivo.get(BASE).json()["size"]["guest_count"] == 0
    definido = _put(api.noivo, "size", {"minimum": 80, "maximum": 120}).json()["size"]
    assert definido["value"] == {"minimum": 80, "maximum": 120}

    api.noiva.post(
        "/api/v1/guests/households",
        json={
            "household": {"name": "Família Exemplo", "side": "Comum"},
            "first_guest": {"name": "Convidado Exemplo A"},
        },
    )
    depois = api.noivo.get(BASE).json()["size"]

    assert depois["guest_count"] == 1
    # Nada que a lista faz mexe no Porte gravado: valor e versão seguem os mesmos.
    assert (depois["value"], depois["version"]) == (definido["value"], definido["version"])


def test_a_contagem_do_porte_ignora_quem_nao_ira_e_o_nucleo_excluido(api):
    lista = api.noiva.post(
        "/api/v1/guests/households",
        json={
            "household": {"name": "Família Exemplo", "side": "Comum"},
            "first_guest": {"name": "Convidado Exemplo A"},
        },
    ).json()
    familia = lista["households"][0]
    api.noiva.post(
        f"/api/v1/guests/households/{familia['id']}/guests", json={"name": "Convidado Exemplo B"}
    )
    segunda = api.noiva.get("/api/v1/guests").json()["households"][0]["guests"][1]
    api.noiva.put(
        f"/api/v1/guests/people/{segunda['id']}/status",
        json={"status": "Não irá", "reason": None, "version": segunda["version"]},
    )
    assert api.noivo.get(BASE).json()["size"]["guest_count"] == 1

    api.noiva.delete(
        f"/api/v1/guests/households/{familia['id']}", params={"version": familia["version"]}
    )

    assert api.noivo.get(BASE).json()["size"]["guest_count"] == 0


def test_o_contrato_declara_a_contagem_do_porte_como_obrigatoria(api):
    esquema = api.app.openapi()["components"]["schemas"]["SizeFieldOut"]

    assert "guest_count" in esquema["required"]
