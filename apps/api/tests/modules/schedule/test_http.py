from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import create_engine, text
from tests.modules.schedule.catalog import MARCOS, categoria_id, fase_id, marco_id

BASE = "/api/v1/schedule"
ESCOPO = "/api/v1/wedding/scope"
AGUARDA_CATEGORIA = "Aguardando classificar a categoria no Mapa de Escopo"
ENTRA = "Entra (Essencial)"


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


def rotulos(item):
    return [b["label"] for b in item["blocked_by"]]


def classificar(client, nome, status, motivo=None):
    mapa = client.get(ESCOPO).json()
    cat = next(c for g in mapa["groups"] for c in g["categories"] if c["name"] == nome)
    resposta = client.put(
        f"{ESCOPO}/categories/{cat['id']}/status",
        json={"status": status, "reason": motivo, "version": cat["version"]},
    )
    assert resposta.status_code == 200, resposta.text


def classificar_todas(client, status=ENTRA):
    nomes = [c["name"] for g in client.get(ESCOPO).json()["groups"] for c in g["categories"]]
    for nome in nomes:
        classificar(client, nome, status)


def mudar_estado(client, codigo, estado, *, ignorar=None, versao=None):
    atual = versao if versao is not None else marco(cronograma(client), codigo)["version"]
    corpo = {"state": estado, "version": atual}
    if ignorar is not None:
        corpo["ignore_block"] = ignorar
    return client.put(f"{BASE}/milestones/{marco_id(codigo)}/state", json=corpo)


def concluir(client, *codigos, ignorar=None):
    for codigo in codigos:
        resposta = mudar_estado(client, codigo, "Concluído", ignorar=ignorar)
        assert resposta.status_code == 200, (codigo, resposta.text)


def editar(client, codigo, *, versao=None, **campos):
    """O PUT é a substituição inteira: o que não vem em `campos` fica como o marco já está."""
    corpo = cronograma(client)
    atual = marco(corpo, codigo)
    fase = next(f for f in corpo["phases"] if atual in f["milestones"])
    padrao = {
        "title": atual["title"],
        "phase_id": fase["id"],
        "responsible": atual["responsible"],
        "category_id": atual["category"]["id"] if atual["category"] else None,
        "note": atual["note"],
        "target_date": atual["target_date"],
        "version": versao if versao is not None else atual["version"],
    }
    return client.put(f"{BASE}/milestones/{marco_id(codigo)}", json={**padrao, **campos})


def historico(api):
    engine = create_engine(api.url)
    with engine.connect() as conn:
        linhas = conn.execute(
            text(
                "SELECT milestone_id, state_before, state_after, ignored_block, profile,"
                " created_by FROM milestone_changes ORDER BY created_at, id"
            )
        ).all()
    engine.dispose()
    return linhas


def test_so_com_sessao(api):
    alvo = f"{BASE}/milestones/{marco_id('C01')}"
    assert api.anonimo.get(BASE).status_code == 401
    corpo = {
        "title": "Marco Exemplo",
        "phase_id": str(fase_id(1)),
        "responsible": "Ambos",
        "category_id": None,
        "note": None,
        "target_date": None,
        "version": 1,
    }
    assert api.anonimo.put(alvo, json=corpo).status_code == 401
    assert api.anonimo.put(f"{alvo}/state", json={"state": None, "version": 1}).status_code == 401


def test_mutacao_sem_o_header_anti_csrf_e_recusada(api):
    alvo = f"{BASE}/milestones/{marco_id('C01')}/state"
    resposta = api.sem_csrf.put(alvo, json={"state": None, "version": 1})
    assert (resposta.status_code, resposta.json()["code"]) == (403, "csrf_missing")


