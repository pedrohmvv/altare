"""As avulsas (F-CRN-06) e o checklist (F-CRN-07) pela API, contra o banco migrado de verdade, com
os dois perfis: sessão, CSRF, 404, 409, 422, o responsável padrão vindo da sessão, o dono excluído
que esconde os itens e a confirmação de concluir com itens em aberto."""

from datetime import date

import pytest
from sqlalchemy import create_engine, text
from tests.modules.schedule.catalog import marco_id

BASE = "/api/v1/schedule"
ESCOPO = "/api/v1/wedding/scope"


@pytest.fixture
def api(api_clock):
    return api_clock


def cronograma(client):
    resposta = client.get(BASE)
    assert resposta.status_code == 200
    return resposta.json()


def marco(corpo, codigo):
    return next(
        m for f in corpo["phases"] for m in f["milestones"] if m["id"] == str(marco_id(codigo))
    )


def avulsa(corpo, id_ou_titulo):
    return next(t for t in corpo["tasks"] if id_ou_titulo in (t["id"], t["title"]))


def criar(client, titulo="Pesquisar Alianças", **campos):
    resposta = client.post(f"{BASE}/tasks", json={"title": titulo, **campos})
    assert resposta.status_code == 201, resposta.text
    return avulsa(resposta.json(), titulo.strip())


def alterar(client, tarefa, *, versao=None, **campos):
    """O PUT é a substituição inteira: o que não vem em `campos` fica como a avulsa já está."""
    atual = avulsa(cronograma(client), tarefa["id"])
    corpo = {
        "title": atual["title"],
        "responsible": atual["responsible"],
        "note": atual["note"],
        "target_date": atual["target_date"],
        "version": versao if versao is not None else atual["version"],
    }
    return client.put(f"{BASE}/tasks/{tarefa['id']}", json={**corpo, **campos})


def estado_da_avulsa(client, tarefa, estado, *, ignorar=None, versao=None):
    atual = versao if versao is not None else avulsa(cronograma(client), tarefa["id"])["version"]
    corpo = {"state": estado, "version": atual}
    if ignorar is not None:
        corpo["ignore_open_items"] = ignorar
    return client.put(f"{BASE}/tasks/{tarefa['id']}/state", json=corpo)


def adicionar(client, tipo, dono, texto="Pedir orçamento"):
    return client.post(f"{BASE}/{tipo}/{dono}/checklist", json={"text": texto})


def itens(corpo, tipo, dono):
    if tipo == "milestones":
        return next(m for f in corpo["phases"] for m in f["milestones"] if m["id"] == str(dono))[
            "checklist"
        ]
    return avulsa(corpo, str(dono))["checklist"]


def item_de_marco(client, codigo, posicao=0):
    return marco(cronograma(client), codigo)["checklist"][posicao]


def estado_do_marco(client, codigo, estado, **flags):
    versao = marco(cronograma(client), codigo)["version"]
    return client.put(
        f"{BASE}/milestones/{marco_id(codigo)}/state",
        json={"state": estado, "version": versao, **flags},
    )


def erro(resposta, status, code):
    assert (resposta.status_code, resposta.json()["code"]) == (status, code), resposta.text


# --- contrato ---------------------------------------------------------------------------------

ESCRITAS = [
    ("post", "/tasks", {"title": "Tarefa Exemplo"}),
    (
        "put",
        "/tasks/{t}",
        {
            "title": "Tarefa Exemplo",
            "responsible": "Ambos",
            "note": None,
            "target_date": None,
            "version": 1,
        },
    ),
    ("put", "/tasks/{t}/state", {"state": "A fazer", "version": 1}),
    ("delete", "/tasks/{t}?version=1", None),
    ("post", "/tasks/{t}/restore", None),
    ("post", "/milestones/{m}/checklist", {"text": "Item Exemplo"}),
    ("post", "/tasks/{t}/checklist", {"text": "Item Exemplo"}),
    ("put", "/milestones/{m}/checklist/order", {"ids": []}),
    ("put", "/tasks/{t}/checklist/order", {"ids": []}),
    ("put", "/checklist/{i}", {"text": "Item Exemplo", "done": True, "version": 1}),
    ("delete", "/checklist/{i}?version=1", None),
]


def _alvo(caminho):
    marco_c06 = str(marco_id("C06"))
    return BASE + caminho.format(t=marco_c06, m=marco_c06, i=marco_c06)


@pytest.mark.parametrize(("metodo", "caminho", "corpo"), ESCRITAS)
def test_toda_escrita_nova_exige_sessao_e_o_header_anti_csrf(api, metodo, caminho, corpo):
    alvo = _alvo(caminho)
    sem_sessao = getattr(api.anonimo, metodo)(alvo, **({"json": corpo} if corpo else {}))
    assert sem_sessao.status_code == 401, (metodo, caminho)
    sem_csrf = getattr(api.sem_csrf, metodo)(alvo, **({"json": corpo} if corpo else {}))
    assert (sem_csrf.status_code, sem_csrf.json()["code"]) == (403, "csrf_missing")


