"""As rotas de edição do cronograma (F-CRN-01 e F-CRN-03, regra 2): fixture com migration real e os
dois perfis."""

import pytest
from sqlalchemy import create_engine, text
from tests.modules.schedule.catalog import categoria_id, fase_id, marco_id
from tests.modules.schedule.test_http import (
    BASE,
    ESCOPO,
    classificar_todas,
    cronograma,
    editar,
    historico,
    marco,
    mudar_estado,
    rotulos,
)

ENTRA = "Entra (Essencial)"


@pytest.fixture
def api(api_clock):
    return api_clock


def criar(client, titulo="Marco Exemplo", numero_da_fase=1, **extra):
    corpo = {"title": titulo, "phase_id": str(fase_id(numero_da_fase)), **extra}
    return client.post(f"{BASE}/milestones", json=corpo)


def definir_dependencias(client, codigo, *predecessores, versao=None):
    atual = versao if versao is not None else marco(cronograma(client), codigo)["version"]
    ids = [str(marco_id(p)) if len(p) == 3 else p for p in predecessores]
    return client.put(
        f"{BASE}/milestones/{marco_id(codigo)}/dependencies",
        json={"depends_on": ids, "version": atual},
    )


def excluir(client, codigo, versao=None):
    atual = versao if versao is not None else marco(cronograma(client), codigo)["version"]
    return client.delete(f"{BASE}/milestones/{marco_id(codigo)}", params={"version": atual})


def restaurar(client, codigo):
    return client.post(f"{BASE}/milestones/{marco_id(codigo)}/restore")


def fase(corpo, numero):
    return next(f for f in corpo["phases"] if f["id"] == str(fase_id(numero)))


def ids_da_fase(corpo, numero):
    return [m["id"] for m in fase(corpo, numero)["milestones"]]


def por_titulo(corpo, titulo):
    return next(m for f in corpo["phases"] for m in f["milestones"] if m["title"] == titulo)


def ids(corpo, codigo, campo):
    return [x["id"] for x in marco(corpo, codigo)[campo]]


# --- sessão, CSRF e contrato ------------------------------------------------------------------

ROTAS = [
    ("post", f"{BASE}/milestones", {"title": "X", "phase_id": str(fase_id(1))}),
    ("delete", f"{BASE}/milestones/{marco_id('C01')}?version=1", None),
    ("post", f"{BASE}/milestones/{marco_id('C01')}/restore", None),
    (
        "put",
        f"{BASE}/milestones/{marco_id('C01')}/dependencies",
        {"depends_on": [], "version": 1},
    ),
    ("post", f"{BASE}/phases", {"title": "X"}),
    ("put", f"{BASE}/phases/{fase_id(1)}", {"title": "X", "version": 1}),
    ("put", f"{BASE}/phases/order", {"ids": []}),
]


@pytest.mark.parametrize(("metodo", "caminho", "corpo"), ROTAS)
def test_so_com_sessao(api, metodo, caminho, corpo):
    resposta = getattr(api.anonimo, metodo)(caminho, **({"json": corpo} if corpo else {}))
    assert resposta.status_code == 401


@pytest.mark.parametrize(("metodo", "caminho", "corpo"), ROTAS)
def test_mutacao_sem_o_header_anti_csrf_e_recusada(api, metodo, caminho, corpo):
    resposta = getattr(api.sem_csrf, metodo)(caminho, **({"json": corpo} if corpo else {}))
    assert (resposta.status_code, resposta.json()["code"]) == (403, "csrf_missing")


def test_operation_ids_estaveis(api):
    caminhos = api.app.openapi()["paths"]
    esperado = {
        ("post", f"{BASE}/milestones"): "create_milestone",
        ("delete", f"{BASE}/milestones/{{milestone_id}}"): "delete_milestone",
        ("post", f"{BASE}/milestones/{{milestone_id}}/restore"): "restore_milestone",
        ("put", f"{BASE}/milestones/{{milestone_id}}/dependencies"): "set_milestone_dependencies",
        ("post", f"{BASE}/phases"): "create_phase",
        ("put", f"{BASE}/phases/{{phase_id}}"): "rename_phase",
        ("put", f"{BASE}/phases/order"): "reorder_phases",
    }
    for (metodo, caminho), operacao in esperado.items():
        assert caminhos[caminho][metodo]["operationId"] == operacao


