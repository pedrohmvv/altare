import copy
from collections.abc import Iterator
from datetime import datetime
from types import TracebackType
from uuid import UUID

import pytest

from wedding.modules.wedding.application.commands.update_baseline_field import UpdateBaselineField
from wedding.modules.wedding.application.dto import BaselineChangeDto, to_snapshot_dto
from wedding.modules.wedding.application.queries.get_baseline import GetBaseline
from wedding.modules.wedding.application.queries.list_baseline_changes import ListBaselineChanges
from wedding.modules.wedding.application.use_cases import WeddingUseCases
from wedding.modules.wedding.domain.entities import BaselineChange, BaselineField
from wedding.modules.wedding.domain.value_objects import BaselineKey, DefinitionStatus
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.profile import ProfileKind

NOIVO = Actor(user_id=UUID(int=1), profile=ProfileKind.NOIVO)
NOIVA = Actor(user_id=UUID(int=2), profile=ProfileKind.NOIVA)


class _Baseline:
    def __init__(self, world: "World", fields: dict[BaselineKey, BaselineField]) -> None:
        self._world = world
        self.fields = fields
        self.added: list[BaselineChange] = []

    def get(self, key: BaselineKey) -> BaselineField | None:
        return self.fields.get(key)

    def all(self) -> list[BaselineField]:
        return list(self.fields.values())

    def add_change(self, change: BaselineChange) -> None:
        self.added.append(change)

    def changes(self, limit: int) -> list[BaselineChangeDto]:
        stored = [*self._world.changes, *self.added]
        newest_first = list(reversed(stored))[:limit]
        return [
            BaselineChangeDto(
                id=change.id,
                key=change.key,
                before=to_snapshot_dto(change.key, change.before),
                after=to_snapshot_dto(change.key, change.after),
                profile=change.profile,
                changed_at=self._world.stamps[change.id],
            )
            for change in newest_first
        ]


class _UnitOfWork:
    """Transação de mentira: trabalha numa cópia e só a publica no commit, subindo a `version`
    dos campos que mudaram, como o mapeamento faz."""

    def __init__(self, world: "World", actor: Actor) -> None:
        self._world = world
        world.actors.append(actor)
        self._original = world.fields
        self.baseline = _Baseline(world, copy.deepcopy(world.fields))

    def __enter__(self) -> "_UnitOfWork":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None

    def commit(self) -> None:
        for key, field in self.baseline.fields.items():
            if field.snapshot() != self._original[key].snapshot():
                field.version += 1
        self._world.fields = self.baseline.fields
        for change in self.baseline.added:
            self._world.stamps[change.id] = self._world.clock.now()
        self._world.changes.extend(self.baseline.added)
        self.baseline.added = []

    def rollback(self) -> None:
        return None


class _Ids:
    def __init__(self) -> None:
        self._next = 100

    def new_id(self) -> UUID:
        self._next += 1
        return UUID(int=self._next)


class World:
    def __init__(self, clock) -> None:
        self.clock = clock
        self.actors: list[Actor] = []
        self.ids = _Ids()
        self.changes: list[BaselineChange] = []
        self.stamps: dict[UUID, datetime] = {}
        # A semente da migration: seis campos vazios e `Em definição`.
        self.fields = {
            key: BaselineField(
                id=UUID(int=index + 1),
                key=key,
                status=DefinitionStatus.IN_DEFINITION,
                version=1,
            )
            for index, key in enumerate(BaselineKey)
        }

    def uow_factory(self, actor: Actor) -> _UnitOfWork:
        return _UnitOfWork(self, actor)

    def use_cases(self) -> WeddingUseCases:
        return WeddingUseCases(
            get_baseline=GetBaseline(self.uow_factory),
            update_baseline_field=UpdateBaselineField(self.uow_factory, self.ids),
            list_baseline_changes=ListBaselineChanges(self.uow_factory),
        )


@pytest.fixture
def world(clock) -> World:
    return World(clock)


def iterate(items: Iterator[object]) -> list[object]:
    return list(items)


class _FakeHasher:
    def hash(self, password: str) -> str:
        return f"hash::{password}"

    def verify(self, password_hash: str, password: str) -> bool:
        return password_hash == f"hash::{password}"

    def needs_rehash(self, password_hash: str) -> bool:
        return False

    def verify_unknown_user(self, password: str) -> None:
        return None


CSRF = {"X-Altare-CSRF": "1"}
SENHA = "senha-exemplo-12345"


@pytest.fixture
def api(tmp_path):
    """O app inteiro contra um banco migrado de verdade (a semente vem da migration), com o casal
    de exemplo criado e logado."""
    from pathlib import Path
    from types import SimpleNamespace

    from alembic import command
    from alembic.config import Config
    from fastapi.testclient import TestClient

    from wedding.modules.identity.application.commands.create_user import CreateUserCommand
    from wedding.platform.bootstrap.app import build_app
    from wedding.platform.config import Settings

    url = f"sqlite:///{tmp_path / 'api.db'}"
    config = Config(str(Path(__file__).parents[3] / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", url)
    command.upgrade(config, "head")
    settings = Settings(
        database_url=url, files_dir=str(tmp_path / "arquivos"), session_cookie_secure=True
    )
    app = build_app(settings, hasher=_FakeHasher())
    identity = app.state.identity.use_cases()
    identity.create_user.execute(CreateUserCommand("exemplo.noivo", ProfileKind.NOIVO, SENHA))
    identity.create_user.execute(CreateUserCommand("exemplo.noiva", ProfileKind.NOIVA, SENHA))

    def entrar(usuario: str) -> TestClient:
        client = TestClient(app, base_url="https://testserver", headers=CSRF)
        resposta = client.post("/api/v1/auth/login", json={"username": usuario, "password": SENHA})
        assert resposta.status_code == 200
        return client

    return SimpleNamespace(
        app=app,
        noivo=entrar("exemplo.noivo"),
        noiva=entrar("exemplo.noiva"),
        anonimo=TestClient(app, base_url="https://testserver", headers=CSRF),
        sem_csrf=TestClient(app, base_url="https://testserver"),
    )