def test_operation_ids_estaveis_das_rotas_novas(api):
    caminhos = api.app.openapi()["paths"]
    esperados = {
        ("post", f"{BASE}/tasks"): "create_task",
        ("put", f"{BASE}/tasks/{{task_id}}"): "update_task",
        ("put", f"{BASE}/tasks/{{task_id}}/state"): "change_task_state",
        ("delete", f"{BASE}/tasks/{{task_id}}"): "delete_task",
        ("post", f"{BASE}/tasks/{{task_id}}/restore"): "restore_task",
        ("post", f"{BASE}/{{owner_kind}}/{{owner_id}}/checklist"): "add_checklist_item",
        ("put", f"{BASE}/{{owner_kind}}/{{owner_id}}/checklist/order"): "reorder_checklist",
        ("put", f"{BASE}/checklist/{{item_id}}"): "update_checklist_item",
        ("delete", f"{BASE}/checklist/{{item_id}}"): "remove_checklist_item",
    }
    for (metodo, caminho), operacao in esperados.items():
        assert caminhos[caminho][metodo]["operationId"] == operacao, caminho


def test_nao_ha_rota_de_restaurar_item_de_checklist(api):
    caminhos = api.app.openapi()["paths"]
    assert not [c for c in caminhos if "checklist" in c and c.endswith("restore")]
    resposta = api.noivo.post(f"{BASE}/checklist/{marco_id('C06')}/restore")
    assert resposta.status_code in (404, 405)


def test_o_dono_do_checklist_e_marco_ou_avulsa_e_so(api):
    parametro = next(
        p
        for p in api.app.openapi()["paths"][f"{BASE}/{{owner_kind}}/{{owner_id}}/checklist"][
            "post"
        ]["parameters"]
        if p["name"] == "owner_kind"
    )
    assert parametro["schema"]["enum"] == ["milestones", "tasks"]
    resposta = api.noivo.post(f"{BASE}/phases/{marco_id('C06')}/checklist", json={"text": "x"})
    erro(resposta, 422, "validation_error")


def test_reordenar_o_checklist_nao_anuncia_409_porque_nao_usa_version(api):
    caminhos = api.app.openapi()["paths"]
    respostas = caminhos[f"{BASE}/{{owner_kind}}/{{owner_id}}/checklist/order"]["put"]["responses"]
    assert set(respostas) >= {"200", "401", "404", "422"}
    assert "409" not in respostas
    corpo = api.app.openapi()["components"]["schemas"]["ChecklistOrderIn"]
    assert set(corpo["properties"]) == {"ids"}
    # As demais escritas com version anunciam o 409.
    for caminho, metodo in (
        (f"{BASE}/tasks/{{task_id}}", "put"),
        (f"{BASE}/tasks/{{task_id}}/state", "put"),
        (f"{BASE}/tasks/{{task_id}}", "delete"),
        (f"{BASE}/checklist/{{item_id}}", "put"),
        (f"{BASE}/checklist/{{item_id}}", "delete"),
    ):
        assert "409" in caminhos[caminho][metodo]["responses"], (caminho, metodo)


def test_o_contrato_declara_todos_os_campos_de_saida_novos_como_obrigatorios(api):
    esquemas = api.app.openapi()["components"]["schemas"]
    for nome in (
        "ScheduleOut",
        "TaskOut",
        "ChecklistItemOut",
        "ChecklistProgressOut",
        "MilestoneOut",
    ):
        esquema = esquemas[nome]
        assert set(esquema["required"]) == set(esquema["properties"]), nome
    assert set(esquemas["TaskOut"]["properties"]) == {
        "id",
        "title",
        "responsible",
        "note",
        "target_date",
        "state",
        "overdue",
        "days_left",
        "checklist",
        "checklist_progress",
        "attachments",
        "version",
    }
    assert set(esquemas["ChecklistItemOut"]["properties"]) == {
        "id",
        "text",
        "done",
        "position",
        "version",
    }
    assert {"tasks"} <= set(esquemas["ScheduleOut"]["properties"])
    assert {"checklist", "checklist_progress"} <= set(esquemas["MilestoneOut"]["properties"])


def test_os_corpos_de_entrada_novos_sao_a_substituicao_inteira_e_nao_tem_autoria(api):
    esquemas = api.app.openapi()["components"]["schemas"]
    atualizar = esquemas["TaskUpdateIn"]
    assert set(atualizar["required"]) == set(atualizar["properties"])
    assert set(atualizar["properties"]) == {
        "title",
        "responsible",
        "note",
        "target_date",
        "version",
    }
    item = esquemas["ChecklistItemUpdateIn"]
    assert set(item["required"]) == set(item["properties"]) == {"text", "done", "version"}
    criar_avulsa = esquemas["TaskCreateIn"]
    assert criar_avulsa["required"] == ["title"]  # o responsável é opcional: o servidor decide
    for nome in ("TaskCreateIn", "TaskUpdateIn", "TaskStateIn", "ChecklistItemCreateIn"):
        assert not {"created_by", "author", "profile"} & set(esquemas[nome]["properties"]), nome
    for nome in ("TaskStateIn", "MilestoneStateIn"):
        permissao = esquemas[nome]["properties"]["ignore_open_items"]
        assert permissao["default"] is False
        assert "ignore_open_items" not in esquemas[nome]["required"]
        assert "Concluíd" in permissao["description"]


# --- avulsas ----------------------------------------------------------------------------------


def test_o_cronograma_recem_criado_tem_a_lista_de_avulsas_vazia(api):  # F-CRN-06
    corpo = cronograma(api.noivo)
    assert corpo["tasks"] == []
    assert marco(corpo, "C01")["checklist"] == []
    assert marco(corpo, "C01")["checklist_progress"] == {"done": 0, "total": 0}


