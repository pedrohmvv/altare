import pytest

from wedding.modules.identity.application.commands.create_user import CreateUser, CreateUserCommand
from wedding.modules.identity.domain.errors import (
    DuplicateUsername,
    InvalidUsername,
    ProfileTaken,
    WeakPassword,
)
from wedding.shared_kernel.errors import DomainRuleViolated
from wedding.shared_kernel.profile import ProfileKind


def _criar(world, username="Exemplo.Noivo", profile=ProfileKind.NOIVO, password=None):
    caso = CreateUser(uow_factory=world.uow_factory, hasher=world.hasher, ids=world.ids)
    senha = password if password is not None else world.password
    return caso.execute(CreateUserCommand(username=username, profile=profile, password=senha))


def test_cria_o_usuario_com_nome_normalizado_e_senha_em_hash(world):
    criado = _criar(world)
    (usuario,) = world.store.users.values()
    assert criado.user_id == usuario.id
    assert usuario.username == "exemplo.noivo"
    assert usuario.password_hash == world.hasher.hash(world.password)
    assert usuario.password_hash != world.password


def test_a_criacao_pela_cli_nao_tem_ator(world):
    _criar(world)
    assert world.store.actors == []


def test_recusa_usuario_repetido_sem_diferenciar_maiusculas(world):
    world.add_user("exemplo.noivo", ProfileKind.NOIVO)
    with pytest.raises(DuplicateUsername):
        _criar(world, username="EXEMPLO.NOIVO", profile=ProfileKind.NOIVA)


def test_recusa_um_segundo_usuario_com_o_mesmo_perfil(world):
    world.add_user("exemplo.noivo", ProfileKind.NOIVO)
    with pytest.raises(ProfileTaken):
        _criar(world, username="outro.usuario", profile=ProfileKind.NOIVO)


def test_recusa_senha_fraca_sem_criar_nada(world):
    with pytest.raises(WeakPassword):
        _criar(world, password="curta")
    assert world.store.users == {}


def test_recusa_usuario_com_formato_invalido(world):
    with pytest.raises(InvalidUsername):
        _criar(world, username="com espaço")


def test_recusa_o_perfil_ambos(world):
    with pytest.raises(DomainRuleViolated) as erro:
        _criar(world, profile=ProfileKind.AMBOS)
    assert erro.value.code == "invalid_profile"
    assert world.store.users == {}
