import copy
from types import TracebackType
from uuid import UUID

import pytest
from tests.modules.schedule.catalog import (
    MARCOS,
    categoria_id,
    fase_id,
    marco_id,
)
from tests.modules.wedding.conftest import CSRF, SENHA, _FakeHasher

from wedding.modules.schedule.application.commands.change_milestone_state import (
    ChangeMilestoneState,
)
from wedding.modules.schedule.application.commands.update_milestone import UpdateMilestone
from wedding.modules.schedule.application.ports import CategoryInfo, WeddingDate
from wedding.modules.schedule.application.queries.read_schedule import ReadSchedule
from wedding.modules.schedule.application.schedule_map import ScheduleReader
from wedding.modules.schedule.application.use_cases import ScheduleUseCases
from wedding.modules.schedule.domain.entities import (
    Dependency,
    Milestone,
    MilestoneChange,
    Phase,
)
from wedding.modules.schedule.domain.values import Standing
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.clock import Clock
from wedding.shared_kernel.profile import ProfileKind

NOIVO = Actor(user_id=UUID(int=1), profile=ProfileKind.NOIVO)
NOIVA = Actor(user_id=UUID(int=2), profile=ProfileKind.NOIVA)
FASES_DO_CATALOGO = [
    "Marco Zero",
    "Contrato Âncora",
    "Fornecedores Essenciais",
    "Identidade, Complementares e Convidados",
    "Reta Final",
]


class Store:
    def __init__(self) -> None:
        self.phases: dict[UUID, Phase] = {}
        self.milestones: dict[UUID, Milestone] = {}
        self.dependencies: list[Dependency] = []
        self.changes: list[MilestoneChange] = []


class _Repository:
    """O cronograma em memória, com as mesmas regras de leitura do SQL."""

    def __init__(self, store: Store) -> None:
        self.store = store

    def list_phases(self) -> list[Phase]:
        return list(self.store.phases.values())

    def list_milestones(self) -> list[Milestone]:
        return list(self.store.milestones.values())

    def get_milestone(self, milestone_id: UUID) -> Milestone | None:
        return self.store.milestones.get(milestone_id)

    def dependencies(self) -> list[Dependency]:
        return list(self.store.dependencies)

    def add_change(self, change: MilestoneChange) -> None:
        self.store.changes.append(change)


class _UnitOfWork:
    """Transação de mentira: trabalha numa cópia e só a publica no commit, subindo a `version`
    dos marcos que mudaram, como o mapeamento faz."""

    def __init__(self, world: "World", actor: Actor) -> None:
        self._world = world
        world.actors.append(actor)
        self._store = copy.deepcopy(world.store)
        self._before = copy.deepcopy(world.store.milestones)
        self.schedule = _Repository(self._store)

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
        for key, milestone in self._store.milestones.items():
            if milestone != self._before[key]:
                milestone.version = self._before[key].version + 1
        self._world.store = self._store
        self._before = copy.deepcopy(self._store.milestones)

    def rollback(self) -> None:
        return None


class _Categories:
    def __init__(self, world: "World") -> None:
        self._world = world

    def categories(self, actor: Actor) -> dict[UUID, CategoryInfo]:
        return dict(self._world.categories)


class _WeddingDate:
    def __init__(self, world: "World") -> None:
        self._world = world

    def wedding_date(self, actor: Actor) -> WeddingDate:
        return self._world.wedding_date


class _Ids:
    def __init__(self) -> None:
        self._next = 1000

    def new_id(self) -> UUID:
        self._next += 1
        return UUID(int=self._next)


class World:
    """O catálogo inicial inteiro (29 marcos, 5 fases, as dependências) e o Mapa de Escopo com
    todas as categorias ligadas `Em discussão`, como no casamento recém-criado."""

    def __init__(self, clock: Clock) -> None:
        self.clock = clock
        self.actors: list[Actor] = []
        self.ids = _Ids()
        self.store = Store()
        self.wedding_date = WeddingDate(defined=False, exact=None)
        self.categories: dict[UUID, CategoryInfo] = {}
        self._seed()

    def _seed(self) -> None:
        for numero, titulo in enumerate(FASES_DO_CATALOGO, start=1):
            self.store.phases[fase_id(numero)] = Phase(fase_id(numero), titulo, numero - 1, 1)
        posicao: dict[int, int] = {}
        for codigo, fase, titulo, categoria, dependencias, _janela in MARCOS:
            ordem = posicao.get(fase, 0)
            posicao[fase] = ordem + 1
            self.store.milestones[marco_id(codigo)] = Milestone(
                id=marco_id(codigo),
                phase_id=fase_id(fase + 1),
                title=titulo,
                position=ordem,
                category_id=categoria_id(categoria) if categoria else None,
                version=1,
            )
            if categoria:
                self.categories[categoria_id(categoria)] = CategoryInfo(
                    categoria, Standing.IN_DISCUSSION
                )
            self.store.dependencies.extend(
                Dependency(marco_id(codigo), marco_id(dep)) for dep in dependencias
            )

    def classify(self, nome: str, standing: Standing) -> None:
        self.categories[categoria_id(nome)] = CategoryInfo(nome, standing)

    def classify_all(self, standing: Standing = Standing.ENTERS) -> None:
        for nome in [info.name for info in self.categories.values()]:
            self.classify(nome, standing)

    def uow_factory(self, actor: Actor) -> _UnitOfWork:
        return _UnitOfWork(self, actor)

    def use_cases(self) -> ScheduleUseCases:
        reader = ScheduleReader(_Categories(self), _WeddingDate(self), self.clock)
        return ScheduleUseCases(
            read_schedule=ReadSchedule(self.uow_factory, reader),
            update_milestone=UpdateMilestone(self.uow_factory, reader),
            change_milestone_state=ChangeMilestoneState(self.uow_factory, self.ids, reader),
        )


@pytest.fixture
def world(clock) -> World:
    return World(clock)


@pytest.fixture
def api_clock(tmp_path, clock):
    """O app inteiro contra um banco migrado de verdade, com o relógio do teste (o atraso e a
    data de hoje dependem dele), o casal de exemplo criado e logado."""
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
    app = build_app(settings, clock=clock, hasher=_FakeHasher())
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
        url=url,
        clock=clock,
        noivo=entrar("exemplo.noivo"),
        noiva=entrar("exemplo.noiva"),
        anonimo=TestClient(app, base_url="https://testserver", headers=CSRF),
        sem_csrf=TestClient(app, base_url="https://testserver"),
    )
