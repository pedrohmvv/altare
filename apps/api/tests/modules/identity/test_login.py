from datetime import timedelta

import pytest

from wedding.modules.identity.application.commands.login import Login, LoginCommand
from wedding.modules.identity.domain.errors import InvalidCredentials
from wedding.modules.identity.domain.value_objects import hash_token
from wedding.shared_kernel.errors import TooManyAttempts
from wedding.shared_kernel.profile import ProfileKind

IP = "203.0.113.7"


def _login(world) -> Login:
    return Login(
        uow_factory=world.uow_factory,
        hasher=world.hasher,
        attempts=world.attempts,
        clock=world.clock,
        ids=world.ids,
    )


def _entrar(world, username="exemplo.noivo", password=None, ip=IP, previous_token=None):
    comando = LoginCommand(
        username=username,
        password=password if password is not None else world.password,
        ip=ip,
        previous_token=previous_token,
    )
    return _login(world).execute(comando)


def _errar(world, vezes: int, **kwargs) -> None:
    for _ in range(vezes):
        with pytest.raises(InvalidCredentials):
            _entrar(world, password="senha-errada-123", **kwargs)


def test_login_correto_cria_a_sessao_e_devolve_o_usuario(world):
    usuario = world.add_user()
    resultado = _entrar(world)
    assert resultado.user.user_id == usuario.id
    assert resultado.user.profile is ProfileKind.NOIVO
    assert len(world.store.sessions) == 1


def test_o_banco_guarda_so_o_hash_do_token_e_nunca_o_token(world):
    world.add_user()
    resultado = _entrar(world)
    (sessao,) = world.store.sessions.values()
    assert sessao.token_hash == hash_token(resultado.token)
    assert resultado.token not in repr(sessao)


def test_cada_login_gera_um_token_novo(world):
    world.add_user()
    assert _entrar(world).token != _entrar(world).token


def test_usuario_e_normalizado_antes_de_procurar(world):
    world.add_user()
    assert _entrar(world, username="  Exemplo.Noivo ").user.username == "exemplo.noivo"


def test_senha_errada_nao_cria_sessao_e_registra_a_falha(world):
    world.add_user()
    with pytest.raises(InvalidCredentials):
        _entrar(world, password="senha-errada-123")
    assert world.store.sessions == {}
    assert len(world.attempts.data[f"exemplo.noivo|{IP}"]) == 1


def test_usuario_inexistente_da_o_mesmo_erro_e_gasta_o_mesmo_trabalho(world):
    world.add_user()
    with pytest.raises(InvalidCredentials) as senha_errada:
        _entrar(world, password="senha-errada-123")
    with pytest.raises(InvalidCredentials) as sem_conta:
        _entrar(world, username="ninguem")
    assert type(senha_errada.value) is type(sem_conta.value)
    assert str(senha_errada.value) == str(sem_conta.value)
    assert world.hasher.unknown_user_calls == 1
    assert len(world.attempts.data["ninguem|" + IP]) == 1


def test_cinco_falhas_bloqueiam_a_sexta_tentativa_sem_verificar_a_senha(world):
    world.add_user()
    _errar(world, 5)
    verificacoes = world.hasher.verify_calls
    with pytest.raises(TooManyAttempts) as erro:
        _entrar(world, password="senha-errada-123")
    assert erro.value.retry_after == 15 * 60
    assert world.hasher.verify_calls == verificacoes


def test_durante_o_bloqueio_ate_a_senha_certa_e_recusada(world):
    world.add_user()
    _errar(world, 5)
    with pytest.raises(TooManyAttempts):
        _entrar(world)
    assert world.store.sessions == {}


def test_depois_da_janela_o_login_volta_a_funcionar(world):
    world.add_user()
    _errar(world, 5)
    world.clock.advance(minutes=15)
    assert _entrar(world).token


def test_o_sucesso_zera_a_contagem_de_falhas(world):
    world.add_user()
    _errar(world, 4)
    _entrar(world)
    _errar(world, 4)
    assert _entrar(world).token


def test_o_bloqueio_e_por_usuario_e_por_ip(world):
    world.add_user()
    world.add_user("exemplo.noiva", ProfileKind.NOIVA)
    _errar(world, 5)
    assert _entrar(world, ip="198.51.100.9").token
    assert _entrar(world, username="exemplo.noiva").user.profile is ProfileKind.NOIVA


def test_senha_com_parametros_antigos_e_regravada_no_login_pelo_proprio_usuario(world):
    usuario = world.add_user()
    antigo = usuario.password_hash
    world.hasher.stale.add(antigo)
    _entrar(world)
    assert world.store.users[usuario.id].password_hash == antigo
    (ator,) = world.store.actors
    assert (ator.user_id, ator.profile) == (usuario.id, usuario.profile)


def test_senha_em_dia_nao_e_regravada(world):
    world.add_user()
    _entrar(world)
    assert world.store.actors == []


def test_o_login_apaga_a_sessao_do_cookie_anterior(world):
    usuario = world.add_user()
    anterior = world.add_session(usuario, token="token-anterior")
    resultado = _entrar(world, previous_token="token-anterior")
    assert anterior.id not in world.store.sessions
    assert len(world.store.sessions) == 1
    assert resultado.token != "token-anterior"


def test_o_login_apaga_as_sessoes_vencidas_de_qualquer_usuario(world):
    usuario = world.add_user()
    outra = world.add_user("exemplo.noiva", ProfileKind.NOIVA)
    vencida = world.add_session(outra, token="vencida", seen_ago=timedelta(days=31))
    valida = world.add_session(outra, token="valida", seen_ago=timedelta(days=1))
    _entrar(world)
    assert vencida.id not in world.store.sessions
    assert valida.id in world.store.sessions
    assert usuario.id in {s.user_id for s in world.store.sessions.values()}