def test_operation_ids_estaveis(api):
    caminhos = api.app.openapi()["paths"]
    assert caminhos[BASE]["get"]["operationId"] == "read_schedule"
    assert (
        caminhos[f"{BASE}/milestones/{{milestone_id}}"]["put"]["operationId"] == "update_milestone"
    )
    estado = caminhos[f"{BASE}/milestones/{{milestone_id}}/state"]["put"]
    assert estado["operationId"] == "change_milestone_state"


def test_o_contrato_declara_todos_os_campos_de_saida_como_obrigatorios(api):
    esquemas = api.app.openapi()["components"]["schemas"]
    saidas = (
        "ScheduleOut",
        "PhaseOut",
        "PhaseProgressOut",
        "MilestoneOut",
        "BlockerOut",
        "DependencyOut",
        "MilestoneRefOut",
        "WarningOut",
        "CategoryLinkOut",
        "CategoryOptionOut",
        "RestoreOut",
        "LeftOutOut",
        "MilestoneWindowOut",
        "TaskOut",
        "ChecklistItemOut",
        "ChecklistProgressOut",
    )
    for nome in saidas:
        esquema = esquemas[nome]
        assert set(esquema["required"]) == set(esquema["properties"]), nome


def test_recem_criado_tem_29_marcos_em_5_fases_todos_ambos_e_sem_prazo(api):  # F-CRN-02
    corpo = cronograma(api.noivo)
    assert [f["title"] for f in corpo["phases"]] == [
        "Marco Zero",
        "Contrato Âncora",
        "Fornecedores Essenciais",
        "Identidade, Complementares e Convidados",
        "Reta Final",
    ]
    marcos = [m for f in corpo["phases"] for m in f["milestones"]]
    assert len(marcos) == 29
    assert {m["responsible"] for m in marcos} == {"Ambos"}
    assert {m["target_date"] for m in marcos} == {None}
    assert {m["note"] for m in marcos} == {None}
    assert {m["version"] for m in marcos} == {1}
    assert corpo["has_exact_date"] is False
    assert [m["title"] for m in marcos][:2] == [
        "Classificar o Mapa de Escopo",
        "Montar a lista preliminar de convidados",
    ]


def test_o_marco_liga_a_categoria_do_mapa_pelo_id_e_mostra_o_nome_atual(api):  # F-CRN-02, regra 1
    corpo = cronograma(api.noivo)
    assert marco(corpo, "C01")["category"] is None
    assert marco(corpo, "C06")["category"] == {"id": str(categoria_id("Espaço")), "name": "Espaço"}
    assert marco(corpo, "C11")["category"] == {
        "id": str(categoria_id("Música (DJ, banda)")),
        "name": "Música (DJ, banda)",
    }
    mapa = api.noivo.get(ESCOPO).json()
    ids_do_mapa = {c["id"] for g in mapa["groups"] for c in g["categories"]}
    ligados = {
        m["category"]["id"] for f in corpo["phases"] for m in f["milestones"] if m["category"]
    }
    assert ligados <= ids_do_mapa
    assert len(ligados) == sum(1 for c in MARCOS if c[3])


def test_renomear_a_categoria_nao_quebra_a_ligacao(api):  # F-CRN-02, regra 1
    mapa = api.noivo.get(ESCOPO).json()
    cat = next(c for g in mapa["groups"] for c in g["categories"] if c["name"] == "Espaço")
    grupo = next(g for g in mapa["groups"] if cat in g["categories"])
    renomeada = api.noivo.put(
        f"{ESCOPO}/categories/{cat['id']}",
        json={
            "name": "Local da festa",
            "group_id": grupo["id"],
            "estimate_cents": None,
            "version": 1,
        },
    )
    assert renomeada.status_code == 200
    assert marco(cronograma(api.noiva), "C06")["category"] == {
        "id": cat["id"],
        "name": "Local da festa",
    }


def test_com_todas_as_categorias_em_discussao_os_ligados_aguardam_a_classificacao(api):  # F-CRN-02
    corpo = cronograma(api.noivo)
    for codigo, _f, _t, categoria, _d, _j in MARCOS:
        item = marco(corpo, codigo)
        if categoria:
            assert item["state"] == "Bloqueado", codigo
            assert item["blocked_by"][0] == {
                "kind": "category",
                "milestone_id": None,
                "label": AGUARDA_CATEGORIA,
            }, codigo


