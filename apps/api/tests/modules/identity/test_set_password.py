import pytest

from wedding.modules.identity.application.commands.set_password import (
    SetPassword,
    SetPasswordCommand,
)
from wedding.modules.identity.domain.errors import WeakPassword
from wedding.shared_kernel.errors import NotFound
from wedding.shared_kernel.profile import ProfileKind

NOVA = "outra-senha-exemplo-98765"


def _trocar(world, username="exemplo.noivo", password=NOVA):
    caso = SetPassword(uow_factory=world.uow_factory, hasher=world.hasher)
    caso.execute(SetPasswordCommand(username=username, password=password))


def test_troca_a_senha_guardando_so_o_hash(world):
    usuario = world.add_user()
    _trocar(world)
    assert world.store.users[usuario.id].password_hash == world.hasher.hash(NOVA)


def test_derruba_as_sessoes_do_usuario_e_so_as_dele(world):
    noivo = world.add_user()
    noiva = world.add_user("exemplo.noiva", ProfileKind.NOIVA)
    world.add_session(noivo, token="a")
    world.add_session(noivo, token="b")
    da_noiva = world.add_session(noiva, token="c")
    _trocar(world)
    assert list(world.store.sessions) == [da_noiva.id]


def test_usuario_e_normalizado_antes_de_procurar(world):
    usuario = world.add_user()
    _trocar(world, username=" Exemplo.Noivo ")
    assert world.store.users[usuario.id].password_hash == world.hasher.hash(NOVA)


def test_senha_fraca_nao_muda_nada(world):
    usuario = world.add_user()
    antigo = usuario.password_hash
    with pytest.raises(WeakPassword):
        _trocar(world, password="curta")
    assert world.store.users[usuario.id].password_hash == antigo


def test_usuario_inexistente_e_nao_encontrado(world):
    with pytest.raises(NotFound):
        _trocar(world, username="ninguem")
