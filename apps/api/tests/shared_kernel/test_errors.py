import pytest

from wedding.shared_kernel.errors import (
    Conflict,
    DomainError,
    DomainRuleViolated,
    Forbidden,
    NotFound,
    Unauthenticated,
    VersionConflict,
)


@pytest.mark.parametrize(
    ("erro", "codigo"),
    [
        (NotFound, "not_found"),
        (Forbidden, "forbidden"),
        (Unauthenticated, "unauthenticated"),
        (VersionConflict, "version_conflict"),
    ],
)
def test_erro_base_traz_o_code_estavel_de_maquina(erro, codigo):
    assert erro().code == codigo


def test_code_pode_ser_especifico_da_regra():
    assert DomainRuleViolated("proposal_already_decided").code == "proposal_already_decided"
    assert Conflict("duplicate_contact").code == "duplicate_contact"


@pytest.mark.parametrize("erro", [DomainRuleViolated, Conflict])
def test_regra_e_conflito_exigem_um_code(erro):
    with pytest.raises(ValueError, match="code"):
        erro()


def test_conflito_de_versao_e_um_conflito():
    assert issubclass(VersionConflict, Conflict)


def test_todo_erro_de_dominio_herda_de_domain_error():
    for erro in (NotFound, Forbidden, Unauthenticated, Conflict, DomainRuleViolated):
        assert issubclass(erro, DomainError)


def test_texto_do_erro_e_o_proprio_code():
    assert str(NotFound()) == "not_found"
