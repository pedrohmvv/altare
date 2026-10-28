from datetime import date

import pytest
from tests.modules.wedding.conftest import NOIVA, NOIVO

from wedding.modules.wedding.application.commands.update_baseline_field import (
    UpdateBaselineFieldCommand,
)
from wedding.modules.wedding.domain.errors import BaselineValueRequired
from wedding.modules.wedding.domain.value_objects import (
    BaselineKey,
    CeilingValue,
    DateKind,
    DateValue,
    DefinitionStatus,
    TextValue,
)
from wedding.shared_kernel.errors import VersionConflict
from wedding.shared_kernel.profile import ProfileKind


def _definir_cidade(world, texto="Cidade Exemplo", versao=1, ator=NOIVO, **extra):
    return world.use_cases().update_baseline_field.execute(
        UpdateBaselineFieldCommand(
            key=BaselineKey.CITY,
            value=TextValue(texto),
            status=extra.get("status", DefinitionStatus.DEFINED),
            note=extra.get("note"),
            version=versao,
        ),
        ator,
    )


def test_casamento_novo_tem_todos_os_campos_vazios_e_em_definicao(world):  # F-PLN-01
    baseline = world.use_cases().get_baseline.execute(NOIVO)
    for campo in (
        baseline.date,
        baseline.city,
        baseline.format,
        baseline.size,
        baseline.ceiling,
        baseline.ceremony,
    ):
        assert campo.value is None
        assert campo.status is DefinitionStatus.IN_DEFINITION
        assert campo.note is None


def test_definir_um_campo_devolve_o_quadro_com_o_valor_e_a_versao_nova(world):
    baseline = _definir_cidade(world, note="decidimos juntos")
    assert baseline.city.value == TextValue("Cidade Exemplo")
    assert baseline.city.status is DefinitionStatus.DEFINED
    assert baseline.city.note == "decidimos juntos"
    assert baseline.city.version == 2
    assert baseline.format.version == 1


def test_o_teto_e_gravado_em_centavos(world):  # F-PLN-01: R$ 28.000,00 vira 2800000
    baseline = world.use_cases().update_baseline_field.execute(
        UpdateBaselineFieldCommand(
            BaselineKey.CEILING, CeilingValue(2_800_000), DefinitionStatus.DEFINED, None, 1
        ),
        NOIVA,
    )
    assert baseline.ceiling.value == CeilingValue(2_800_000)


def test_qualquer_dos_dois_edita_sem_aprovacao_conjunta(world):  # F-PLN-01, regra 5
    _definir_cidade(world, ator=NOIVO)
    baseline = _definir_cidade(world, "Outra Cidade Exemplo", versao=2, ator=NOIVA)
    assert baseline.city.value == TextValue("Outra Cidade Exemplo")


def test_definido_sem_valor_e_bloqueado_sem_registrar_nada(world):
    with pytest.raises(BaselineValueRequired):
        world.use_cases().update_baseline_field.execute(
            UpdateBaselineFieldCommand(BaselineKey.CITY, None, DefinitionStatus.DEFINED, None, 1),
            NOIVO,
        )
    assert world.changes == []
    assert world.fields[BaselineKey.CITY].version == 1


def test_versao_velha_da_conflito_e_nao_grava(world):
    _definir_cidade(world, versao=1, ator=NOIVO)
    with pytest.raises(VersionConflict):
        _definir_cidade(world, "Outra Cidade Exemplo", versao=1, ator=NOIVA)
    assert world.fields[BaselineKey.CITY].value == {"text": "Cidade Exemplo"}
    assert len(world.changes) == 1


def test_a_alteracao_fica_no_historico_com_antes_depois_e_perfil(world, clock):  # F-PLN-01, regra 3
    exata = DateValue(kind=DateKind.EXACT, exact=date(2027, 5, 1))
    outra = DateValue(kind=DateKind.EXACT, exact=date(2027, 6, 5))
    casos = world.use_cases()
    casos.update_baseline_field.execute(
        UpdateBaselineFieldCommand(BaselineKey.DATE, exata, DefinitionStatus.DEFINED, None, 1),
        NOIVO,
    )
    clock.advance(hours=1)
    casos.update_baseline_field.execute(
        UpdateBaselineFieldCommand(BaselineKey.DATE, outra, DefinitionStatus.DEFINED, None, 2),
        NOIVA,
    )

    primeira, segunda = reversed(casos.list_baseline_changes.execute(NOIVO))
    assert primeira.before.value is None
    assert primeira.after.value == exata
    assert primeira.profile is ProfileKind.NOIVO
    assert segunda.before.value == exata  # o valor anterior fica registrado
    assert segunda.after.value == outra
    assert segunda.profile is ProfileKind.NOIVA
    assert segunda.changed_at > primeira.changed_at


def test_historico_vem_do_mais_novo_para_o_mais_antigo_e_respeita_o_limite(world):
    for versao, cidade in enumerate(["A Exemplo", "B Exemplo", "C Exemplo"], start=1):
        _definir_cidade(world, cidade, versao=versao)
    todas = world.use_cases().list_baseline_changes.execute(NOIVO)
    assert [c.after.value for c in todas] == [
        TextValue("C Exemplo"),
        TextValue("B Exemplo"),
        TextValue("A Exemplo"),
    ]
    assert len(world.use_cases().list_baseline_changes.execute(NOIVO, limit=2)) == 2


def test_repetir_o_mesmo_estado_nao_gera_historico_nem_sobe_a_versao(world):
    _definir_cidade(world, versao=1)
    baseline = _definir_cidade(world, versao=2)
    assert baseline.city.version == 2
    assert len(world.changes) == 1


def test_voltar_a_em_definicao_e_permitido_e_registrado(world):  # F-PLN-01, regra 4
    _definir_cidade(world, versao=1)
    baseline = _definir_cidade(
        world, versao=2, status=DefinitionStatus.IN_DEFINITION, note="em dúvida"
    )
    assert baseline.city.status is DefinitionStatus.IN_DEFINITION
    assert baseline.city.value == TextValue("Cidade Exemplo")
    ultima = world.use_cases().list_baseline_changes.execute(NOIVO)[0]
    assert ultima.before.status is DefinitionStatus.DEFINED
    assert ultima.after.status is DefinitionStatus.IN_DEFINITION


def test_o_ator_da_sessao_vai_para_a_transacao(world):
    _definir_cidade(world, ator=NOIVA)
    assert world.actors == [NOIVA]