@pytest.mark.parametrize(("quem", "perfil"), [("noiva", "Noiva"), ("noivo", "Noivo")])
def test_sem_responsavel_a_avulsa_e_do_perfil_da_sessao(api, quem, perfil):
    # F-CRN-06: criar "pesquisar alianças" como Noiva a mostra na lente Minha visão da Noiva.
    tarefa = criar(getattr(api, quem))
    assert tarefa["responsible"] == perfil
    assert (tarefa["state"], tarefa["note"], tarefa["target_date"]) == ("A fazer", None, None)
    assert (tarefa["overdue"], tarefa["days_left"], tarefa["version"]) == (False, None, 1)
    assert tarefa["checklist"] == []
    assert tarefa["checklist_progress"] == {"done": 0, "total": 0}


def test_responsavel_nulo_no_corpo_tambem_vale_o_perfil_e_ambos_explicito_passa(api):
    assert criar(api.noiva, "Nulo", responsible=None)["responsible"] == "Noiva"
    assert criar(api.noivo, "Ambos", responsible="Ambos")["responsible"] == "Ambos"
    assert criar(api.noivo, "Do outro", responsible="Noiva")["responsible"] == "Noiva"


def test_responsavel_desconhecido_e_422_de_validacao(api):
    resposta = api.noivo.post(f"{BASE}/tasks", json={"title": "Tarefa", "responsible": "Outro"})
    erro(resposta, 422, "validation_error")
    assert any(e["field"] == "responsible" for e in resposta.json()["errors"])


def test_a_avulsa_criada_leva_o_autor_da_sessao_e_nao_o_do_corpo(api):
    resposta = api.noiva.post(
        f"{BASE}/tasks",
        json={"title": "Autoria Exemplo", "created_by": "x", "profile": "Noivo", "author": "y"},
    )
    assert resposta.status_code == 201
    nova = avulsa(resposta.json(), "Autoria Exemplo")
    engine = create_engine(api.url)
    with engine.connect() as conn:
        linha = conn.execute(
            text("SELECT created_by, responsible FROM schedule_tasks WHERE id = :id"),
            {"id": nova["id"].replace("-", "")},
        ).one()
        noiva = conn.execute(
            text("SELECT id FROM users WHERE username = 'exemplo.noiva'")
        ).scalar_one()
    engine.dispose()
    assert (linha.created_by, linha.responsible) == (noiva, "Noiva")


def test_criar_com_nota_e_prazo_e_apara_o_titulo(api):
    tarefa = criar(api.noivo, "  Cotar Lua de Mel  ", note="pacotes", target_date="2027-03-01")
    assert (tarefa["title"], tarefa["note"], tarefa["target_date"]) == (
        "Cotar Lua de Mel",
        "pacotes",
        "2027-03-01",
    )


def test_criar_sem_titulo_e_422_com_texto_em_voces_e_nada_e_gravado(api):
    for titulo in ("", "   "):
        resposta = api.noivo.post(f"{BASE}/tasks", json={"title": titulo})
        erro(resposta, 422, "task_title_required")
        assert "Escrevam" in resposta.json()["detail"]
    assert cronograma(api.noivo)["tasks"] == []
    erro(api.noivo.post(f"{BASE}/tasks", json={}), 422, "validation_error")


def test_criar_com_valor_fora_do_limite_e_422(api):
    for corpo in (
        {"title": "x" * 121},
        {"title": "Tarefa", "note": "x" * 501},
        {"title": "Tarefa", "target_date": "2101-01-01"},
        {"title": "Tarefa", "target_date": "1999-12-31"},
    ):
        erro(api.noivo.post(f"{BASE}/tasks", json=corpo), 422, "invalid_schedule_value")


def test_a_avulsa_fica_fora_das_fases_e_dos_bloqueios_dos_marcos(api):  # F-CRN-06, critério
    antes = cronograma(api.noivo)["phases"]
    criar(api.noiva, "Avulsa Fora do Fluxo")
    depois = cronograma(api.noivo)
    assert depois["phases"] == antes
    marcos = [m for f in depois["phases"] for m in f["milestones"]]
    assert "Avulsa Fora do Fluxo" not in str(marcos)
    assert [t["title"] for t in depois["tasks"]] == ["Avulsa Fora do Fluxo"]


def test_as_avulsas_sao_as_mesmas_para_os_dois_perfis(api):
    criar(api.noiva, "Da Noiva")
    assert [t["title"] for t in cronograma(api.noivo)["tasks"]] == ["Da Noiva"]


def test_o_prazo_da_avulsa_usa_o_dia_de_brasilia_e_a_regra_do_marco(api):
    # O relógio marca 27/10/2026 às 12h UTC (9h em Brasília).
    vencida = criar(api.noivo, "Vencida", target_date="2026-10-25")
    hoje = criar(api.noivo, "Hoje", target_date="2026-10-27")
    futura = criar(api.noivo, "Futura", target_date="2026-11-06")
    assert (vencida["overdue"], vencida["days_left"]) == (True, -2)
    assert (hoje["overdue"], hoje["days_left"]) == (False, 0)
    assert (futura["overdue"], futura["days_left"]) == (False, 10)
    resposta = estado_da_avulsa(api.noivo, vencida, "Concluída")
    concluida = avulsa(resposta.json(), "Vencida")
    assert (concluida["overdue"], concluida["days_left"]) == (False, None)