def test_o_contrato_de_saida_nao_tem_valor_padrao_nem_campo_opcional(api):
    esquemas = api.app.openapi()["components"]["schemas"]
    for nome in ("ScheduleOut", "PhaseOut", "RestoreOut", "LeftOutOut", "CategoryOptionOut"):
        esquema = esquemas[nome]
        assert set(esquema["required"]) == set(esquema["properties"]), nome
        assert not any("default" in p for p in esquema["properties"].values()), nome


def test_nao_ha_rota_para_excluir_fase(api):
    resposta = api.noivo.delete(f"{BASE}/phases/{fase_id(1)}")
    assert resposta.status_code == 405


# --- criar marco ------------------------------------------------------------------------------


def test_criar_marco_devolve_o_id_do_marco_e_o_cronograma_com_ele_no_fim_da_fase_certa(api):
    antes = ids_da_fase(cronograma(api.noivo), 4)
    resposta = criar(api.noivo, "Marco Com Id Exemplo", 4)
    assert resposta.status_code == 201
    corpo = resposta.json()
    assert set(corpo) == {"schedule", "milestone_id"}
    criado = corpo["milestone_id"]
    assert ids_da_fase(corpo["schedule"], 4) == [*antes, criado]
    assert por_titulo(corpo["schedule"], "Marco Com Id Exemplo")["id"] == criado
    assert all(criado not in ids_da_fase(corpo["schedule"], n) for n in (1, 2, 3, 5))
    assert criado in [m["id"] for f in cronograma(api.noivo)["phases"] for m in f["milestones"]]


def test_o_contrato_do_criar_tem_o_modelo_de_saida_proprio_com_tudo_obrigatorio(api):
    caminhos = api.app.openapi()["paths"]
    post = caminhos[f"{BASE}/milestones"]["post"]
    assert post["operationId"] == "create_milestone"
    ref = post["responses"]["201"]["content"]["application/json"]["schema"]["$ref"]
    assert ref == "#/components/schemas/CreatedMilestoneOut"
    esquema = api.app.openapi()["components"]["schemas"]["CreatedMilestoneOut"]
    assert set(esquema["required"]) == set(esquema["properties"]) == {"schedule", "milestone_id"}


def test_criar_marco_devolve_o_cronograma_com_o_marco_no_fim_da_fase(api):  # F-CRN-01
    antes = ids_da_fase(cronograma(api.noivo), 4)
    resposta = criar(api.noivo, "  Marco Novo Exemplo ", 4)
    assert resposta.status_code == 201
    corpo = resposta.json()["schedule"]
    novo = por_titulo(corpo, "Marco Novo Exemplo")
    assert ids_da_fase(corpo, 4) == [*antes, novo["id"]]
    assert (novo["responsible"], novo["target_date"], novo["note"], novo["version"]) == (
        "Ambos",
        None,
        None,
        1,
    )
    assert (novo["state"], novo["blocked_by"], novo["category"]) == ("Destravado", [], None)


def test_criar_marco_com_responsavel_categoria_e_dependencias(api):
    resposta = criar(
        api.noiva,
        "Marco Ligado Exemplo",
        2,
        responsible="Noiva",
        category_id=str(categoria_id("Espaço")),
        depends_on=[str(marco_id("C01")), str(marco_id("C02"))],
    )
    novo = por_titulo(resposta.json()["schedule"], "Marco Ligado Exemplo")
    assert novo["responsible"] == "Noiva"
    assert novo["state"] == "Bloqueado"
    assert novo["blocked_by"][0]["label"] == (
        "Aguardando classificar a categoria no Mapa de Escopo"
    )
    assert {d["id"] for d in novo["depends_on"]} == {str(marco_id("C01")), str(marco_id("C02"))}
    assert novo["id"] in ids(resposta.json()["schedule"], "C01", "unlocks")
    assert novo["category"] == {"id": str(categoria_id("Espaço")), "name": "Espaço"}


