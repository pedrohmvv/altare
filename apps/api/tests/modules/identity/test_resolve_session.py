from datetime import timedelta

import pytest

from wedding.modules.identity.application.queries.current_user import GetCurrentUser
from wedding.modules.identity.application.queries.resolve_session import ResolveSession
from wedding.shared_kernel.errors import NotFound
from wedding.shared_kernel.profile import ProfileKind


def _resolver(world) -> ResolveSession:
    return ResolveSession(uow_factory=world.uow_factory, clock=world.clock)


def test_token_valido_vira_o_ator_da_sessao(world):
    usuario = world.add_user("exemplo.noiva", ProfileKind.NOIVA)
    world.add_session(usuario, token="token-a")
    ator = _resolver(world).execute("token-a")
    assert ator is not None
    assert (ator.user_id, ator.profile) == (usuario.id, ProfileKind.NOIVA)


def test_token_desconhecido_nao_e_ninguem(world):
    world.add_user()
    assert _resolver(world).execute("token-que-nao-existe") is None


def test_sessao_vencida_nao_e_ninguem_e_e_apagada(world):
    usuario = world.add_user()
    sessao = world.add_session(usuario, token="token-a", seen_ago=timedelta(days=30))
    assert _resolver(world).execute("token-a") is None
    assert sessao.id not in world.store.sessions


def test_sessao_de_usuario_que_nao_existe_mais_e_apagada(world):
    usuario = world.add_user()
    sessao = world.add_session(usuario, token="token-a")
    del world.store.users[usuario.id]
    assert _resolver(world).execute("token-a") is None
    assert sessao.id not in world.store.sessions


def test_uso_com_mais_de_uma_hora_renova_o_ultimo_acesso(world):
    usuario = world.add_user()
    sessao = world.add_session(usuario, token="token-a", seen_ago=timedelta(hours=2))
    _resolver(world).execute("token-a")
    assert world.store.sessions[sessao.id].last_seen_at == world.clock.now()


def test_uso_dentro_da_hora_nao_grava_nada(world):
    usuario = world.add_user()
    sessao = world.add_session(usuario, token="token-a", seen_ago=timedelta(minutes=10))
    visto = sessao.last_seen_at
    _resolver(world).execute("token-a")
    assert world.store.sessions[sessao.id].last_seen_at == visto
    assert world.store.commits == 0


def test_usuario_atual_vem_pelo_id(world):
    usuario = world.add_user("exemplo.noiva", ProfileKind.NOIVA)
    atual = GetCurrentUser(uow_factory=world.uow_factory).execute(usuario.id)
    assert (atual.user_id, atual.username, atual.profile) == (
        usuario.id,
        "exemplo.noiva",
        ProfileKind.NOIVA,
    )


def test_usuario_atual_inexistente_nao_e_encontrado(world):
    with pytest.raises(NotFound):
        GetCurrentUser(uow_factory=world.uow_factory).execute(world.ids.new_id())
