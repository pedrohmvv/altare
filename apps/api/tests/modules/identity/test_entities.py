from datetime import UTC, datetime
from uuid import uuid4

import pytest

from wedding.modules.identity.domain.entities import User, UserSession
from wedding.modules.identity.domain.errors import (
    DuplicateUsername,
    InvalidCredentials,
    ProfileTaken,
)
from wedding.shared_kernel.errors import (
    Conflict,
    DomainRuleViolated,
    Unauthenticated,
)
from wedding.shared_kernel.profile import ProfileKind


@pytest.mark.parametrize("perfil", [ProfileKind.NOIVO, ProfileKind.NOIVA])
def test_usuario_aceita_os_perfis_de_login(perfil):
    usuario = User(id=uuid4(), username="exemplo", profile=perfil, password_hash="hash")
    assert usuario.profile is perfil


def test_usuario_nao_pode_ter_o_perfil_ambos():
    with pytest.raises(DomainRuleViolated) as erro:
        User(id=uuid4(), username="exemplo", profile=ProfileKind.AMBOS, password_hash="hash")
    assert erro.value.code == "invalid_profile"


def test_sessao_guarda_o_hash_do_token_e_nunca_o_token():
    agora = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)
    sessao = UserSession(
        id=uuid4(), user_id=uuid4(), token_hash="a" * 64, created_at=agora, last_seen_at=agora
    )
    assert sessao.token_hash == "a" * 64
    assert not hasattr(sessao, "token")


def test_credencial_invalida_e_um_erro_de_nao_autenticado_com_code_estavel():
    assert issubclass(InvalidCredentials, Unauthenticated)
    assert InvalidCredentials().code == "invalid_credentials"


@pytest.mark.parametrize(
    ("erro", "codigo"),
    [(DuplicateUsername, "duplicate_username"), (ProfileTaken, "profile_taken")],
)
def test_usuario_ou_perfil_repetido_e_conflito(erro, codigo):
    assert issubclass(erro, Conflict)
    assert erro().code == codigo
