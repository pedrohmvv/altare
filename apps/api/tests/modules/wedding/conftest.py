import copy
from collections.abc import Iterator
from datetime import datetime
from types import TracebackType
from uuid import UUID

import pytest

from wedding.modules.wedding.application.commands.change_scope_status import ChangeScopeStatus
from wedding.modules.wedding.application.commands.create_scope_category import CreateScopeCategory
from wedding.modules.wedding.application.commands.create_scope_group import CreateScopeGroup
from wedding.modules.wedding.application.commands.delete_scope_category import DeleteScopeCategory
from wedding.modules.wedding.application.commands.delete_scope_group import DeleteScopeGroup
from wedding.modules.wedding.application.commands.rename_scope_group import RenameScopeGroup
from wedding.modules.wedding.application.commands.set_my_evaluation import SetMyEvaluation
from wedding.modules.wedding.application.commands.set_scope_category_visibility import (
    SetScopeCategoryVisibility,
)
from wedding.modules.wedding.application.commands.set_scope_group_visibility import (
    SetScopeGroupVisibility,
)
from wedding.modules.wedding.application.commands.update_baseline_field import UpdateBaselineField
from wedding.modules.wedding.application.commands.update_scope_category import UpdateScopeCategory
from wedding.modules.wedding.application.dto import BaselineChangeDto, to_snapshot_dto
from wedding.modules.wedding.application.queries.get_baseline import GetBaseline
from wedding.modules.wedding.application.queries.get_scope_map import GetScopeMap
from wedding.modules.wedding.application.queries.list_baseline_changes import ListBaselineChanges
from wedding.modules.wedding.application.queries.list_scope_category_history import (
    ListScopeCategoryHistory,
)
from wedding.modules.wedding.application.scope_dto import StatusChangeDto
from wedding.modules.wedding.application.scope_use_cases import ScopeUseCases
from wedding.modules.wedding.application.use_cases import WeddingUseCases
from wedding.modules.wedding.domain.entities import BaselineChange, BaselineField
from wedding.modules.wedding.domain.scope_entities import (
    ScopeCategory,
    ScopeEvaluation,
    ScopeGroup,
    ScopeStatusChange,
)
from wedding.modules.wedding.domain.scope_values import Origin, ScopeStatus
from wedding.modules.wedding.domain.value_objects import BaselineKey, DefinitionStatus
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.clock import Clock
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


class _Scope:
    """O Mapa de Escopo em memória, com as mesmas regras de leitura do SQL: exclusão lógica
    filtrada, ocultas presentes, nome único entre os vivos."""

    def __init__(self, world: "World", store: "ScopeStore") -> None:
        self._world = world
        self.store = store
        self.new_changes: list[ScopeStatusChange] = []

    def get_group(self, group_id: UUID) -> ScopeGroup | None:
        group = self.store.groups.get(group_id)
        return group if group and group.deleted_at is None else None

    def list_groups(self) -> list[ScopeGroup]:
        return [g for g in self.store.groups.values() if g.deleted_at is None]

    def add_group(self, group: ScopeGroup) -> None:
        self.store.groups[group.id] = group

    def next_group_position(self) -> int:
        return max((g.position for g in self.list_groups()), default=-1) + 1

    def group_name_taken(self, key: str, *, excluding: UUID | None = None) -> bool:
        return any(g.name_key == key and g.id != excluding for g in self.list_groups())

    def count_categories(self, group_id: UUID) -> int:
        return sum(c.group_id == group_id for c in self.list_categories())

    def get_category(self, category_id: UUID) -> ScopeCategory | None:
        category = self.store.categories.get(category_id)
        return category if category and category.deleted_at is None else None

    def list_categories(self) -> list[ScopeCategory]:
        return [c for c in self.store.categories.values() if c.deleted_at is None]

    def add_category(self, category: ScopeCategory) -> None:
        self.store.categories[category.id] = category

    def next_category_position(self, group_id: UUID) -> int:
        positions = [c.position for c in self.list_categories() if c.group_id == group_id]
        return max(positions, default=-1) + 1

    def category_name_taken(self, key: str, *, excluding: UUID | None = None) -> bool:
        return any(c.name_key == key and c.id != excluding for c in self.list_categories())

    def get_evaluation(self, category_id: UUID, profile: ProfileKind) -> ScopeEvaluation | None:
        return self.store.evaluations.get((category_id, profile))

    def list_evaluations(self) -> list[ScopeEvaluation]:
        live = {c.id for c in self.list_categories()}
        return [e for e in self.store.evaluations.values() if e.category_id in live]

    def add_evaluation(self, evaluation: ScopeEvaluation) -> None:
        self.store.evaluations[(evaluation.category_id, evaluation.profile)] = evaluation

    def add_status_change(self, change: ScopeStatusChange) -> None:
        self.new_changes.append(change)

    def _all_changes(self) -> list[ScopeStatusChange]:
        return [*self._world.status_changes, *self.new_changes]

    def status_history(self, category_id: UUID) -> list[StatusChangeDto]:
        rows = [c for c in self._all_changes() if c.category_id == category_id]
        return [
            StatusChangeDto(
                id=c.id,
                from_status=c.from_status,
                to_status=c.to_status,
                reason=c.reason,
                profile=c.profile,
                changed_at=self._world.stamps.get(c.id, self._world.clock.now()),
            )
            for c in reversed(rows)
        ]

    def discard_reasons(self) -> dict[UUID, str | None]:
        reasons: dict[UUID, str | None] = {}
        for change in self._all_changes():
            if change.to_status is ScopeStatus.OUT:
                reasons[change.category_id] = change.reason
        return reasons


