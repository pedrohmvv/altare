from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest
from sqlalchemy import insert, inspect, select, update
from sqlalchemy.exc import IntegrityError

from wedding.modules.identity.application.commands.create_user import CreateUser, CreateUserCommand
from wedding.modules.identity.application.commands.login import Login, LoginCommand
from wedding.modules.identity.application.queries.resolve_session import ResolveSession
from wedding.modules.identity.domain.entities import User, UserSession
from wedding.modules.identity.infrastructure.login_attempts import InMemoryLoginAttempts
from wedding.modules.identity.infrastructure.mapping import start_mappers
from wedding.modules.identity.infrastructure.tables import users
from wedding.modules.identity.infrastructure.uow import SqlIdentityUnitOfWork
from wedding.platform.db.engine import create_db_engine, create_session_factory
from wedding.platform.db.metadata import metadata
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.errors import VersionConflict
from wedding.shared_kernel.ids import UuidGenerator
from wedding.shared_kernel.profile import ProfileKind

AGORA = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)


@pytest.fixture
def banco(tmp_path, clock):
    start_mappers()
    engine = create_db_engine(f"sqlite:///{tmp_path / 'identidade.db'}")
    metadata.create_all(engine)
    factory = create_session_factory(engine)
    yield SimpleNamespace(
        engine=engine,
        clock=clock,
        uow=lambda ator=None: SqlIdentityUnitOfWork(factory, clock, ator),
    )
    engine.dispose()


def _usuario(username="exemplo.noivo", profile=ProfileKind.NOIVO) -> User:
    return User(id=uuid4(), username=username, profile=profile, password_hash="hash-exemplo")


def _gravar(banco, *entidades) -> None:
    with banco.uow() as uow:
        for entidade in entidades:
            uow.session.add(entidade)
        uow.commit()


def test_usuario_gravado_volta_pelo_id_pelo_nome_e_pelo_perfil(banco):
    usuario = _usuario()
    _gravar(banco, usuario)
    with banco.uow() as uow:
        assert uow.users.get(usuario.id).username == "exemplo.noivo"
        assert uow.users.get_by_username("exemplo.noivo").id == usuario.id
        achado = uow.users.get_by_profile(ProfileKind.NOIVO)
        assert achado.profile is ProfileKind.NOIVO
        assert uow.users.get_by_profile(ProfileKind.NOIVA) is None
        assert uow.users.get_by_username("outro") is None


def test_usuario_recebe_o_historico_basico(banco):
    usuario = _usuario()
    _gravar(banco, usuario)
    with banco.engine.connect() as conn:
        linha = conn.execute(select(users)).one()
    assert (linha.created_at, linha.updated_at) == (AGORA, AGORA)
    assert (linha.created_by, linha.deleted_at, linha.version) == (None, None, 1)


def test_o_banco_barra_usuario_repetido(banco):
    _gravar(banco, _usuario("exemplo.noivo", ProfileKind.NOIVO))
    with pytest.raises(IntegrityError):
        _gravar(banco, _usuario("exemplo.noivo", ProfileKind.NOIVA))


def test_o_banco_barra_dois_usuarios_com_o_mesmo_perfil(banco):
    _gravar(banco, _usuario("exemplo.noivo", ProfileKind.NOIVO))
    with pytest.raises(IntegrityError):
        _gravar(banco, _usuario("outro.noivo", ProfileKind.NOIVO))


def test_o_banco_barra_o_perfil_ambos(banco):
    with pytest.raises(IntegrityError), banco.engine.begin() as conn:
        conn.execute(
            insert(users).values(
                id=uuid4(),
                created_at=AGORA,
                updated_at=AGORA,
                username="exemplo.ambos",
                profile="Ambos",
                password_hash="hash-exemplo",
                version=1,
            )
        )


def test_usuario_excluido_some_das_consultas_e_libera_o_nome_e_o_perfil(banco):
    antigo = _usuario("exemplo.noivo", ProfileKind.NOIVO)
    _gravar(banco, antigo)
    with banco.engine.begin() as conn:
        conn.execute(update(users).values(deleted_at=AGORA, deleted_by=None))
    with banco.uow() as uow:
        assert uow.users.get(antigo.id) is None
        assert uow.users.get_by_username("exemplo.noivo") is None
        assert uow.users.get_by_profile(ProfileKind.NOIVO) is None
    _gravar(banco, _usuario("exemplo.noivo", ProfileKind.NOIVO))


def test_regravar_a_senha_pelo_proprio_usuario_registra_quem_alterou(banco):
    usuario = _usuario()
    _gravar(banco, usuario)
    banco.clock.advance(hours=1)
    ator = Actor(user_id=usuario.id, profile=usuario.profile)
    with banco.uow() as uow:
        uow.act_as(ator)
        uow.users.get(usuario.id).password_hash = "hash-novo"
        uow.commit()
    with banco.engine.connect() as conn:
        linha = conn.execute(select(users)).one()
    assert (linha.updated_by, linha.version) == (usuario.id, 2)
    assert linha.updated_at == AGORA + timedelta(hours=1)


