"""Os textos dos erros (`platform/http/messages.py`): todo `{campo}` do `detail` tem dono."""

from string import Formatter
from uuid import UUID

import pytest

import wedding.modules.files.domain.errors
import wedding.modules.guests.domain.errors
import wedding.modules.identity.domain.errors
import wedding.modules.schedule.domain.errors
import wedding.modules.wedding.domain.errors  # noqa: F401
from wedding.modules.schedule.domain.errors import DependencyCycle
from wedding.platform.http.messages import MESSAGES
from wedding.platform.http.problem import problem_response
from wedding.shared_kernel.errors import DomainError, DomainRuleViolated


def _erros(base=DomainError):
    for erro in base.__subclasses__():
        yield erro
        yield from _erros(erro)


def _campos(texto: str) -> set[str]:
    return {nome for _, nome, _, _ in Formatter().parse(texto) if nome}


COM_CAMPOS = {code: _campos(m.detail) for code, m in MESSAGES.items() if _campos(m.detail)}


def test_so_o_ciclo_de_dependencias_usa_campos_no_texto_hoje():
    assert {"dependency_cycle": {"path"}} == COM_CAMPOS


@pytest.mark.parametrize("code", sorted(COM_CAMPOS))
def test_todo_code_com_campo_tem_um_erro_dono_que_declara_exatamente_esses_campos(code):
    donos = [e for e in _erros() if e.default_code == code]
    assert donos, f"{code} tem campo no texto e nenhum erro de domínio o lança"
    for dono in donos:
        assert dono.detail_params_keys == COM_CAMPOS[code], dono.__name__


def test_o_erro_de_ciclo_preenche_os_campos_que_declara():
    erro = DependencyCycle([(UUID(int=1), "A"), (UUID(int=2), "B"), (UUID(int=1), "A")])
    assert set(erro.detail_params) == DependencyCycle.detail_params_keys


def test_code_com_campo_lancado_sem_os_parametros_nao_vira_erro_interno():
    resposta = problem_response(422, "dependency_cycle")
    assert resposta.status_code == 422
    assert b"{path}" not in resposta.body


def test_codes_sem_campo_continuam_sem_parametros():
    sem_campo = DomainRuleViolated("proposal_already_decided")
    assert sem_campo.detail_params == {}


@pytest.mark.parametrize(
    ("code", "esperado", "proibido"),
    [
        (
            "dependency_cycle",
            ["Removam uma dessas dependências", "escolham outro marco"],
            ["Remova ", "escolha "],
        ),
        ("self_dependency", ["Escolham outro marco"], ["Escolha "]),
        (
            "category_not_available",
            ["Escolham outra", "mostrem a categoria"],
            ["Escolha ", "mostre "],
        ),
        ("invalid_phase_order", ["Recarreguem", "tentem de novo"], ["Recarregue ", "tente "]),
        ("milestone_title_required", ["Escrevam o título do marco"], ["Escreva "]),
        ("phase_title_required", ["Escrevam o título da fase"], ["Escreva "]),
        (
            "invalid_schedule_value",
            ["Confiram", "título do marco ou da tarefa", "120", "texto de um item", "200"],
            ["Confira "],
        ),
        (
            "milestone_blocked",
            ["Confirmem", "queiram ignorar o bloqueio", "marcá-lo"],
            ["Confirme ", "quer "],
        ),
        ("task_title_required", ["Escrevam o título da tarefa"], ["Escreva "]),
        ("checklist_text_required", ["Escrevam o texto do item"], ["Escreva "]),
        (
            "invalid_checklist_order",
            ["Recarreguem", "tentem de novo", "checklist"],
            ["Recarregue ", "tente "],
        ),
        ("checklist_full", ["50 itens", "Removam"], ["Remova "]),
        (
            "checklist_open_items",
            ["em aberto", "Confirmem", "mesmo assim", "ficam como estão"],
            ["Confirme "],
        ),
        (
            "invalid_preview_date",
            ["A data do casamento precisa estar entre os anos 2000 e 2100."],
            [],
        ),
        (
            "invalid_window",
            ["Confiram", "120 meses", "520 semanas", "início", "fim"],
            ["Confira ", "Use "],
        ),
    ],
)
def test_as_mensagens_da_edicao_do_cronograma_falam_com_o_casal_em_voces(code, esperado, proibido):
    detail = MESSAGES[code].detail
    for trecho in esperado:
        assert trecho in detail, (code, trecho)
    for trecho in proibido:
        assert trecho not in detail, (code, trecho)


def test_todo_erro_do_cronograma_tem_mensagem_propria():
    codes = {
        e.default_code
        for e in _erros()
        if e.__module__ == "wedding.modules.schedule.domain.errors" and e.default_code
    }
    assert codes <= MESSAGES.keys(), codes - MESSAGES.keys()


def test_a_mensagem_dos_itens_em_aberto_nao_leva_a_contagem_a_tela_a_monta():
    """A tela diz "há 3 itens em aberto" com o progresso que a leitura já traz: o texto do erro não
    leva `{open}` nem nenhum outro campo (F-CRN-07, regra 5)."""
    assert _campos(MESSAGES["checklist_open_items"].detail) == set()
    assert "checklist_open_items" not in COM_CAMPOS