def test_marco_novo_com_categoria_que_entra_nasce_destravado(api):
    classificar_todas(api.noivo)
    resposta = criar(api.noivo, category_id=str(categoria_id("Espaço")))
    assert por_titulo(resposta.json()["schedule"], "Marco Exemplo")["state"] == "Destravado"


def test_marco_sem_titulo_e_422_com_code_estavel_e_mensagem_em_portugues(api):  # F-CRN-01
    for titulo in ("", "   "):
        resposta = criar(api.noivo, titulo)
        corpo = resposta.json()
        assert (resposta.status_code, corpo["code"]) == (422, "milestone_title_required")
        assert "título" in corpo["detail"].lower()
    ausente = api.noivo.post(f"{BASE}/milestones", json={"phase_id": str(fase_id(1))})
    assert (ausente.status_code, ausente.json()["code"]) == (422, "validation_error")
    assert len(cronograma(api.noivo)["phases"][0]["milestones"]) == 4


def test_titulo_longo_demais_e_422(api):
    resposta = criar(api.noivo, "x" * 121)
    assert (resposta.status_code, resposta.json()["code"]) == (422, "invalid_schedule_value")
    assert "120" in resposta.json()["detail"]
    assert criar(api.noivo, "x" * 120).status_code == 201


def test_criar_com_fase_ou_predecessor_inexistente_e_404(api):
    desconhecido = "00000000-0000-0000-0000-000000000abc"
    resposta = api.noivo.post(f"{BASE}/milestones", json={"title": "X", "phase_id": desconhecido})
    assert resposta.status_code == 404
    assert criar(api.noivo, depends_on=[desconhecido]).status_code == 404


def test_categoria_oculta_nao_pode_ser_ligada_a_marco_novo(api):
    cat = _categoria(api.noivo, "Buffet")
    api.noivo.put(
        f"{ESCOPO}/categories/{cat['id']}/visibility",
        json={"hidden": True, "version": cat["version"]},
    )
    resposta = criar(api.noivo, category_id=cat["id"])
    assert (resposta.status_code, resposta.json()["code"]) == (422, "category_not_available")


def _categoria(client, nome):
    mapa = client.get(ESCOPO).json()
    return next(c for g in mapa["groups"] for c in g["categories"] if c["name"] == nome)


def test_marco_criado_leva_o_autor_da_sessao_e_um_id_novo(api):
    resposta = criar(api.noiva, "Marco Autoria Exemplo")
    novo = por_titulo(resposta.json()["schedule"], "Marco Autoria Exemplo")
    engine = create_engine(api.url)
    with engine.connect() as conn:
        linha = conn.execute(
            text("SELECT created_by FROM milestones WHERE id = :id"),
            {"id": novo["id"].replace("-", "")},
        ).one()
        noiva = conn.execute(
            text("SELECT id FROM users WHERE username = 'exemplo.noiva'")
        ).scalar_one()
    engine.dispose()
    assert linha.created_by == noiva
    assert novo["id"] not in {str(marco_id(f"C{n:02d}")) for n in range(1, 30)}


# --- editar marco -----------------------------------------------------------------------------