def test_duas_alteracoes_do_mesmo_usuario_dao_conflito_de_versao(banco):
    usuario = _usuario()
    _gravar(banco, usuario)
    primeira, segunda = banco.uow(), banco.uow()
    with primeira, segunda:
        primeira.users.get(usuario.id).password_hash = "hash-a"
        segunda.users.get(usuario.id).password_hash = "hash-b"
        primeira.commit()
        with pytest.raises(VersionConflict):
            segunda.commit()


def _sessao(usuario: User, token_hash="h" * 64) -> UserSession:
    return UserSession(
        id=uuid4(),
        user_id=usuario.id,
        token_hash=token_hash,
        created_at=AGORA,
        last_seen_at=AGORA,
    )


def test_sessao_volta_pelo_hash_do_token_com_instantes_em_utc(banco):
    usuario = _usuario()
    sessao = _sessao(usuario)
    _gravar(banco, usuario, sessao)
    with banco.uow() as uow:
        achada = uow.sessions.get_by_token_hash("h" * 64)
        assert achada.id == sessao.id
        assert achada.created_at == AGORA
        assert achada.last_seen_at.tzinfo is UTC
        assert uow.sessions.get_by_token_hash("x" * 64) is None


def test_listar_e_apagar_sessoes(banco):
    usuario = _usuario()
    a, b = _sessao(usuario, "a" * 64), _sessao(usuario, "b" * 64)
    _gravar(banco, usuario, a, b)
    with banco.uow() as uow:
        assert {s.id for s in uow.sessions.list_all()} == {a.id, b.id}
        uow.sessions.delete(uow.sessions.get_by_token_hash("a" * 64))
        uow.commit()
    with banco.uow() as uow:
        assert [s.id for s in uow.sessions.list_all()] == [b.id]


def test_apagar_as_sessoes_de_um_usuario_preserva_as_do_outro(banco):
    noivo, noiva = _usuario(), _usuario("exemplo.noiva", ProfileKind.NOIVA)
    _gravar(banco, noivo, noiva, _sessao(noivo, "a" * 64), _sessao(noiva, "b" * 64))
    with banco.uow() as uow:
        uow.sessions.delete_for_user(noivo.id)
        uow.commit()
    with banco.uow() as uow:
        assert [s.user_id for s in uow.sessions.list_all()] == [noiva.id]


def test_o_banco_barra_sessao_de_usuario_inexistente(banco):
    orfa = _sessao(_usuario())
    with pytest.raises(IntegrityError):
        _gravar(banco, orfa)


def test_o_banco_barra_dois_hashes_de_token_iguais(banco):
    usuario = _usuario()
    with pytest.raises(IntegrityError):
        _gravar(banco, usuario, _sessao(usuario), _sessao(usuario))


def test_unicidade_e_indices_seguem_a_convencao_de_nomes(banco):
    inspetor = inspect(banco.engine)
    unicas = {u["name"] for u in inspetor.get_unique_constraints("user_sessions")}
    indices = {i["name"] for t in ("users", "user_sessions") for i in inspetor.get_indexes(t)}
    assert unicas == {"uq_user_sessions_token_hash"}
    assert {
        "uq_users_username_live",
        "uq_users_profile_live",
        "ix_user_sessions_user_id",
    } <= indices


def test_fluxo_completo_contra_o_banco_criar_entrar_e_resolver_a_sessao(banco):
    class Hasher:
        def hash(self, password: str) -> str:
            return f"hash::{password}"

        def verify(self, password_hash: str, password: str) -> bool:
            return password_hash == f"hash::{password}"

        def needs_rehash(self, password_hash: str) -> bool:
            return False

        def verify_unknown_user(self, password: str) -> None:
            return None

    hasher, ids = Hasher(), UuidGenerator()
    CreateUser(uow_factory=banco.uow, hasher=hasher, ids=ids).execute(
        CreateUserCommand("Exemplo.Noiva", ProfileKind.NOIVA, "senha-exemplo-12345")
    )
    entrou = Login(
        uow_factory=banco.uow,
        hasher=hasher,
        attempts=InMemoryLoginAttempts(),
        clock=banco.clock,
        ids=ids,
    ).execute(LoginCommand("exemplo.noiva", "senha-exemplo-12345", "203.0.113.7", None))
    ator = ResolveSession(uow_factory=banco.uow, clock=banco.clock).execute(entrou.token)
    assert ator is not None
    assert (ator.user_id, ator.profile) == (entrou.user.user_id, ProfileKind.NOIVA)