def test_depois_de_classificar_o_c06_c12_c13_aguardam_a_data_e_c07_a_c11_o_espaco(api):  # F-CRN-02
    classificar_todas(api.noivo)
    corpo = cronograma(api.noiva)
    for codigo in ("C06", "C12", "C13"):
        assert rotulos(marco(corpo, codigo)) == ["Definir a data (ou janela de datas)"], codigo
    for codigo in ("C07", "C08", "C09", "C10", "C11"):
        assert rotulos(marco(corpo, codigo)) == ["Fechar o Espaço"], codigo
        assert marco(corpo, codigo)["blocked_by"][0]["milestone_id"] == str(marco_id("C06"))


def test_concluir_o_c06_destrava_os_dependentes_e_o_c20_espera_o_c02(api):  # F-CRN-03
    classificar_todas(api.noivo)
    concluir(api.noivo, "C01", "C03", "C04", "C05", ignorar=True)
    concluir(api.noivo, "C06")
    corpo = cronograma(api.noivo)
    for codigo in ("C07", "C08", "C09", "C10", "C11", "C14", "C15", "C21", "C24"):
        assert marco(corpo, codigo)["state"] == "Destravado", codigo
    assert marco(corpo, "C20")["state"] == "Bloqueado"
    assert rotulos(marco(corpo, "C20")) == ["Montar a lista preliminar de convidados"]
    concluir(api.noiva, "C02")
    assert marco(cronograma(api.noivo), "C20")["state"] == "Destravado"


def test_fotografia_fica_de_fora_arquiva_o_c08_e_reabrir_restaura_o_estado(api):  # F-CRN-04
    classificar_todas(api.noivo)
    assert mudar_estado(api.noivo, "C08", "Em andamento", ignorar=True).status_code == 200
    classificar(api.noivo, "Fotografia", "Fica de fora", "Não faremos")
    arquivado = marco(cronograma(api.noivo), "C08")
    assert (arquivado["archived"], arquivado["state"]) == (True, "Em andamento")
    classificar(api.noiva, "Fotografia", ENTRA)
    restaurado = marco(cronograma(api.noivo), "C08")
    assert (restaurado["archived"], restaurado["state"]) == (False, "Em andamento")


def test_buffet_fica_de_fora_e_quem_dependia_dele_nao_espera_por_ele(api):  # F-CRN-04
    classificar_todas(api.noivo)
    concluir(api.noivo, "C01", "C02", "C03", "C04", "C05", "C06")
    assert rotulos(marco(cronograma(api.noivo), "C16")) == ["Fechar o Buffet"]
    classificar(api.noivo, "Buffet", "Fica de fora", "Sem buffet")
    corpo = cronograma(api.noivo)
    assert marco(corpo, "C07")["archived"] is True
    assert marco(corpo, "C16")["state"] == "Destravado"
    assert marco(corpo, "C16")["depends_on"][0]["resolved"] is True


def test_categoria_oculta_tambem_arquiva_o_marco(api):  # F-CRN-04, regra 3
    classificar_todas(api.noivo)
    mapa = api.noivo.get(ESCOPO).json()
    cat = next(c for g in mapa["groups"] for c in g["categories"] if c["name"] == "Vídeo")
    ocultar = api.noivo.put(
        f"{ESCOPO}/categories/{cat['id']}/visibility",
        json={"hidden": True, "version": cat["version"]},
    )
    assert ocultar.status_code == 200
    assert marco(cronograma(api.noivo), "C09")["archived"] is True