def test_editar_troca_titulo_fase_e_categoria_e_move_para_o_fim_da_fase(api):  # F-CRN-01
    antes = cronograma(api.noivo)
    resposta = editar(
        api.noiva,
        "C06",
        title="  Fechar o Salão ",
        phase_id=str(fase_id(5)),
        category_id=str(categoria_id("Buffet")),
    )
    assert resposta.status_code == 200
    corpo = resposta.json()
    item = marco(corpo, "C06")
    assert item["title"] == "Fechar o Salão"
    assert ids_da_fase(corpo, 5)[-1] == item["id"]
    assert item["position"] == len(ids_da_fase(antes, 5))
    assert item["category"]["name"] == "Buffet"
    assert item["version"] == 2
    assert ids(corpo, "C06", "depends_on") == ids(antes, "C06", "depends_on")
    assert ids(corpo, "C06", "unlocks") == ids(antes, "C06", "unlocks")


def test_editar_com_categoria_nula_desliga_a_ligacao(api):
    resposta = editar(api.noivo, "C06", category_id=None)
    assert marco(resposta.json(), "C06")["category"] is None


def test_editar_exige_titulo_e_fase_e_aceita_so_marco_existente(api):
    atual = marco(cronograma(api.noivo), "C06")
    sem = api.noivo.put(
        f"{BASE}/milestones/{atual['id']}",
        json={"responsible": "Ambos", "category_id": None, "version": atual["version"]},
    )
    assert (sem.status_code, sem.json()["code"]) == (422, "validation_error")
    vazio = editar(api.noivo, "C06", title=" ")
    assert (vazio.status_code, vazio.json()["code"]) == (422, "milestone_title_required")
    fase_ruim = editar(api.noivo, "C06", phase_id="00000000-0000-0000-0000-000000000abc")
    assert fase_ruim.status_code == 404


def test_editar_marco_arquivado_continua_permitido(api):
    classificar_todas(api.noivo)
    cat = _categoria(api.noivo, "Fotografia")
    api.noivo.put(
        f"{ESCOPO}/categories/{cat['id']}/status",
        json={"status": "Fica de fora", "reason": "Sem foto", "version": cat["version"]},
    )
    resposta = editar(api.noivo, "C08", title="Fotos")
    assert resposta.status_code == 200
    assert marco(resposta.json(), "C08")["archived"] is True


def test_editar_com_version_velha_e_409(api):
    editar(api.noivo, "C06", title="Salão")
    resposta = editar(api.noiva, "C06", title="Outro", versao=1)
    assert (resposta.status_code, resposta.json()["code"]) == (409, "version_conflict")


# --- excluir e restaurar ------------------------------------------------------------------------


def test_excluir_marco_devolve_o_cronograma_sem_ele_e_os_dependentes_recalculados(api):  # F-CRN-01
    classificar_todas(api.noivo)
    resposta = excluir(api.noivo, "C06")
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert str(marco_id("C06")) not in {m["id"] for f in corpo["phases"] for m in f["milestones"]}
    assert str(marco_id("C06")) not in ids(corpo, "C07", "depends_on")
    assert str(marco_id("C06")) not in ids(corpo, "C05", "unlocks")
    assert marco(corpo, "C07")["state"] == "Destravado"
    assert rotulos(marco(corpo, "C20")) == ["Montar a lista preliminar de convidados"]


def test_excluir_exige_a_version_na_query_e_confere(api):
    sem = api.noivo.delete(f"{BASE}/milestones/{marco_id('C06')}")
    assert (sem.status_code, sem.json()["code"]) == (422, "validation_error")
    velha = excluir(api.noivo, "C06", versao=7)
    assert (velha.status_code, velha.json()["code"]) == (409, "version_conflict")
    assert marco(cronograma(api.noivo), "C06")["title"] == "Fechar o Espaço"


def test_excluir_marco_inexistente_ou_ja_excluido_e_404(api):
    desconhecido = "00000000-0000-0000-0000-000000000abc"
    assert (
        api.noivo.delete(f"{BASE}/milestones/{desconhecido}", params={"version": 1}).status_code
        == 404
    )
    excluir(api.noivo, "C06")
    outra_vez = api.noiva.delete(f"{BASE}/milestones/{marco_id('C06')}", params={"version": 1})
    assert outra_vez.status_code == 404