def test_a_lista_vem_com_concluidas_e_sem_prazo_por_ultimo(api):
    sem_prazo = criar(api.noivo, "A sem prazo")
    tarde = criar(api.noivo, "B tarde", target_date="2027-05-01")
    cedo = criar(api.noivo, "C cedo", target_date="2026-12-01")
    feita = criar(api.noivo, "D feita", target_date="2026-11-01")
    estado_da_avulsa(api.noivo, feita, "Concluída")
    ordem = [t["id"] for t in cronograma(api.noivo)["tasks"]]
    assert ordem == [cedo["id"], tarde["id"], sem_prazo["id"], feita["id"]]


# --- editar -----------------------------------------------------------------------------------


def test_editar_a_avulsa_substitui_os_campos_e_sobe_a_version(api):
    tarefa = criar(api.noivo)
    resposta = alterar(
        api.noiva,
        tarefa,
        title="Cotar Alianças",
        responsible="Ambos",
        note="duas lojas",
        target_date="2027-02-01",
    )
    assert resposta.status_code == 200
    nova = avulsa(resposta.json(), tarefa["id"])
    assert (nova["title"], nova["responsible"], nova["note"], nova["target_date"]) == (
        "Cotar Alianças",
        "Ambos",
        "duas lojas",
        "2027-02-01",
    )
    assert nova["version"] == tarefa["version"] + 1


def test_o_put_da_avulsa_e_substituicao_inteira_e_omitir_campo_e_422(api):
    tarefa = criar(api.noivo)
    completo = {
        "title": "Tarefa Exemplo",
        "responsible": "Ambos",
        "note": None,
        "target_date": None,
        "version": tarefa["version"],
    }
    for omitido in completo:
        corpo = {k: v for k, v in completo.items() if k != omitido}
        resposta = api.noivo.put(f"{BASE}/tasks/{tarefa['id']}", json=corpo)
        erro(resposta, 422, "validation_error")
        assert any(e["field"] == omitido for e in resposta.json()["errors"]), omitido
    assert avulsa(cronograma(api.noivo), tarefa["id"])["title"] == "Pesquisar Alianças"


def test_editar_nulo_apaga_nota_e_prazo(api):
    tarefa = criar(api.noivo, note="nota", target_date="2027-02-01")
    nova = avulsa(alterar(api.noivo, tarefa, note=None, target_date=None).json(), tarefa["id"])
    assert (nova["note"], nova["target_date"]) == (None, None)


def test_editar_sem_mudanca_nao_sobe_a_version(api):
    tarefa = criar(api.noivo)
    nova = avulsa(alterar(api.noivo, tarefa).json(), tarefa["id"])
    assert nova["version"] == tarefa["version"]


def test_editar_com_version_velha_e_409_e_nao_grava(api):
    tarefa = criar(api.noivo)
    assert alterar(api.noivo, tarefa, note="primeira").status_code == 200
    velha = alterar(api.noiva, tarefa, versao=tarefa["version"], note="segunda")
    erro(velha, 409, "version_conflict")
    assert avulsa(cronograma(api.noivo), tarefa["id"])["note"] == "primeira"


def test_editar_com_titulo_em_branco_e_422_e_version_zero_e_validacao(api):
    tarefa = criar(api.noivo)
    erro(alterar(api.noivo, tarefa, title="  "), 422, "task_title_required")
    erro(alterar(api.noivo, tarefa, versao=0), 422, "validation_error")


def test_editar_avulsa_que_nao_existe_e_404(api):
    corpo = {
        "title": "x",
        "responsible": "Ambos",
        "note": None,
        "target_date": None,
        "version": 1,
    }
    erro(api.noivo.put(f"{BASE}/tasks/{marco_id('C06')}", json=corpo), 404, "not_found")


# --- estado -----------------------------------------------------------------------------------


def test_o_estado_da_avulsa_muda_livremente(api):  # F-CRN-06
    tarefa = criar(api.noivo)
    for estado in ("Concluída", "Em andamento", "A fazer", "Em andamento", "Concluída", "A fazer"):
        resposta = estado_da_avulsa(api.noiva, tarefa, estado)
        assert resposta.status_code == 200
        assert avulsa(resposta.json(), tarefa["id"])["state"] == estado


def test_estado_desconhecido_ou_o_do_marco_e_422_de_validacao(api):
    tarefa = criar(api.noivo)
    erro(estado_da_avulsa(api.noivo, tarefa, "Concluído"), 422, "validation_error")
    erro(estado_da_avulsa(api.noivo, tarefa, None), 422, "validation_error")
    erro(estado_da_avulsa(api.noivo, tarefa, "Bloqueada"), 422, "validation_error")


def test_repetir_o_estado_da_avulsa_nao_sobe_a_version(api):
    tarefa = criar(api.noivo)
    estado_da_avulsa(api.noivo, tarefa, "Em andamento")
    nova = avulsa(estado_da_avulsa(api.noivo, tarefa, "Em andamento").json(), tarefa["id"])
    assert nova["version"] == tarefa["version"] + 1


def test_mudar_o_estado_com_version_velha_e_409_e_o_404_vale_para_o_que_nao_existe(api):
    tarefa = criar(api.noivo)
    estado_da_avulsa(api.noivo, tarefa, "Em andamento")
    erro(
        estado_da_avulsa(api.noiva, tarefa, "Concluída", versao=tarefa["version"]),
        409,
        "version_conflict",
    )
    resposta = api.noivo.put(
        f"{BASE}/tasks/{marco_id('C06')}/state", json={"state": "Concluída", "version": 1}
    )
    erro(resposta, 404, "not_found")


# --- excluir e restaurar ----------------------------------------------------------------------