def test_grupo_oculto_arquiva_os_marcos_das_categorias_dele(api):  # F-CRN-04, regra 3
    classificar_todas(api.noivo)
    mapa = api.noivo.get(ESCOPO).json()
    grupo = next(g for g in mapa["groups"] if g["name"] == "Registro")
    ocultar = api.noivo.put(
        f"{ESCOPO}/groups/{grupo['id']}/visibility",
        json={"hidden": True, "version": grupo["version"]},
    )
    assert ocultar.status_code == 200
    corpo = cronograma(api.noivo)
    assert marco(corpo, "C08")["archived"] is True
    assert marco(corpo, "C09")["archived"] is True
    assert marco(corpo, "C07")["archived"] is False


def test_musica_talvez_mostra_o_c11_opcional_e_o_c29_nao_muda(api):  # F-CRN-04
    classificar_todas(api.noivo)
    antes = marco(cronograma(api.noivo), "C29")
    classificar(api.noivo, "Música (DJ, banda)", "Talvez (Se couber)")
    corpo = cronograma(api.noivo)
    assert (marco(corpo, "C11")["optional"], marco(corpo, "C11")["archived"]) == (True, False)
    assert marco(corpo, "C29")["blocked_by"] == antes["blocked_by"]
    assert marco(corpo, "C29")["state"] == antes["state"]


def test_marcar_concluido_um_bloqueado_sem_ignorar_e_422_com_codigo_proprio(api):  # F-CRN-03
    antes = cronograma(api.noivo)
    resposta = mudar_estado(api.noivo, "C03", "Concluído")
    assert resposta.status_code == 422
    corpo = resposta.json()
    assert corpo["code"] == "milestone_blocked"
    assert "bloqueio" in corpo["detail"].lower()
    assert cronograma(api.noivo) == antes
    assert historico(api) == []


def test_ignorar_o_bloqueio_passa_e_o_historico_registra_o_perfil_da_sessao(api):  # F-CRN-03
    resposta = mudar_estado(api.noiva, "C03", "Concluído", ignorar=True)
    assert resposta.status_code == 200
    assert marco(resposta.json(), "C03")["state"] == "Concluído"
    [linha] = historico(api)
    assert linha.milestone_id == marco_id("C03").hex
    assert (linha.state_before, linha.state_after) == (None, "Concluído")
    assert (bool(linha.ignored_block), linha.profile) == (True, "Noiva")


def test_o_perfil_do_historico_vem_da_sessao_e_nao_do_corpo(api):
    resposta = api.noivo.put(
        f"{BASE}/milestones/{marco_id('C01')}/state",
        json={"state": "Em andamento", "version": 1, "profile": "Noiva", "created_by": "x"},
    )
    assert resposta.status_code == 200
    [linha] = historico(api)
    assert linha.profile == "Noivo"


def test_ignorar_o_bloqueio_em_marco_livre_nao_registra_que_ignorou(api):
    mudar_estado(api.noivo, "C01", "Em andamento", ignorar=True)
    [linha] = historico(api)
    assert bool(linha.ignored_block) is False


def test_repetir_o_estado_nao_grava_historico_nem_sobe_a_version(api):
    mudar_estado(api.noivo, "C01", "Em andamento")
    resposta = mudar_estado(api.noivo, "C01", "Em andamento")
    assert resposta.status_code == 200
    assert len(historico(api)) == 1
    assert marco(resposta.json(), "C01")["version"] == 2


def test_reabrir_manda_state_nulo_e_volta_ao_estado_derivado(api):  # F-CRN-03, regra 5
    mudar_estado(api.noivo, "C01", "Concluído")
    api.clock.advance(seconds=1)
    reaberto = mudar_estado(api.noivo, "C01", None)
    assert marco(reaberto.json(), "C01")["state"] == "Destravado"
    assert [(h.state_before, h.state_after) for h in historico(api)] == [
        (None, "Concluído"),
        ("Concluído", None),
    ]