def test_excluir_carimba_o_marco_e_os_vinculos_com_o_mesmo_instante_e_guarda_o_historico(api):
    mudar_estado(api.noivo, "C01", "Concluído")
    api.clock.advance(minutes=3)
    excluir(api.noiva, "C06")
    engine = create_engine(api.url)
    with engine.connect() as conn:
        carimbo = conn.execute(
            text("SELECT deleted_at FROM milestones WHERE id = :id"), {"id": marco_id("C06").hex}
        ).scalar_one()
        vinculos = conn.execute(
            text(
                "SELECT deleted_at FROM milestone_dependencies"
                " WHERE milestone_id = :id OR depends_on_id = :id"
            ),
            {"id": marco_id("C06").hex},
        ).all()
        vivos = conn.execute(
            text("SELECT COUNT(*) FROM milestone_dependencies WHERE deleted_at IS NULL")
        ).scalar_one()
    engine.dispose()
    assert carimbo is not None
    assert len(vinculos) == 11
    assert {v.deleted_at for v in vinculos} == {carimbo}
    assert vivos == 31 - 11
    assert len(historico(api)) == 1


def test_excluir_marco_com_dois_dependentes_e_restaurar_traz_tudo_de_volta(api):  # F-CRN-01
    antes = cronograma(api.noivo)
    assert len(marco(antes, "C26")["unlocks"]) == 2
    api.clock.advance(minutes=1)
    excluir(api.noivo, "C26")
    resposta = restaurar(api.noiva, "C26")
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["left_out"] == []
    depois = corpo["schedule"]
    for campo in ("depends_on", "unlocks"):
        assert marco(depois, "C26")[campo] == marco(antes, "C26")[campo]
    assert marco(depois, "C28")["depends_on"] == marco(antes, "C28")["depends_on"]
    assert marco(depois, "C29")["depends_on"] == marco(antes, "C29")["depends_on"]
    assert marco(depois, "C26")["title"] == "Confirmar as presenças"


def test_restaurar_volta_ao_fim_da_fase_original_com_o_estado_marcado(api):
    mudar_estado(api.noivo, "C01", "Concluído")
    excluir(api.noivo, "C01")
    corpo = restaurar(api.noivo, "C01").json()["schedule"]
    assert ids_da_fase(corpo, 1)[-1] == str(marco_id("C01"))
    assert marco(corpo, "C01")["state"] == "Concluído"


def test_restaurar_diz_quais_dependencias_ficaram_de_fora_por_ciclo(api):  # D-080
    excluir(api.noivo, "C26")
    definir_dependencias(api.noivo, "C25", "C28")
    corpo = restaurar(api.noivo, "C26").json()
    assert corpo["left_out"] == [
        {
            "milestone_id": str(marco_id("C28")),
            "title": "Quitar os contratos",
            "direction": "dependency_of",
        }
    ]
    assert marco(corpo["schedule"], "C28")["depends_on"] == []


def test_restaurar_diz_quais_ficaram_de_fora_por_ponta_excluida(api):
    excluir(api.noivo, "C26")
    api.clock.advance(minutes=1)
    excluir(api.noivo, "C25")
    corpo = restaurar(api.noivo, "C26").json()
    assert [(x["title"], x["direction"]) for x in corpo["left_out"]] == [
        ("Enviar os convites", "depends_on")
    ]


def test_restaurar_marco_nao_excluido_ou_inexistente_e_404(api):
    assert restaurar(api.noivo, "C06").status_code == 404
    desconhecido = "00000000-0000-0000-0000-000000000abc"
    assert api.noivo.post(f"{BASE}/milestones/{desconhecido}/restore").status_code == 404


# --- dependências -----------------------------------------------------------------------------