def test_excluir_e_restaurar_a_avulsa_com_os_itens(api):
    tarefa = criar(api.noivo)
    adicionar(api.noivo, "tasks", tarefa["id"], "Primeiro")
    estava = avulsa(cronograma(api.noivo), tarefa["id"])
    resposta = api.noiva.delete(
        f"{BASE}/tasks/{tarefa['id']}", params={"version": estava["version"]}
    )
    assert resposta.status_code == 200
    assert resposta.json()["tasks"] == []
    # Com o dono excluído, o item é 404 em todas as rotas dele.
    item = estava["checklist"][0]
    corpo = {"text": item["text"], "done": True, "version": item["version"]}
    erro(api.noivo.put(f"{BASE}/checklist/{item['id']}", json=corpo), 404, "not_found")
    erro(adicionar(api.noivo, "tasks", tarefa["id"]), 404, "not_found")

    volta = api.noivo.post(f"{BASE}/tasks/{tarefa['id']}/restore")
    assert volta.status_code == 200
    voltou = avulsa(volta.json(), tarefa["id"])
    # Excluir e restaurar sobem a version duas vezes; o resto volta como estava.
    assert {**voltou, "version": 0} == {**estava, "version": 0}
    assert voltou["version"] == estava["version"] + 2
    assert api.noivo.put(f"{BASE}/checklist/{item['id']}", json=corpo).status_code == 200


def test_excluir_exige_a_version_na_query_e_com_a_velha_e_409(api):
    tarefa = criar(api.noivo)
    assert api.noivo.delete(f"{BASE}/tasks/{tarefa['id']}").status_code == 422
    erro(
        api.noivo.delete(f"{BASE}/tasks/{tarefa['id']}", params={"version": 0}),
        422,
        "validation_error",
    )
    estado_da_avulsa(api.noivo, tarefa, "Em andamento")
    erro(
        api.noivo.delete(f"{BASE}/tasks/{tarefa['id']}", params={"version": tarefa["version"]}),
        409,
        "version_conflict",
    )
    assert len(cronograma(api.noivo)["tasks"]) == 1


def test_excluir_ou_restaurar_o_que_nao_existe_ou_esta_vivo_e_404(api):
    tarefa = criar(api.noivo)
    erro(api.noivo.post(f"{BASE}/tasks/{tarefa['id']}/restore"), 404, "not_found")
    erro(api.noivo.post(f"{BASE}/tasks/{marco_id('C06')}/restore"), 404, "not_found")
    api.noivo.delete(f"{BASE}/tasks/{tarefa['id']}", params={"version": tarefa["version"]})
    erro(
        api.noivo.delete(f"{BASE}/tasks/{tarefa['id']}", params={"version": tarefa["version"] + 1}),
        404,
        "not_found",
    )


# --- checklist: adicionar, marcar, editar, remover ---------------------------------------------


def test_adicionar_item_ao_marco_e_a_avulsa_devolve_o_cronograma_inteiro(api):  # F-CRN-07
    tarefa = criar(api.noivo)
    no_marco = adicionar(api.noivo, "milestones", marco_id("C06"), "  Pedir orçamento  ")
    assert no_marco.status_code == 201
    na_avulsa = adicionar(api.noiva, "tasks", tarefa["id"], "Ligar para a joalheria")
    assert na_avulsa.status_code == 201
    corpo = na_avulsa.json()
    assert [
        (i["text"], i["done"], i["position"], i["version"])
        for i in marco(corpo, "C06")["checklist"]
    ] == [("Pedir orçamento", False, 0, 1)]
    assert [i["text"] for i in avulsa(corpo, tarefa["id"])["checklist"]] == [
        "Ligar para a joalheria"
    ]
    assert marco(corpo, "C07")["checklist"] == []


def test_o_item_nao_toca_o_dono_nem_ao_adicionar_nem_ao_marcar_nem_ao_remover(api):  # regra 4
    tarefa = criar(api.noivo)
    antes_marco, antes_tarefa = marco(cronograma(api.noivo), "C06"), tarefa
    for tipo, dono in (("milestones", marco_id("C06")), ("tasks", tarefa["id"])):
        adicionar(api.noivo, tipo, dono, "A")
        adicionar(api.noivo, tipo, dono, "B")
        a = itens(cronograma(api.noivo), tipo, dono)[0]
        marcado = api.noiva.put(
            f"{BASE}/checklist/{a['id']}", json={"text": "A", "done": True, "version": a["version"]}
        )
        assert marcado.status_code == 200
        editado = api.noiva.put(
            f"{BASE}/checklist/{a['id']}",
            json={"text": "A editado", "done": True, "version": a["version"] + 1},
        )
        assert editado.status_code == 200
        b = itens(cronograma(api.noivo), tipo, dono)[1]
        removido = api.noivo.delete(f"{BASE}/checklist/{b['id']}", params={"version": b["version"]})
        assert removido.status_code == 200
    depois = cronograma(api.noivo)
    assert marco(depois, "C06")["version"] == antes_marco["version"]
    assert marco(depois, "C06")["state"] == antes_marco["state"]
    assert avulsa(depois, tarefa["id"])["version"] == antes_tarefa["version"]
    assert avulsa(depois, tarefa["id"])["state"] == antes_tarefa["state"]


def test_marcar_dois_de_cinco_mostra_o_progresso(api):  # F-CRN-07, critério
    for numero in range(5):
        adicionar(api.noivo, "milestones", marco_id("C06"), f"Item {numero}")
    for item in cronograma(api.noivo) and marco(cronograma(api.noivo), "C06")["checklist"][:2]:
        resposta = api.noivo.put(
            f"{BASE}/checklist/{item['id']}",
            json={"text": item["text"], "done": True, "version": item["version"]},
        )
        assert resposta.status_code == 200
    assert marco(cronograma(api.noivo), "C06")["checklist_progress"] == {"done": 2, "total": 5}