def test_estado_fora_dos_dois_marcaveis_e_422_do_contrato(api):
    for estado in ("Bloqueado", "Destravado", "Atrasado", "qualquer"):
        resposta = mudar_estado(api.noivo, "C01", estado)
        assert (resposta.status_code, resposta.json()["code"]) == (422, "validation_error")


def test_o_corpo_do_estado_exige_o_state_explicito(api):
    resposta = api.noivo.put(f"{BASE}/milestones/{marco_id('C01')}/state", json={"version": 1})
    assert (resposta.status_code, resposta.json()["code"]) == (422, "validation_error")


def test_prazo_ontem_destravado_aparece_atrasado_e_concluir_apaga_o_sinal(api):  # F-CRN-03
    ontem = (api.clock.now() - timedelta(days=1)).date().isoformat()
    editado = editar(api.noivo, "C01", target_date=ontem)
    assert editado.status_code == 200
    item = marco(editado.json(), "C01")
    assert (item["state"], item["overdue"], item["target_date"]) == ("Destravado", True, ontem)
    concluido = mudar_estado(api.noivo, "C01", "Concluído")
    assert marco(concluido.json(), "C01")["overdue"] is False


def test_o_dia_de_hoje_e_o_de_brasilia(api):
    api.clock._now = datetime(2026, 10, 28, 1, 0, tzinfo=UTC)  # 22:00 de 27/10 em Brasília
    assert (
        marco(editar(api.noivo, "C01", target_date="2026-10-27").json(), "C01")["overdue"] is False
    )
    api.clock._now = datetime(2026, 10, 28, 3, 0, tzinfo=UTC)
    assert marco(cronograma(api.noivo), "C01")["overdue"] is True


def test_reabrir_o_c06_bloqueia_os_nao_concluidos_e_avisa_os_concluidos(api):  # F-CRN-03, regra 5
    classificar_todas(api.noivo)
    concluir(api.noivo, "C01", "C02", "C03", "C04", "C05", "C06", "C07")
    reaberto = mudar_estado(api.noiva, "C06", None).json()
    nao_concluido = marco(reaberto, "C08")
    assert (nao_concluido["state"], rotulos(nao_concluido)) == ("Bloqueado", ["Fechar o Espaço"])
    concluido = marco(reaberto, "C07")
    assert concluido["state"] == "Concluído"
    assert concluido["warnings"] == [
        {
            "kind": "depends_on_unresolved",
            "milestone_id": str(marco_id("C06")),
            "title": "Fechar o Espaço",
        }
    ]
    assert concluido["version"] == marco(cronograma(api.noivo), "C07")["version"]


def test_cada_marco_traz_depende_de_e_libera(api):  # F-CRN-09
    c06 = marco(cronograma(api.noivo), "C06")
    assert c06["depends_on"] == [
        {
            "id": str(marco_id("C05")),
            "title": "Definir a data (ou janela de datas)",
            "resolved": False,
        }
    ]
    assert [u["id"] for u in c06["unlocks"]][:3] == [
        str(marco_id(c)) for c in ("C07", "C08", "C09")
    ]


def test_o_progresso_da_fase_conta_os_concluidos_sem_os_arquivados(api):
    classificar_todas(api.noivo)
    classificar(api.noivo, "Fotografia", "Fica de fora", "Sem foto")
    concluir(api.noivo, "C01", "C02")
    fases = {f["title"]: f["progress"] for f in cronograma(api.noivo)["phases"]}
    assert fases["Marco Zero"] == {"done": 2, "total": 4}
    assert fases["Fornecedores Essenciais"] == {"done": 0, "total": 6}


