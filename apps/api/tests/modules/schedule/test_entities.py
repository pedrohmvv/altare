from datetime import date
from uuid import UUID

import pytest

from wedding.modules.schedule.domain.entities import Milestone
from wedding.modules.schedule.domain.errors import InvalidMilestoneWindow, InvalidScheduleValue
from wedding.modules.schedule.domain.values import MAX_NOTE, ManualState
from wedding.modules.schedule.domain.windows import Window, WindowUnit
from wedding.shared_kernel.errors import DomainRuleViolated
from wedding.shared_kernel.profile import ProfileKind


def novo():
    return Milestone(id=UUID(int=1), phase_id=UUID(int=2), title="Marco Exemplo", position=0)


def test_marco_nasce_com_responsavel_ambos_sem_prazo_e_sem_estado_manual():  # F-CRN-02, regra 3
    marco = novo()
    assert marco.responsible is ProfileKind.AMBOS
    assert (marco.target_date, marco.note, marco.manual_state) == (None, None, None)


def test_editar_troca_responsavel_nota_e_prazo():  # F-CRN-01
    marco = novo()
    assert marco.edit(ProfileKind.NOIVA, "  Ligar na segunda  ", date(2027, 1, 10)) is True
    assert (marco.responsible, marco.note, marco.target_date) == (
        ProfileKind.NOIVA,
        "Ligar na segunda",
        date(2027, 1, 10),
    )


def test_editar_igual_nao_e_mudanca():
    marco = novo()
    marco.edit(ProfileKind.NOIVO, "nota", date(2027, 1, 10))
    assert marco.edit(ProfileKind.NOIVO, " nota ", date(2027, 1, 10)) is False


def test_nota_em_branco_vira_ausencia_e_prazo_pode_ser_limpo():
    marco = novo()
    marco.edit(ProfileKind.AMBOS, "nota", date(2027, 1, 10))
    assert marco.edit(ProfileKind.AMBOS, "   ", None) is True
    assert (marco.note, marco.target_date) == (None, None)


def test_nota_acima_do_limite_e_recusada_sem_cortar():
    with pytest.raises(InvalidScheduleValue):
        novo().edit(ProfileKind.AMBOS, "x" * (MAX_NOTE + 1), None)
    assert novo().edit(ProfileKind.AMBOS, "x" * MAX_NOTE, None) is True


@pytest.mark.parametrize("ano", [1999, 2101])
def test_prazo_fora_do_intervalo_e_recusado(ano):
    with pytest.raises(InvalidScheduleValue):
        novo().edit(ProfileKind.AMBOS, None, date(ano, 1, 1))


def test_o_erro_de_valor_e_de_dominio_com_codigo_proprio():
    assert issubclass(InvalidScheduleValue, DomainRuleViolated)
    assert InvalidScheduleValue().code == "invalid_schedule_value"


def test_marcar_e_reabrir_mudam_o_estado_manual_e_repetir_nao():  # F-CRN-03
    marco = novo()
    assert marco.set_manual_state(ManualState.DONE) is True
    assert marco.manual_state is ManualState.DONE
    assert marco.set_manual_state(ManualState.DONE) is False
    assert marco.set_manual_state(None) is True
    assert marco.manual_state is None
    assert marco.set_manual_state(None) is False


# --- F-CRN-01: criar, renomear, mover, excluir e restaurar -------------------------------------
from datetime import UTC, datetime  # noqa: E402

from wedding.modules.schedule.domain.entities import Phase  # noqa: E402
from wedding.modules.schedule.domain.errors import (  # noqa: E402
    DependencyCycle,
    InvalidPhaseOrder,
    MilestoneTitleRequired,
    PhaseTitleRequired,
    SelfDependency,
)
from wedding.modules.schedule.domain.values import MAX_PHASE_TITLE, MAX_TITLE  # noqa: E402


def test_marco_sem_titulo_ou_so_com_espacos_e_recusado():  # F-CRN-01
    for titulo in ("", "   ", "\t\n"):
        with pytest.raises(MilestoneTitleRequired):
            Milestone(id=UUID(int=1), phase_id=UUID(int=2), title=titulo, position=0)


def test_titulo_do_marco_e_aparado_e_tem_limite_da_coluna():
    marco = Milestone(id=UUID(int=1), phase_id=UUID(int=2), title="  Marco Exemplo ", position=0)
    assert marco.title == "Marco Exemplo"
    Milestone(id=UUID(int=1), phase_id=UUID(int=2), title="x" * MAX_TITLE, position=0)
    with pytest.raises(InvalidScheduleValue):
        Milestone(id=UUID(int=1), phase_id=UUID(int=2), title="x" * (MAX_TITLE + 1), position=0)


def test_renomear_o_marco_diz_se_mudou_e_recusa_titulo_vazio():
    marco = novo()
    assert marco.rename("Outro Marco") is True
    assert marco.rename(" Outro Marco ") is False
    with pytest.raises(MilestoneTitleRequired):
        marco.rename("  ")
    assert marco.title == "Outro Marco"


def test_trocar_a_categoria_diz_se_mudou_e_aceita_nenhuma():  # F-CRN-04
    marco = novo()
    categoria = UUID(int=77)
    assert marco.link_category(categoria) is True
    assert marco.link_category(categoria) is False
    assert marco.link_category(None) is True
    assert marco.category_id is None


