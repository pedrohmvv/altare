"""A superfície pública do `wedding` (`application/public.py`): o que o cronograma lê."""

from datetime import date

from tests.modules.wedding.conftest import NOIVO

from wedding.modules.wedding.application import public
from wedding.modules.wedding.application.commands.change_scope_status import (
    ChangeScopeStatusCommand,
)
from wedding.modules.wedding.application.commands.create_scope_category import (
    CreateScopeCategoryCommand,
)
from wedding.modules.wedding.application.commands.delete_scope_category import (
    DeleteScopeCategoryCommand,
)
from wedding.modules.wedding.application.commands.set_scope_category_visibility import (
    SetScopeCategoryVisibilityCommand,
)
from wedding.modules.wedding.application.commands.set_scope_group_visibility import (
    SetScopeGroupVisibilityCommand,
)
from wedding.modules.wedding.application.commands.update_baseline_field import (
    UpdateBaselineFieldCommand,
)
from wedding.modules.wedding.domain.value_objects import (
    BaselineKey,
    DateKind,
    DateValue,
    DefinitionStatus,
    MonthYear,
)


def _definir_data(world, value, status=DefinitionStatus.DEFINED, versao=1):
    world.use_cases().update_baseline_field.execute(
        UpdateBaselineFieldCommand(BaselineKey.DATE, value, status, None, versao), NOIVO
    )


def test_a_superficie_publica_exporta_so_o_que_o_cronograma_le():
    assert {
        "CategoryStanding",
        "DateKind",
        "DefinitionStatus",
        "GetScopeStandings",
        "GetWeddingDate",
        "ScopeStatus",
        "WeddingDate",
    } <= set(public.__all__)


def test_data_do_casamento_nasce_em_definicao_sem_forma_nem_valor(world):  # F-PLN-01
    data = world.use_cases().get_wedding_date.execute(NOIVO)
    assert data.status is DefinitionStatus.IN_DEFINITION
    assert (data.kind, data.exact) == (None, None)


def test_data_exata_definida_traz_a_forma_e_o_dia(world):
    _definir_data(world, DateValue(kind=DateKind.EXACT, exact=date(2027, 6, 12)))
    data = world.use_cases().get_wedding_date.execute(NOIVO)
    assert data.status is DefinitionStatus.DEFINED
    assert data.kind is DateKind.EXACT
    assert data.exact == date(2027, 6, 12)


def test_janela_definida_nao_traz_dia_exato(world):
    janela = DateValue(
        kind=DateKind.WINDOW,
        window_start=MonthYear(2027, 5),
        window_end=MonthYear(2027, 7),
    )
    _definir_data(world, janela)
    data = world.use_cases().get_wedding_date.execute(NOIVO)
    assert (data.status, data.kind, data.exact) == (
        DefinitionStatus.DEFINED,
        DateKind.WINDOW,
        None,
    )


def test_data_exata_ainda_em_definicao_continua_em_definicao(world):
    _definir_data(
        world,
        DateValue(kind=DateKind.EXACT, exact=date(2027, 6, 12)),
        status=DefinitionStatus.IN_DEFINITION,
    )
    data = world.use_cases().get_wedding_date.execute(NOIVO)
    assert data.status is DefinitionStatus.IN_DEFINITION
    assert data.exact == date(2027, 6, 12)


def test_categorias_trazem_nome_status_e_visibilidade(world):
    _grupo, categoria = world.seed_catalog()
    [item] = world.scope_use_cases().get_scope_standings.execute(NOIVO)
    assert item.id == categoria
    assert item.name == "Cerimônia civil"
    assert item.status is public.ScopeStatus.IN_DISCUSSION
    assert item.visible is True


def test_categoria_classificada_aparece_com_o_novo_status(world):
    _grupo, categoria = world.seed_catalog()
    world.scope_use_cases().change_scope_status.execute(
        ChangeScopeStatusCommand(categoria, public.ScopeStatus.MAYBE, None, 1), NOIVO
    )
    [item] = world.scope_use_cases().get_scope_standings.execute(NOIVO)
    assert item.status is public.ScopeStatus.MAYBE


def test_categoria_oculta_ou_de_grupo_oculto_vem_invisivel(world):  # F-CRN-04, regra 3
    grupo, categoria = world.seed_catalog()
    casos = world.scope_use_cases()
    casos.set_scope_category_visibility.execute(
        SetScopeCategoryVisibilityCommand(categoria, True, 1), NOIVO
    )
    assert casos.get_scope_standings.execute(NOIVO)[0].visible is False
    casos.set_scope_category_visibility.execute(
        SetScopeCategoryVisibilityCommand(categoria, False, 2), NOIVO
    )
    assert casos.get_scope_standings.execute(NOIVO)[0].visible is True
    casos.set_scope_group_visibility.execute(SetScopeGroupVisibilityCommand(grupo, True, 1), NOIVO)
    assert casos.get_scope_standings.execute(NOIVO)[0].visible is False


def test_categoria_do_casal_excluida_some_da_lista(world):
    grupo, _categoria = world.seed_catalog()
    casos = world.scope_use_cases()
    mapa = casos.create_scope_category.execute(
        CreateScopeCategoryCommand(grupo, "Frente Exemplo", None), NOIVO
    )
    nova = next(c for g in mapa.groups for c in g.categories if c.name == "Frente Exemplo")
    assert len(casos.get_scope_standings.execute(NOIVO)) == 2
    casos.delete_scope_category.execute(DeleteScopeCategoryCommand(nova.id, nova.version), NOIVO)
    assert [i.name for i in casos.get_scope_standings.execute(NOIVO)] == ["Cerimônia civil"]