def test_com_data_exata_definida_o_cronograma_diz_que_ha_data_e_calcula_as_janelas(api):
    definir = api.noivo.put(
        "/api/v1/wedding/baseline/date",
        json={
            "value": {"kind": "exata", "exact": "2027-06-12"},
            "status": "Definido",
            "note": None,
            "version": 1,
        },
    )
    assert definir.status_code == 200
    corpo = cronograma(api.noivo)
    assert corpo["has_exact_date"] is True
    # F-CRN-05: nenhum prazo MANUAL nasce da data; o que nasce é o prazo efetivo (fim da janela).
    assert {m["target_date"] for f in corpo["phases"] for m in f["milestones"]} == {None}
    c06 = marco(corpo, "C06")
    assert (c06["window_start"], c06["window_end"]) == ("2026-04-12", "2026-08-12")
    assert c06["effective_target"] == "2026-08-12"
    assert marco(corpo, "C01")["effective_target"] is None  # sem janela e sem prazo manual


def test_data_em_janela_ou_ainda_em_definicao_nao_liga_o_modo_com_data(api):
    api.noivo.put(
        "/api/v1/wedding/baseline/date",
        json={
            "value": {"kind": "exata", "exact": "2027-06-12"},
            "status": "Em definição",
            "note": None,
            "version": 1,
        },
    )
    assert cronograma(api.noivo)["has_exact_date"] is False
    api.noivo.put(
        "/api/v1/wedding/baseline/date",
        json={
            "value": {
                "kind": "janela",
                "window_start": {"year": 2027, "month": 5},
                "window_end": {"year": 2027, "month": 7},
            },
            "status": "Definido",
            "note": None,
            "version": 2,
        },
    )
    assert cronograma(api.noivo)["has_exact_date"] is False


def test_editar_troca_responsavel_nota_e_prazo_e_devolve_o_cronograma_inteiro(api):  # F-CRN-01
    resposta = editar(
        api.noiva,
        "C06",
        responsible="Noiva",
        note="  Visitar dois espaços ",
        target_date="2027-01-15",
    )
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert len(corpo["phases"]) == 5
    item = marco(corpo, "C06")
    assert (item["responsible"], item["note"], item["target_date"], item["version"]) == (
        "Noiva",
        "Visitar dois espaços",
        "2027-01-15",
        2,
    )
    assert marco(corpo, "C07")["version"] == 1


def test_editar_pode_limpar_nota_e_prazo(api):
    editar(api.noivo, "C06", note="nota", target_date="2027-01-15")
    limpo = editar(api.noivo, "C06", note=None, target_date=None)
    item = marco(limpo.json(), "C06")
    assert (item["note"], item["target_date"], item["responsible"]) == (None, None, "Ambos")


def test_a_autoria_da_edicao_vem_da_sessao(api):
    editar(api.noiva, "C06", responsible="Noivo")
    engine = create_engine(api.url)
    with engine.connect() as conn:
        autor = conn.execute(
            text("SELECT updated_by FROM milestones WHERE id = :id"),
            {"id": marco_id("C06").hex},
        ).scalar_one()
        noiva = conn.execute(
            text("SELECT id FROM users WHERE username = 'exemplo.noiva'")
        ).scalar_one()
    engine.dispose()
    assert autor == noiva


def test_edicao_com_version_velha_e_409_e_nao_muda_nada(api):
    editar(api.noivo, "C06", responsible="Noivo")
    resposta = editar(api.noiva, "C06", responsible="Noiva", versao=1)
    assert (resposta.status_code, resposta.json()["code"]) == (409, "version_conflict")
    assert marco(cronograma(api.noivo), "C06")["responsible"] == "Noivo"


def test_mudar_estado_com_version_velha_e_409(api):
    mudar_estado(api.noivo, "C01", "Em andamento")
    resposta = mudar_estado(api.noiva, "C01", "Concluído", versao=1)
    assert (resposta.status_code, resposta.json()["code"]) == (409, "version_conflict")


def test_a_version_e_por_marco_e_editar_um_nao_conflita_com_outro(api):
    editar(api.noivo, "C01", responsible="Noivo")
    assert editar(api.noiva, "C02", responsible="Noiva", versao=1).status_code == 200