def test_editar_item_sem_mudanca_nao_sobe_a_version_e_com_version_velha_e_409(api):
    adicionar(api.noivo, "milestones", marco_id("C06"))
    item = item_de_marco(api.noivo, "C06")
    corpo = {"text": item["text"], "done": item["done"], "version": item["version"]}
    sem_mudanca = api.noivo.put(f"{BASE}/checklist/{item['id']}", json=corpo)
    assert sem_mudanca.status_code == 200
    assert marco(sem_mudanca.json(), "C06")["checklist"][0]["version"] == item["version"]
    api.noivo.put(f"{BASE}/checklist/{item['id']}", json={**corpo, "done": True})
    erro(
        api.noiva.put(f"{BASE}/checklist/{item['id']}", json={**corpo, "text": "Outro"}),
        409,
        "version_conflict",
    )
    assert item_de_marco(api.noivo, "C06")["text"] == "Pedir orçamento"


def test_editar_item_com_texto_em_branco_ou_longo_demais_e_422(api):
    adicionar(api.noivo, "milestones", marco_id("C06"))
    item = item_de_marco(api.noivo, "C06")
    base = {"done": False, "version": item["version"]}
    resposta = api.noivo.put(f"{BASE}/checklist/{item['id']}", json={**base, "text": "  "})
    erro(resposta, 422, "checklist_text_required")
    assert "Escrevam" in resposta.json()["detail"]
    erro(
        api.noivo.put(f"{BASE}/checklist/{item['id']}", json={**base, "text": "x" * 201}),
        422,
        "invalid_schedule_value",
    )
    erro(
        api.noivo.put(f"{BASE}/checklist/{item['id']}", json={"text": "x"}), 422, "validation_error"
    )


def test_adicionar_item_sem_texto_e_422_e_dono_que_nao_existe_e_404(api):
    erro(adicionar(api.noivo, "milestones", marco_id("C06"), "  "), 422, "checklist_text_required")
    erro(
        adicionar(api.noivo, "milestones", marco_id("C06"), "x" * 201),
        422,
        "invalid_schedule_value",
    )
    erro(
        adicionar(api.noivo, "tasks", marco_id("C06")), 404, "not_found"
    )  # id de marco, tipo avulsa
    erro(
        adicionar(api.noivo, "milestones", "00000000-0000-0000-0000-000000000abc"), 404, "not_found"
    )
    erro(
        api.noivo.post(f"{BASE}/milestones/nao-e-uuid/checklist", json={"text": "x"}),
        422,
        "validation_error",
    )


def test_o_item_que_nao_existe_e_404_no_put_e_no_delete(api):
    fantasma = "00000000-0000-0000-0000-000000000abc"
    erro(
        api.noivo.put(
            f"{BASE}/checklist/{fantasma}", json={"text": "x", "done": True, "version": 1}
        ),
        404,
        "not_found",
    )
    erro(api.noivo.delete(f"{BASE}/checklist/{fantasma}", params={"version": 1}), 404, "not_found")


def test_o_cinquenta_e_um_item_vivo_e_422_e_remover_abre_vaga(api):
    for numero in range(50):
        assert (
            adicionar(api.noivo, "milestones", marco_id("C06"), f"Item {numero}").status_code == 201
        )
    erro(adicionar(api.noivo, "milestones", marco_id("C06"), "Demais"), 422, "checklist_full")
    primeiro = item_de_marco(api.noivo, "C06")
    api.noivo.delete(f"{BASE}/checklist/{primeiro['id']}", params={"version": primeiro["version"]})
    assert adicionar(api.noivo, "milestones", marco_id("C06"), "Cabe agora").status_code == 201
    assert len(marco(cronograma(api.noivo), "C06")["checklist"]) == 50


def test_remover_o_item_e_logico_nao_ha_restaurar_e_a_version_velha_e_409(api):
    adicionar(api.noivo, "milestones", marco_id("C06"), "A")
    adicionar(api.noivo, "milestones", marco_id("C06"), "B")
    a = item_de_marco(api.noivo, "C06")
    erro(
        api.noivo.delete(f"{BASE}/checklist/{a['id']}", params={"version": 9}),
        409,
        "version_conflict",
    )
    assert api.noivo.delete(f"{BASE}/checklist/{a['id']}").status_code == 422
    resposta = api.noiva.delete(f"{BASE}/checklist/{a['id']}", params={"version": a["version"]})
    assert resposta.status_code == 200
    assert [i["text"] for i in marco(resposta.json(), "C06")["checklist"]] == ["B"]
    erro(
        api.noivo.delete(f"{BASE}/checklist/{a['id']}", params={"version": a["version"]}),
        404,
        "not_found",
    )
    engine = create_engine(api.url)
    with engine.connect() as conn:
        gravado = conn.execute(
            text("SELECT deleted_at, deleted_by FROM checklist_items WHERE id = :id"),
            {"id": a["id"].replace("-", "")},
        ).one()
        noiva = conn.execute(
            text("SELECT id FROM users WHERE username = 'exemplo.noiva'")
        ).scalar_one()
    engine.dispose()
    assert gravado.deleted_at is not None
    assert gravado.deleted_by == noiva


# --- checklist: reordenar ---------------------------------------------------------------------


