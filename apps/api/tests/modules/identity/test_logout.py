from wedding.modules.identity.application.commands.logout import Logout


def _logout(world) -> Logout:
    return Logout(uow_factory=world.uow_factory)


def test_logout_apaga_a_sessao_no_servidor(world):
    usuario = world.add_user()
    sessao = world.add_session(usuario, token="token-a")
    _logout(world).execute("token-a")
    assert sessao.id not in world.store.sessions


def test_logout_nao_mexe_nas_outras_sessoes(world):
    usuario = world.add_user()
    world.add_session(usuario, token="token-a")
    outra = world.add_session(usuario, token="token-b")
    _logout(world).execute("token-a")
    assert list(world.store.sessions) == [outra.id]


def test_logout_com_token_desconhecido_ou_ausente_e_idempotente(world):
    _logout(world).execute("token-que-nao-existe")
    _logout(world).execute(None)
    assert world.store.sessions == {}