def test_edicao_invalida_e_422(api):
    nota = editar(api.noivo, "C01", note="x" * 501)
    assert (nota.status_code, nota.json()["code"]) == (422, "invalid_schedule_value")
    assert "500" in nota.json()["detail"]
    ano = editar(api.noivo, "C01", target_date="1999-12-31")
    assert (ano.status_code, ano.json()["code"]) == (422, "invalid_schedule_value")
    data = editar(api.noivo, "C01", target_date="31/12/2027")
    assert (data.status_code, data.json()["code"]) == (422, "validation_error")
    responsavel = editar(api.noivo, "C01", responsible="Todos")
    assert (responsavel.status_code, responsavel.json()["code"]) == (422, "validation_error")
    sem_responsavel = api.noivo.put(
        f"{BASE}/milestones/{marco_id('C01')}", json={"note": None, "version": 1}
    )
    assert sem_responsavel.status_code == 422


def test_marco_inexistente_e_404(api):
    desconhecido = "00000000-0000-0000-0000-000000000abc"
    corpo = {
        "title": "Marco Exemplo",
        "phase_id": str(fase_id(1)),
        "responsible": "Ambos",
        "category_id": None,
        "note": None,
        "target_date": None,
        "version": 1,
    }
    assert api.noivo.put(f"{BASE}/milestones/{desconhecido}", json=corpo).status_code == 404
    estado = api.noivo.put(
        f"{BASE}/milestones/{desconhecido}/state", json={"state": None, "version": 1}
    )
    assert estado.status_code == 404


def test_o_cronograma_ordena_pela_fase_e_pela_posicao(api):
    corpo = cronograma(api.noivo)
    assert [f["position"] for f in corpo["phases"]] == [0, 1, 2, 3, 4]
    for fase in corpo["phases"]:
        assert [m["position"] for m in fase["milestones"]] == list(range(len(fase["milestones"])))


def test_concluido_ignorando_o_bloqueio_avisa_os_predecessores_nao_resolvidos(api):  # F-CRN-03
    corpo = mudar_estado(api.noivo, "C03", "Concluído", ignorar=True).json()
    assert [(w["kind"], w["title"]) for w in marco(corpo, "C03")["warnings"]] == [
        ("depends_on_unresolved", "Classificar o Mapa de Escopo"),
        ("depends_on_unresolved", "Montar a lista preliminar de convidados"),
    ]


def test_concluido_para_em_andamento_com_predecessor_pendente_e_422_sem_ignorar(api):  # F-CRN-03
    mudar_estado(api.noivo, "C03", "Concluído", ignorar=True)
    api.clock.advance(seconds=1)
    recusado = mudar_estado(api.noivo, "C03", "Em andamento")
    assert (recusado.status_code, recusado.json()["code"]) == (422, "milestone_blocked")
    assert len(historico(api)) == 1
    aceito = mudar_estado(api.noivo, "C03", "Em andamento", ignorar=True)
    assert aceito.status_code == 200
    ultima = historico(api)[-1]
    assert (ultima.state_before, ultima.state_after, bool(ultima.ignored_block)) == (
        "Concluído",
        "Em andamento",
        True,
    )


def test_libera_nao_mostra_o_marco_arquivado(api):  # F-CRN-04
    classificar_todas(api.noivo)
    classificar(api.noivo, "Fotografia", "Fica de fora", "Sem foto")
    liberados = [u["id"] for u in marco(cronograma(api.noivo), "C06")["unlocks"]]
    assert str(marco_id("C08")) not in liberados
    assert str(marco_id("C07")) in liberados


def test_a_descricao_de_ignore_block_diz_a_regra_inteira(api):
    esquema = api.app.openapi()["components"]["schemas"]["MilestoneStateIn"]
    descricao = esquema["properties"]["ignore_block"]["description"]
    assert "Em andamento" in descricao
    assert "Concluído" in descricao
    assert "em discussão" in descricao.lower()
    assert "dependência não resolvida" in descricao
    assert "milestone_blocked" in descricao
    assert "marco Bloqueado" not in descricao