def _ordem(client, tipo, dono, ids):
    return client.put(f"{BASE}/{tipo}/{dono}/checklist/order", json={"ids": ids})


@pytest.mark.parametrize("tipo", ["milestones", "tasks"])
def test_reordenar_aplica_a_permutacao_e_deixa_as_posicoes_densas(api, tipo):
    dono = marco_id("C06") if tipo == "milestones" else criar(api.noivo)["id"]
    for texto in ("A", "B", "C"):
        adicionar(api.noivo, tipo, dono, texto)
    a, b, c = itens(cronograma(api.noivo), tipo, dono)
    # Um removido no meio deixa buraco; reordenar reatribui 0..n-1 só entre os vivos.
    api.noivo.delete(f"{BASE}/checklist/{b['id']}", params={"version": b["version"]})
    resposta = _ordem(api.noiva, tipo, dono, [c["id"], a["id"]])
    assert resposta.status_code == 200
    depois = itens(resposta.json(), tipo, dono)
    assert [(i["text"], i["position"]) for i in depois] == [("C", 0), ("A", 1)]


def test_reordenar_so_sobe_a_version_de_quem_mudou_e_nunca_a_do_dono(api):
    for texto in ("A", "B", "C"):
        adicionar(api.noivo, "milestones", marco_id("C06"), texto)
    dono = marco(cronograma(api.noivo), "C06")
    a, b, c = dono["checklist"]
    resposta = _ordem(api.noivo, "milestones", marco_id("C06"), [a["id"], c["id"], b["id"]])
    depois = marco(resposta.json(), "C06")
    versoes = {i["text"]: i["version"] for i in depois["checklist"]}
    assert versoes == {"A": a["version"], "B": b["version"] + 1, "C": c["version"] + 1}
    assert depois["version"] == dono["version"]


def test_reordenar_o_que_nao_e_permutacao_exata_dos_vivos_e_422_e_nada_muda(api):
    for texto in ("A", "B"):
        adicionar(api.noivo, "milestones", marco_id("C06"), texto)
    adicionar(api.noivo, "milestones", marco_id("C07"), "De outro marco")
    a, b = marco(cronograma(api.noivo), "C06")["checklist"]
    de_outro = marco(cronograma(api.noivo), "C07")["checklist"][0]
    fantasma = "00000000-0000-0000-0000-000000000abc"
    for ids in (
        [a["id"]],
        [a["id"], b["id"], b["id"]],
        [a["id"], b["id"], de_outro["id"]],
        [a["id"], de_outro["id"]],
        [a["id"], b["id"], fantasma],
        [],
    ):
        resposta = _ordem(api.noivo, "milestones", marco_id("C06"), ids)
        erro(resposta, 422, "invalid_checklist_order")
        assert "Recarreguem" in resposta.json()["detail"]
    assert [i["text"] for i in marco(cronograma(api.noivo), "C06")["checklist"]] == ["A", "B"]
    erro(_ordem(api.noivo, "milestones", marco_id("C06"), ["nao-e-uuid"]), 422, "validation_error")


def test_reordenar_dono_que_nao_existe_e_404(api):
    erro(_ordem(api.noivo, "tasks", marco_id("C06"), []), 404, "not_found")
    erro(
        _ordem(api.noivo, "milestones", "00000000-0000-0000-0000-000000000abc", []),
        404,
        "not_found",
    )


def test_a_rota_de_ordem_nao_e_engolida_pela_do_item(api):
    # `/checklist/order` casaria com `/checklist/{item_id}`; a de ordem vem de outro formato de
    # caminho e a do item exige UUID. Cada uma responde pelo que é.
    adicionar(api.noivo, "milestones", marco_id("C06"), "A")
    a = item_de_marco(api.noivo, "C06")
    assert _ordem(api.noivo, "milestones", marco_id("C06"), [a["id"]]).status_code == 200
    erro(
        api.noivo.put(f"{BASE}/checklist/order", json={"text": "x", "done": True, "version": 1}),
        422,
        "validation_error",
    )


# --- o dono excluído e restaurado --------------------------------------------------------------


def test_excluir_o_marco_esconde_os_itens_e_restaurar_traz_de_volta(api):
    adicionar(api.noivo, "milestones", marco_id("C06"), "A")
    adicionar(api.noivo, "milestones", marco_id("C06"), "B")
    item = item_de_marco(api.noivo, "C06")
    api.noivo.put(
        f"{BASE}/checklist/{item['id']}",
        json={"text": "A", "done": True, "version": item["version"]},
    )
    estava = marco(cronograma(api.noivo), "C06")["checklist"]
    dono = marco(cronograma(api.noivo), "C06")
    api.noiva.delete(f"{BASE}/milestones/{dono['id']}", params={"version": dono["version"]})
    # Os itens somem junto: nenhum marco ativo os carrega.
    assert str(estava[0]["id"]) not in str(cronograma(api.noivo))
    corpo = {"text": "A", "done": False, "version": estava[0]["version"]}
    erro(api.noivo.put(f"{BASE}/checklist/{estava[0]['id']}", json=corpo), 404, "not_found")
    erro(
        api.noivo.delete(f"{BASE}/checklist/{estava[0]['id']}", params={"version": 1}),
        404,
        "not_found",
    )
    erro(adicionar(api.noivo, "milestones", dono["id"]), 404, "not_found")
    erro(_ordem(api.noivo, "milestones", dono["id"], [i["id"] for i in estava]), 404, "not_found")

    volta = api.noivo.post(f"{BASE}/milestones/{dono['id']}/restore")
    assert volta.status_code == 200
    assert marco(volta.json()["schedule"], "C06")["checklist"] == estava