def test_definir_dependencias_troca_o_conjunto_e_sobe_a_version(api):  # F-CRN-03
    resposta = definir_dependencias(api.noivo, "C07", "C01", "C02")
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert set(ids(corpo, "C07", "depends_on")) == {str(marco_id("C01")), str(marco_id("C02"))}
    assert str(marco_id("C07")) in ids(corpo, "C01", "unlocks")
    assert str(marco_id("C07")) not in ids(corpo, "C06", "unlocks")
    assert marco(corpo, "C07")["version"] == 2


def test_definir_o_mesmo_conjunto_nao_grava_nada_e_repeticao_vale_como_conjunto(api):
    antes = cronograma(api.noivo)
    assert definir_dependencias(api.noivo, "C07", "C06").json() == antes
    assert definir_dependencias(api.noivo, "C07", "C06", "C06").json() == antes


def test_auto_dependencia_e_422_e_predecessor_inexistente_ou_excluido_e_404(api):
    propria = definir_dependencias(api.noivo, "C07", "C07")
    assert (propria.status_code, propria.json()["code"]) == (422, "self_dependency")
    desconhecido = "00000000-0000-0000-0000-000000000abc"
    assert definir_dependencias(api.noivo, "C07", desconhecido).status_code == 404
    excluir(api.noivo, "C01")
    assert definir_dependencias(api.noivo, "C07", "C01").status_code == 404


def test_ciclo_e_422_com_o_caminho_nos_dados_e_no_texto(api):  # F-CRN-03, regra 2
    resposta = definir_dependencias(api.noivo, "C01", "C05")
    corpo = resposta.json()
    assert (resposta.status_code, corpo["code"]) == (422, "dependency_cycle")
    caminho = corpo["data"]["path"]
    assert [p["id"] for p in caminho] == [
        str(marco_id(c)) for c in ("C01", "C05", "C04", "C03", "C01")
    ]
    assert caminho[0]["title"] == "Classificar o Mapa de Escopo"
    assert (
        "Classificar o Mapa de Escopo → Definir a data (ou janela de datas) → "
        "Escolher o caminho macro (formato e região) → "
        "Definir o teto macro e simular orçamentos → Classificar o Mapa de Escopo"
    ) in corpo["detail"]
    assert "fecharia um ciclo" in corpo["detail"]
    assert "Removam uma dessas dependências" in corpo["detail"]
    assert marco(cronograma(api.noivo), "C01")["depends_on"] == []


def test_dependencias_com_version_velha_e_409(api):
    definir_dependencias(api.noivo, "C07", "C01")
    velha = definir_dependencias(api.noiva, "C07", "C02", versao=1)
    assert (velha.status_code, velha.json()["code"]) == (409, "version_conflict")


def test_marco_inexistente_nas_dependencias_e_404(api):
    desconhecido = "00000000-0000-0000-0000-000000000abc"
    resposta = api.noivo.put(
        f"{BASE}/milestones/{desconhecido}/dependencies", json={"depends_on": [], "version": 1}
    )
    assert resposta.status_code == 404


# --- fases ------------------------------------------------------------------------------------


def test_criar_fase_vai_para_o_fim_vazia(api):  # F-CRN-01
    resposta = api.noivo.post(f"{BASE}/phases", json={"title": "  Fase Nova Exemplo "})
    assert resposta.status_code == 201
    ultima = resposta.json()["phases"][-1]
    assert (ultima["title"], ultima["position"], ultima["milestones"], ultima["version"]) == (
        "Fase Nova Exemplo",
        5,
        [],
        1,
    )
    assert ultima["progress"] == {"done": 0, "total": 0}


def test_criar_fase_sem_titulo_ou_longa_demais_e_422(api):
    vazia = api.noivo.post(f"{BASE}/phases", json={"title": "  "})
    assert (vazia.status_code, vazia.json()["code"]) == (422, "phase_title_required")
    longa = api.noivo.post(f"{BASE}/phases", json={"title": "x" * 61})
    assert (longa.status_code, longa.json()["code"]) == (422, "invalid_schedule_value")
    assert api.noivo.post(f"{BASE}/phases", json={"title": "x" * 60}).status_code == 201


