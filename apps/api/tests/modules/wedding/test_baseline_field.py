from uuid import uuid4

import pytest

from wedding.modules.wedding.domain.entities import BaselineField
from wedding.modules.wedding.domain.errors import BaselineValueRequired, InvalidBaselineValue
from wedding.modules.wedding.domain.value_objects import (
    BaselineKey,
    CeilingValue,
    DefinitionStatus,
    TextValue,
)


def _campo(chave: BaselineKey = BaselineKey.CITY) -> BaselineField:
    return BaselineField(id=uuid4(), key=chave, status=DefinitionStatus.IN_DEFINITION)


def test_campo_recem_criado_esta_vazio_e_em_definicao():
    campo = _campo()
    assert campo.value is None
    assert campo.note is None
    assert campo.status is DefinitionStatus.IN_DEFINITION


def test_definir_com_valor_grava_valor_e_status():
    campo = _campo()
    mudou = campo.update(TextValue("Cidade Exemplo"), DefinitionStatus.DEFINED, None)
    assert mudou is True
    assert campo.status is DefinitionStatus.DEFINED
    assert campo.value == {"text": "Cidade Exemplo"}


def test_definido_sem_valor_e_bloqueado_e_nada_muda():  # F-PLN-01, regra 1
    campo = _campo()
    with pytest.raises(BaselineValueRequired):
        campo.update(None, DefinitionStatus.DEFINED, None)
    assert campo.status is DefinitionStatus.IN_DEFINITION


def test_limpar_o_valor_de_um_campo_definido_e_bloqueado():
    campo = _campo()
    campo.update(TextValue("Cidade Exemplo"), DefinitionStatus.DEFINED, None)
    with pytest.raises(BaselineValueRequired):
        campo.update(None, DefinitionStatus.DEFINED, None)
    assert campo.value == {"text": "Cidade Exemplo"}


def test_voltar_a_em_definicao_mantem_o_valor():  # F-PLN-01, regra 4
    campo = _campo()
    campo.update(TextValue("Cidade Exemplo"), DefinitionStatus.DEFINED, None)
    campo.update(TextValue("Cidade Exemplo"), DefinitionStatus.IN_DEFINITION, "em dúvida")
    assert campo.status is DefinitionStatus.IN_DEFINITION
    assert campo.value == {"text": "Cidade Exemplo"}
    assert campo.note == "em dúvida"


def test_em_definicao_pode_ter_valor_provisorio_ou_nenhum():
    campo = _campo()
    campo.update(None, DefinitionStatus.IN_DEFINITION, "ainda não conversamos")
    assert campo.value is None
    assert campo.note == "ainda não conversamos"


def test_repetir_o_mesmo_estado_nao_conta_como_mudanca():
    campo = _campo()
    campo.update(TextValue("Cidade Exemplo"), DefinitionStatus.DEFINED, "ok")
    assert campo.update(TextValue("Cidade Exemplo"), DefinitionStatus.DEFINED, "ok") is False


def test_nota_perde_espacos_e_em_branco_vira_nada():
    campo = _campo()
    campo.update(None, DefinitionStatus.IN_DEFINITION, "  por quê  ")
    assert campo.note == "por quê"
    campo.update(None, DefinitionStatus.IN_DEFINITION, "   ")
    assert campo.note is None


def test_nota_longa_demais_e_recusada():
    with pytest.raises(InvalidBaselineValue):
        _campo().update(None, DefinitionStatus.IN_DEFINITION, "x" * 501)


def test_valor_de_outro_tipo_para_a_chave_e_erro_de_programacao():
    with pytest.raises(TypeError):
        _campo(BaselineKey.CEILING).update(TextValue("x"), DefinitionStatus.DEFINED, None)


def test_retrato_guarda_status_valor_e_nota():
    campo = _campo(BaselineKey.CEILING)
    campo.update(CeilingValue(2_800_000), DefinitionStatus.DEFINED, "teto macro")
    assert campo.snapshot() == {
        "status": "Definido",
        "value": {"cents": 2_800_000},
        "note": "teto macro",
    }