# --- concluir com itens em aberto (F-CRN-07, regra 5) -----------------------------------------


def test_concluir_o_marco_com_item_em_aberto_e_422_e_com_a_permissao_conclui_e_preserva(api):
    adicionar(api.noivo, "milestones", marco_id("C01"), "A")
    adicionar(api.noivo, "milestones", marco_id("C01"), "B")
    antes = marco(cronograma(api.noivo), "C01")["checklist"]
    resposta = estado_do_marco(api.noivo, "C01", "Concluído")
    erro(resposta, 422, "checklist_open_items")
    assert "{" not in resposta.json()["detail"]
    assert marco(cronograma(api.noivo), "C01")["state"] != "Concluído"

    aceito = estado_do_marco(api.noiva, "C01", "Concluído", ignore_open_items=True)
    assert aceito.status_code == 200
    depois = marco(aceito.json(), "C01")
    assert depois["state"] == "Concluído"
    assert depois["checklist"] == antes
    assert depois["checklist_progress"] == {"done": 0, "total": 2}


def test_a_permissao_dos_itens_so_vale_ao_concluir(api):
    adicionar(api.noivo, "milestones", marco_id("C01"), "A")
    assert estado_do_marco(api.noivo, "C01", "Em andamento").status_code == 200
    assert (
        estado_do_marco(api.noivo, "C01", "Em andamento", ignore_open_items=True).status_code == 200
    )
    assert estado_do_marco(api.noivo, "C01", None, ignore_open_items=True).status_code == 200
    # Sem item em aberto, a permissão é inofensiva.
    assert estado_do_marco(api.noivo, "C02", "Concluído", ignore_open_items=True).status_code == 200


def test_o_bloqueio_do_marco_vem_antes_dos_itens_em_aberto(api):
    adicionar(api.noivo, "milestones", marco_id("C03"), "A")
    # C03 aguarda C01 e C02. A permissão dos itens não substitui a do bloqueio.
    erro(
        estado_do_marco(api.noivo, "C03", "Concluído", ignore_open_items=True),
        422,
        "milestone_blocked",
    )
    erro(estado_do_marco(api.noivo, "C03", "Concluído"), 422, "milestone_blocked")
    erro(
        estado_do_marco(api.noivo, "C03", "Concluído", ignore_block=True),
        422,
        "checklist_open_items",
    )
    aceito = estado_do_marco(
        api.noivo, "C03", "Concluído", ignore_block=True, ignore_open_items=True
    )
    assert aceito.status_code == 200
    assert marco(aceito.json(), "C03")["state"] == "Concluído"


def test_repetir_concluido_com_item_aberto_depois_nao_pede_nada_e_a_version_vem_antes(api):
    estado_do_marco(api.noivo, "C01", "Concluído")
    adicionar(api.noivo, "milestones", marco_id("C01"), "Aberto depois")
    assert estado_do_marco(api.noivo, "C01", "Concluído").status_code == 200
    resposta = api.noivo.put(
        f"{BASE}/milestones/{marco_id('C01')}/state", json={"state": "Concluído", "version": 99}
    )
    erro(resposta, 409, "version_conflict")


def test_concluir_a_avulsa_com_item_em_aberto_e_422_e_com_a_permissao_conclui(api):
    tarefa = criar(api.noivo)
    adicionar(api.noivo, "tasks", tarefa["id"], "A")
    erro(estado_da_avulsa(api.noivo, tarefa, "Concluída"), 422, "checklist_open_items")
    erro(
        estado_da_avulsa(api.noivo, tarefa, "Concluída", ignorar=False), 422, "checklist_open_items"
    )
    resposta = estado_da_avulsa(api.noiva, tarefa, "Concluída", ignorar=True)
    assert resposta.status_code == 200
    concluida = avulsa(resposta.json(), tarefa["id"])
    assert concluida["state"] == "Concluída"
    assert concluida["checklist_progress"] == {"done": 0, "total": 1}
    # Reabrir e ir a Em andamento nunca pedem nada.
    assert estado_da_avulsa(api.noivo, tarefa, "A fazer").status_code == 200
    assert estado_da_avulsa(api.noivo, tarefa, "Em andamento").status_code == 200


def test_o_historico_de_estado_dos_marcos_nao_ganha_nada_pelos_itens(api):
    adicionar(api.noivo, "milestones", marco_id("C01"), "A")
    estado_do_marco(api.noivo, "C01", "Concluído")  # 422, não grava
    estado_do_marco(api.noivo, "C01", "Concluído", ignore_open_items=True)
    engine = create_engine(api.url)
    with engine.connect() as conn:
        linhas = conn.execute(
            text("SELECT state_before, state_after, ignored_block FROM milestone_changes")
        ).all()
    engine.dispose()
    assert [(a, b, bool(c)) for a, b, c in linhas] == [(None, "Concluído", False)]


def test_a_data_de_hoje_nao_vem_do_corpo_nem_do_relogio_do_cliente(api):
    # Hoje é o dia de Brasília pelo Clock do servidor: o prazo vencido no dia seguinte vira atraso.
    tarefa = criar(api.noivo, target_date=date(2026, 10, 27).isoformat())
    assert tarefa["overdue"] is False
    api.clock.advance(days=1)
    assert avulsa(cronograma(api.noivo), tarefa["id"])["overdue"] is True