def test_mover_de_fase_vai_para_a_posicao_dada_e_nao_mexe_em_mais_nada():  # F-CRN-01
    marco = novo()
    marco.set_manual_state(ManualState.DONE)
    assert marco.move_to(UUID(int=9), 4) is True
    assert (marco.phase_id, marco.position) == (UUID(int=9), 4)
    assert marco.manual_state is ManualState.DONE
    assert marco.move_to(UUID(int=9), 7) is False
    assert marco.position == 4


def test_excluir_carimba_e_restaurar_limpa_e_vai_para_o_fim_da_fase():  # F-CRN-01
    marco = novo()
    agora = datetime(2026, 11, 3, 12, 0, tzinfo=UTC)
    marco.delete(agora, UUID(int=5))
    assert (marco.deleted_at, marco.deleted_by) == (agora, UUID(int=5))
    marco.restore(position=12)
    assert (marco.deleted_at, marco.deleted_by, marco.position) == (None, None, 12)


def test_mexer_nas_dependencias_sobe_a_revisao_para_as_edicoes_se_conflitarem():
    marco = novo()
    assert marco.dependencies_revision == 0
    marco.touch_dependencies()
    assert marco.dependencies_revision == 1


def test_fase_sem_titulo_e_recusada_e_o_titulo_e_aparado():  # F-CRN-01
    with pytest.raises(PhaseTitleRequired):
        Phase(id=UUID(int=1), title="   ", position=0)
    fase = Phase(id=UUID(int=1), title="  Fase Exemplo ", position=0)
    assert fase.title == "Fase Exemplo"
    with pytest.raises(InvalidScheduleValue):
        Phase(id=UUID(int=1), title="x" * (MAX_PHASE_TITLE + 1), position=0)


def test_renomear_a_fase_diz_se_mudou():
    fase = Phase(id=UUID(int=1), title="Fase Exemplo", position=0)
    assert fase.rename("Outra Fase") is True
    assert fase.rename("Outra Fase") is False
    with pytest.raises(PhaseTitleRequired):
        fase.rename("")


def test_erro_de_ciclo_leva_o_caminho_nos_dados_e_no_texto():  # F-CRN-03, regra 2
    erro = DependencyCycle([(UUID(int=1), "A"), (UUID(int=2), "B"), (UUID(int=1), "A")])
    assert erro.code == "dependency_cycle"
    assert erro.data == {
        "path": [
            {"id": UUID(int=1), "title": "A"},
            {"id": UUID(int=2), "title": "B"},
            {"id": UUID(int=1), "title": "A"},
        ]
    }
    assert erro.detail_params == {"path": "A → B → A"}
    assert isinstance(erro, DomainRuleViolated)


def test_codigos_estaveis_dos_demais_erros_da_edicao():
    assert SelfDependency().code == "self_dependency"
    assert InvalidPhaseOrder().code == "invalid_phase_order"
    assert MilestoneTitleRequired().code == "milestone_title_required"
    assert PhaseTitleRequired().code == "phase_title_required"


# --- Janela do marco (F-CRN-05, regra 5) -------------------------------------------------------


def com_janela_sugerida():
    marco = novo()
    marco.window_start_before, marco.window_end_before, marco.window_unit = 14, 10, "meses"
    return marco


def test_marco_nasce_sem_janela_e_sem_ter_sido_editado():
    marco = novo()
    assert (marco.window_start_before, marco.window_end_before, marco.window_unit) == (
        None,
        None,
        None,
    )
    assert marco.window_edited is False
    assert marco.window is None


def test_a_janela_do_marco_vem_dos_tres_deslocamentos():
    assert com_janela_sugerida().window == Window(14, 10, WindowUnit.MONTHS)


def test_editar_a_janela_troca_os_tres_valores_e_marca_como_editada():  # F-CRN-05, regra 5
    marco = com_janela_sugerida()
    assert marco.set_window(12, 8, WindowUnit.WEEKS) is True
    assert (marco.window_start_before, marco.window_end_before, marco.window_unit) == (
        12,
        8,
        "semanas",
    )
    assert marco.window_edited is True


def test_confirmar_a_mesma_janela_pela_primeira_vez_ja_deixa_de_ser_sugestao():
    marco = com_janela_sugerida()
    assert marco.set_window(14, 10, WindowUnit.MONTHS) is True
    assert marco.window_edited is True


def test_repetir_a_janela_ja_editada_nao_e_mudanca():
    marco = com_janela_sugerida()
    marco.set_window(12, 8, WindowUnit.MONTHS)
    assert marco.set_window(12, 8, WindowUnit.MONTHS) is False


def test_dar_janela_a_marco_sem_janela_e_mudanca():
    marco = novo()
    assert marco.set_window(3, 1, WindowUnit.MONTHS) is True
    assert marco.window == Window(3, 1, WindowUnit.MONTHS)
    assert marco.window_edited is True


@pytest.mark.parametrize(("inicio", "fim"), [(1, 2), (3, -1), (121, 0)])
def test_janela_invalida_e_recusada_e_nao_muda_o_marco(inicio, fim):
    marco = com_janela_sugerida()
    with pytest.raises(InvalidMilestoneWindow):
        marco.set_window(inicio, fim, WindowUnit.MONTHS)
    assert (marco.window, marco.window_edited) == (Window(14, 10, WindowUnit.MONTHS), False)
