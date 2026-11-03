"""A cola do `bootstrap` entre o cronograma e o `wedding`: só ela conhece os dois módulos."""

from datetime import date
from types import SimpleNamespace
from uuid import UUID

import pytest
from tests.modules.schedule.conftest import NOIVO

from wedding.modules.schedule.application.ports import CategoryInfo, WeddingDate
from wedding.modules.schedule.domain.values import Standing
from wedding.modules.wedding.application.public import (
    CategoryStanding,
    DateKind,
    DefinitionStatus,
    ScopeStatus,
)
from wedding.modules.wedding.application.public import (
    WeddingDate as WeddingDateFound,
)
from wedding.platform.bootstrap.schedule import WeddingDateFromBaseline, WeddingScopeCategories


def _categorias(*itens: CategoryStanding):
    scope = SimpleNamespace(get_scope_standings=SimpleNamespace(execute=lambda actor: tuple(itens)))
    return WeddingScopeCategories(lambda: scope)  # type: ignore[arg-type]


def _data(achada: WeddingDateFound):
    wedding = SimpleNamespace(get_wedding_date=SimpleNamespace(execute=lambda actor: achada))
    return WeddingDateFromBaseline(lambda: wedding)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("status", "visivel", "esperado"),
    [
        (ScopeStatus.ESSENTIAL, True, Standing.ENTERS),
        (ScopeStatus.MAYBE, True, Standing.MAYBE),
        (ScopeStatus.IN_DISCUSSION, True, Standing.IN_DISCUSSION),
        (ScopeStatus.OUT, True, Standing.OUT),
        # Oculta, de grupo oculto ou excluída conta como `Fica de fora` (F-CRN-04, regra 3).
        (ScopeStatus.ESSENTIAL, False, Standing.OUT),
        (ScopeStatus.MAYBE, False, Standing.OUT),
        (ScopeStatus.IN_DISCUSSION, False, Standing.OUT),
    ],
)
def test_status_e_visibilidade_viram_a_situacao_da_categoria(status, visivel, esperado):
    identificador = UUID(int=7)
    categorias = _categorias(CategoryStanding(identificador, "Frente Exemplo", status, visivel))
    assert categorias.categories(NOIVO) == {identificador: CategoryInfo("Frente Exemplo", esperado)}


def test_sem_categorias_a_leitura_vem_vazia():
    assert _categorias().categories(NOIVO) == {}


@pytest.mark.parametrize(
    ("status", "forma", "dia", "esperado"),
    [
        (
            DefinitionStatus.DEFINED,
            DateKind.EXACT,
            date(2027, 6, 12),
            WeddingDate(True, date(2027, 6, 12)),
        ),
        (DefinitionStatus.DEFINED, DateKind.WINDOW, None, WeddingDate(True, None)),
        (
            DefinitionStatus.IN_DEFINITION,
            DateKind.EXACT,
            date(2027, 6, 12),
            WeddingDate(False, date(2027, 6, 12)),
        ),
        (DefinitionStatus.IN_DEFINITION, None, None, WeddingDate(False, None)),
    ],
)
def test_a_data_do_casamento_so_vale_com_status_definido_e_forma_exata(
    status, forma, dia, esperado
):
    lida = _data(WeddingDateFound(status, forma, dia)).wedding_date(NOIVO)
    assert lida == esperado
    assert lida.is_exact_and_defined is (status is DefinitionStatus.DEFINED and dia is not None)