class ScopeStore:
    def __init__(self) -> None:
        self.groups: dict[UUID, ScopeGroup] = {}
        self.categories: dict[UUID, ScopeCategory] = {}
        self.evaluations: dict[tuple[UUID, ProfileKind], ScopeEvaluation] = {}

    def snapshot(self) -> dict[object, object]:
        return {
            **{("g", k): copy.deepcopy(v) for k, v in self.groups.items()},
            **{("c", k): copy.deepcopy(v) for k, v in self.categories.items()},
            **{("e", k): copy.deepcopy(v) for k, v in self.evaluations.items()},
        }

    def bump_versions(self, before: dict[object, object]) -> None:
        """Como o mapeamento: novo começa em 1; mudado sobe um; igual fica."""
        for kind, items in (("g", self.groups), ("c", self.categories), ("e", self.evaluations)):
            for key, item in items.items():
                original = before.get((kind, key))
                if original is None:
                    item.version = 1
                elif item != original:
                    item.version = original.version + 1  # type: ignore[attr-defined]


class _UnitOfWork:
    """Transação de mentira: trabalha numa cópia e só a publica no commit, subindo a `version`
    dos campos que mudaram, como o mapeamento faz."""

    def __init__(self, world: "World", actor: Actor) -> None:
        self._world = world
        world.actors.append(actor)
        self._original = world.fields
        self.baseline = _Baseline(world, copy.deepcopy(world.fields))
        self._scope_before = world.scope_store.snapshot()
        self._scope_store = copy.deepcopy(world.scope_store)
        self.scope = _Scope(world, self._scope_store)

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
        self._scope_store.bump_versions(self._scope_before)
        self._world.scope_store = self._scope_store
        for change in self.scope.new_changes:
            self._world.stamps[change.id] = self._world.clock.now()
        self._world.status_changes.extend(self.scope.new_changes)
        self.scope.new_changes = []
        self._scope_before = self._scope_store.snapshot()

    def rollback(self) -> None:
        return None


class _Ids:
    def __init__(self) -> None:
        self._next = 100

    def new_id(self) -> UUID:
        self._next += 1
        return UUID(int=self._next)


class World:
    def __init__(self, clock: Clock) -> None:
        self.clock = clock
        self.actors: list[Actor] = []
        self.ids = _Ids()
        self.changes: list[BaselineChange] = []
        self.stamps: dict[UUID, datetime] = {}
        self.scope_store = ScopeStore()
        self.status_changes: list[ScopeStatusChange] = []
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

    def scope_use_cases(self) -> ScopeUseCases:
        return ScopeUseCases(
            get_scope_map=GetScopeMap(self.uow_factory),
            list_scope_category_history=ListScopeCategoryHistory(self.uow_factory),
            create_scope_group=CreateScopeGroup(self.uow_factory, self.ids),
            rename_scope_group=RenameScopeGroup(self.uow_factory),
            set_scope_group_visibility=SetScopeGroupVisibility(self.uow_factory, self.clock),
            delete_scope_group=DeleteScopeGroup(self.uow_factory, self.clock),
            create_scope_category=CreateScopeCategory(self.uow_factory, self.ids),
            update_scope_category=UpdateScopeCategory(self.uow_factory),
            set_scope_category_visibility=SetScopeCategoryVisibility(self.uow_factory, self.clock),
            delete_scope_category=DeleteScopeCategory(self.uow_factory, self.clock),
            change_scope_status=ChangeScopeStatus(self.uow_factory, self.ids),
            set_my_evaluation=SetMyEvaluation(self.uow_factory),
        )

    def seed_catalog(self) -> tuple[UUID, UUID]:
        """Um grupo e uma categoria do catálogo, como a migration os deixa (com as avaliações)."""
        group = ScopeGroup(id=UUID(int=9001), name="Cerimônia", position=0, origin=Origin.CATALOG)
        category = ScopeCategory(
            id=UUID(int=9002),
            group_id=group.id,
            name="Cerimônia civil",
            position=0,
            origin=Origin.CATALOG,
        )
        group.version = category.version = 1
        self.scope_store.groups[group.id] = group
        self.scope_store.categories[category.id] = category
        for index, profile in enumerate((ProfileKind.NOIVO, ProfileKind.NOIVA)):
            evaluation = ScopeEvaluation(UUID(int=9100 + index), category.id, profile)
            evaluation.version = 1
            self.scope_store.evaluations[(category.id, profile)] = evaluation
        return group.id, category.id


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