def test_renomear_a_fase_nao_perde_nenhum_marco_dela(api):  # F-CRN-01
    antes = cronograma(api.noivo)
    resposta = api.noiva.put(
        f"{BASE}/phases/{fase_id(3)}", json={"title": "Fornecedores", "version": 1}
    )
    assert resposta.status_code == 200
    depois = resposta.json()
    assert fase(depois, 3)["title"] == "Fornecedores"
    assert ids_da_fase(depois, 3) == ids_da_fase(antes, 3)
    assert fase(depois, 3)["version"] == 2


def test_renomear_fase_com_version_velha_inexistente_ou_vazio(api):
    api.noivo.put(f"{BASE}/phases/{fase_id(3)}", json={"title": "Fornecedores", "version": 1})
    velha = api.noiva.put(f"{BASE}/phases/{fase_id(3)}", json={"title": "Outro", "version": 1})
    assert (velha.status_code, velha.json()["code"]) == (409, "version_conflict")
    desconhecida = api.noivo.put(
        f"{BASE}/phases/00000000-0000-0000-0000-000000000abc", json={"title": "X", "version": 1}
    )
    assert desconhecida.status_code == 404
    vazio = api.noivo.put(f"{BASE}/phases/{fase_id(3)}", json={"title": "", "version": 2})
    assert (vazio.status_code, vazio.json()["code"]) == (422, "phase_title_required")


def test_reordenar_as_fases(api):
    ordem = [str(fase_id(n)) for n in (2, 1, 3, 4, 5)]
    resposta = api.noivo.put(f"{BASE}/phases/order", json={"ids": ordem})
    assert resposta.status_code == 200
    fases = resposta.json()["phases"]
    assert [f["id"] for f in fases] == ordem
    assert [f["position"] for f in fases] == [0, 1, 2, 3, 4]
    assert [f["version"] for f in fases] == [2, 2, 1, 1, 1]


@pytest.mark.parametrize("ordem", [[], [1, 2, 3, 4], [1, 2, 3, 4, 5, 5], [1, 2, 3, 4, 99]])
def test_reordenar_exige_exatamente_as_fases_vivas(api, ordem):
    ids_ = [str(fase_id(n)) if n < 10 else "00000000-0000-0000-0000-000000000abc" for n in ordem]
    resposta = api.noivo.put(f"{BASE}/phases/order", json={"ids": ids_})
    assert (resposta.status_code, resposta.json()["code"]) == (422, "invalid_phase_order")
    assert [f["position"] for f in cronograma(api.noivo)["phases"]] == [0, 1, 2, 3, 4]


# --- categorias que o casal pode ligar ---------------------------------------------------------


def test_o_cronograma_traz_as_opcoes_de_categoria_na_ordem_do_mapa(api):  # F-CRN-01
    mapa = api.noivo.get(ESCOPO).json()
    do_mapa = [(c["id"], c["name"]) for g in mapa["groups"] for c in g["categories"]]
    opcoes = cronograma(api.noivo)["category_options"]
    assert [(o["id"], o["name"]) for o in opcoes] == do_mapa
    assert set(opcoes[0]) == {"id", "name"}


def test_categoria_nova_do_casal_entra_nas_opcoes_e_a_oculta_sai_se_nenhum_marco_a_usa(api):
    mapa = api.noivo.get(ESCOPO).json()
    grupo = mapa["groups"][0]
    criada = api.noivo.post(
        f"{ESCOPO}/categories", json={"group_id": grupo["id"], "name": "Frente Exemplo"}
    )
    nova = next(
        c for g in criada.json()["groups"] for c in g["categories"] if c["name"] == "Frente Exemplo"
    )
    assert nova["id"] in [o["id"] for o in cronograma(api.noivo)["category_options"]]
    api.noivo.put(
        f"{ESCOPO}/categories/{nova['id']}/visibility", json={"hidden": True, "version": 1}
    )
    assert nova["id"] not in [o["id"] for o in cronograma(api.noivo)["category_options"]]


def test_categoria_oculta_ligada_a_um_marco_continua_nas_opcoes(api):
    cat = _categoria(api.noivo, "Buffet")
    api.noivo.put(
        f"{ESCOPO}/categories/{cat['id']}/visibility",
        json={"hidden": True, "version": cat["version"]},
    )
    corpo = cronograma(api.noivo)
    assert cat["id"] in [o["id"] for o in corpo["category_options"]]
    assert marco(corpo, "C07")["archived"] is True


def test_toda_escrita_devolve_as_opcoes(api):
    esperado = len(cronograma(api.noivo)["category_options"])
    assert len(criar(api.noivo).json()["schedule"]["category_options"]) == esperado
    assert len(excluir(api.noivo, "C06").json()["category_options"]) == esperado
    assert len(restaurar(api.noivo, "C06").json()["schedule"]["category_options"]) == esperado
    assert esperado == 18


def test_excluir_e_restaurar_invalidam_a_version_dos_dependentes(api):  # F-CRN-03
    antes = marco(cronograma(api.noivo), "C07")["version"]
    excluir(api.noivo, "C06")
    velha = definir_dependencias(api.noiva, "C07", "C01", versao=antes)
    assert (velha.status_code, velha.json()["code"]) == (409, "version_conflict")
    guardada = marco(cronograma(api.noiva), "C07")["version"]
    assert guardada == antes + 1
    restaurar(api.noivo, "C06")
    velha = definir_dependencias(api.noiva, "C07", "C01", versao=guardada)
    assert (velha.status_code, velha.json()["code"]) == (409, "version_conflict")
    atual = marco(cronograma(api.noiva), "C07")["version"]
    assert definir_dependencias(api.noiva, "C07", "C01", versao=atual).status_code == 200


def test_o_put_do_marco_e_substituicao_inteira_e_omitir_campo_e_422(api):
    atual = marco(cronograma(api.noivo), "C06")
    completo = {
        "title": atual["title"],
        "phase_id": str(fase_id(2)),
        "responsible": "Ambos",
        "category_id": atual["category"]["id"],
        "note": None,
        "target_date": None,
        "version": atual["version"],
    }
    editar(api.noivo, "C06", note="nota importante", target_date="2027-01-15")
    for omitido in ("title", "phase_id", "responsible", "category_id", "note", "target_date"):
        corpo = {**completo, "version": atual["version"] + 1}
        del corpo[omitido]
        resposta = api.noivo.put(f"{BASE}/milestones/{atual['id']}", json=corpo)
        assert (resposta.status_code, resposta.json()["code"]) == (
            422,
            "validation_error",
        )
        assert any(e["field"] == omitido for e in resposta.json()["errors"]), omitido
    item = marco(cronograma(api.noivo), "C06")
    assert (item["note"], item["target_date"]) == ("nota importante", "2027-01-15")


def test_todo_campo_de_entrada_do_put_do_marco_e_obrigatorio_no_contrato(api):
    esquema = api.app.openapi()["components"]["schemas"]["MilestoneUpdateIn"]
    assert set(esquema["required"]) == set(esquema["properties"])


def test_reordenar_as_fases_nao_anuncia_conflito_de_version_porque_nao_usa_version(api):
    caminhos = api.app.openapi()["paths"]
    respostas = caminhos[f"{BASE}/phases/order"]["put"]["responses"]
    assert set(respostas) >= {"200", "401", "422"}
    assert "409" not in respostas
    assert "404" not in respostas
    corpo = api.app.openapi()["components"]["schemas"]["PhaseOrderIn"]
    assert set(corpo["properties"]) == {"ids"}
    # As demais escritas continuam anunciando o 409.
    assert "409" in caminhos[f"{BASE}/phases/{{phase_id}}"]["put"]["responses"]
    assert "409" in caminhos[f"{BASE}/milestones/{{milestone_id}}/dependencies"]["put"]["responses"]
