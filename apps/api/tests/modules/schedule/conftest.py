import copy
from datetime import date
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

from wedding.modules.schedule.application.commands.add_checklist_item import AddChecklistItem
from wedding.modules.schedule.application.commands.change_milestone_state import (
    ChangeMilestoneState,
)
from wedding.modules.schedule.application.commands.change_task_state import ChangeTaskState
from wedding.modules.schedule.application.commands.create_milestone import CreateMilestone
from wedding.modules.schedule.application.commands.create_phase import CreatePhase
from wedding.modules.schedule.application.commands.create_task import CreateTask
from wedding.modules.schedule.application.commands.delete_milestone import DeleteMilestone
from wedding.modules.schedule.application.commands.delete_task import DeleteTask
from wedding.modules.schedule.application.commands.remove_checklist_item import (
    RemoveChecklistItem,
)
from wedding.modules.schedule.application.commands.rename_phase import RenamePhase
from wedding.modules.schedule.application.commands.reorder_checklist import ReorderChecklist
from wedding.modules.schedule.application.commands.reorder_phases import ReorderPhases
from wedding.modules.schedule.application.commands.restore_milestone import RestoreMilestone
from wedding.modules.schedule.application.commands.restore_task import RestoreTask
from wedding.modules.schedule.application.commands.set_milestone_dependencies import (
    SetMilestoneDependencies,
)
from wedding.modules.schedule.application.commands.update_checklist_item import (
    UpdateChecklistItem,
)
from wedding.modules.schedule.application.commands.update_milestone import UpdateMilestone
from wedding.modules.schedule.application.commands.update_milestone_window import (
    UpdateMilestoneWindow,
)
from wedding.modules.schedule.application.commands.update_task import UpdateTask
from wedding.modules.schedule.application.ports import CategoryInfo, WeddingDate
from wedding.modules.schedule.application.queries.preview_date_change import PreviewDateChange
from wedding.modules.schedule.application.queries.read_schedule import ReadSchedule
from wedding.modules.schedule.application.schedule_map import ScheduleReader
from wedding.modules.schedule.application.use_cases import ScheduleUseCases
from wedding.modules.schedule.domain.entities import (
    ChecklistItem,
    Dependency,
    Milestone,
    MilestoneChange,
    MilestoneDependency,
    Phase,
    Task,
)
from wedding.modules.schedule.domain.values import OwnerKind, Standing
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
        self.links: list[MilestoneDependency] = []
        self.changes: list[MilestoneChange] = []
        self.tasks: dict[UUID, Task] = {}
        self.items: dict[UUID, ChecklistItem] = {}


class _Repository:
    """O cronograma em memória, com as mesmas regras de leitura do SQL: exclusão lógica filtrada
    e, nas dependências, só os vínculos vivos entre marcos vivos."""

    def __init__(self, store: Store) -> None:
        self.store = store

    def list_phases(self) -> list[Phase]:
        return list(self.store.phases.values())

    def get_phase(self, phase_id: UUID) -> Phase | None:
        return self.store.phases.get(phase_id)

    def add_phase(self, phase: Phase) -> None:
        self.store.phases[phase.id] = phase

    def next_phase_position(self) -> int:
        return max((p.position for p in self.store.phases.values()), default=-1) + 1

    def list_milestones(self) -> list[Milestone]:
        return [m for m in self.store.milestones.values() if m.deleted_at is None]

    def get_milestone(
        self, milestone_id: UUID, *, include_deleted: bool = False
    ) -> Milestone | None:
        found = self.store.milestones.get(milestone_id)
        if found is None or (found.deleted_at is not None and not include_deleted):
            return None
        return found

    def add_milestone(self, milestone: Milestone) -> None:
        self.store.milestones[milestone.id] = milestone

    def next_milestone_position(self, phase_id: UUID) -> int:
        positions = [m.position for m in self.list_milestones() if m.phase_id == phase_id]
        return max(positions, default=-1) + 1

    def dependencies(self) -> list[Dependency]:
        live = {m.id for m in self.list_milestones()}
        return [
            link.as_edge()
            for link in self.store.links
            if link.deleted_at is None and link.milestone_id in live and link.depends_on_id in live
        ]

    def live_links_of(self, milestone_id: UUID) -> list[MilestoneDependency]:
        return [
            link
            for link in self.store.links
            if link.deleted_at is None and milestone_id in (link.milestone_id, link.depends_on_id)
        ]

    def deleted_links_of(self, milestone_id: UUID) -> list[MilestoneDependency]:
        return [
            link
            for link in self.store.links
            if link.deleted_at is not None
            and milestone_id in (link.milestone_id, link.depends_on_id)
        ]

    def add_link(self, link: MilestoneDependency) -> None:
        self.store.links.append(link)

    def add_change(self, change: MilestoneChange) -> None:
        self.store.changes.append(change)

    def list_tasks(self) -> list[Task]:
        return [t for t in self.store.tasks.values() if t.deleted_at is None]

    def get_task(self, task_id: UUID, *, include_deleted: bool = False) -> Task | None:
        found = self.store.tasks.get(task_id)
        if found is None or (found.deleted_at is not None and not include_deleted):
            return None
        return found

    def add_task(self, task: Task) -> None:
        self.store.tasks[task.id] = task

    def list_checklist_items(self) -> list[ChecklistItem]:
        return [i for i in self.store.items.values() if i.deleted_at is None]

    def live_items_of(self, kind: OwnerKind, owner_id: UUID) -> list[ChecklistItem]:
        return sorted(
            (
                i
                for i in self.list_checklist_items()
                if i.owner_kind is kind and i.owner_id == owner_id
            ),
            key=lambda i: (i.position, i.id),
        )

    def get_checklist_item(self, item_id: UUID) -> ChecklistItem | None:
        found = self.store.items.get(item_id)
        return None if found is None or found.deleted_at is not None else found

    def add_checklist_item(self, item: ChecklistItem) -> None:
        self.store.items[item.id] = item


class _UnitOfWork:
    """Transação de mentira: trabalha numa cópia e só a publica no commit, subindo a `version`
    dos marcos que mudaram, como o mapeamento faz."""

    def __init__(self, world: "World", actor: Actor) -> None:
        self._world = world
        world.actors.append(actor)
        self._store = copy.deepcopy(world.store)
        self._before = copy.deepcopy(world.store.milestones)
        self._phases_before = copy.deepcopy(world.store.phases)
        self._tasks_before = copy.deepcopy(world.store.tasks)
        self._items_before = copy.deepcopy(world.store.items)
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
        _bump(self._store.milestones, self._before)
        _bump(self._store.phases, self._phases_before)
        _bump(self._store.tasks, self._tasks_before)
        _bump(self._store.items, self._items_before)
        for link in self._store.links:
            link.version = link.version or 1
        self._world.store = self._store
        self._before = copy.deepcopy(self._store.milestones)
        self._phases_before = copy.deepcopy(self._store.phases)
        self._tasks_before = copy.deepcopy(self._store.tasks)
        self._items_before = copy.deepcopy(self._store.items)

    def rollback(self) -> None:
        return None


def _bump(items: dict, before: dict) -> None:
    """Como o mapeamento: novo começa em 1; mudado sobe um; igual fica."""
    for key, item in items.items():
        original = before.get(key)
        if original is None:
            item.version = 1
        elif item != original:
            item.version = original.version + 1


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
        for codigo, fase, titulo, categoria, dependencias, janela in MARCOS:
            inicio, fim, unidade = janela or (None, None, None)
            ordem = posicao.get(fase, 0)
            posicao[fase] = ordem + 1
            self.store.milestones[marco_id(codigo)] = Milestone(
                id=marco_id(codigo),
                phase_id=fase_id(fase + 1),
                title=titulo,
                position=ordem,
                category_id=categoria_id(categoria) if categoria else None,
                window_start_before=inicio,
                window_end_before=fim,
                window_unit=unidade,
                version=1,
            )
            if categoria:
                self.categories[categoria_id(categoria)] = CategoryInfo(
                    categoria, Standing.IN_DISCUSSION, True
                )
            for dep in dependencias:
                self.store.links.append(
                    MilestoneDependency(
                        id=self.ids.new_id(),
                        milestone_id=marco_id(codigo),
                        depends_on_id=marco_id(dep),
                        version=1,
                    )
                )

    def set_wedding_date(self, exact: date | None, *, defined: bool = True) -> None:
        """A data do casamento nas Definições Base: exata e `Definida` por padrão (Modo Com Data);
        `None` volta ao Modo Sem Data."""
        self.wedding_date = WeddingDate(defined=defined and exact is not None, exact=exact)

    def classify(self, nome: str, standing: Standing, visible: bool = True) -> None:
        # Como o bootstrap: a categoria oculta conta como `Fica de fora` para o cronograma.
        folded = standing if visible else Standing.OUT
        self.categories[categoria_id(nome)] = CategoryInfo(nome, folded, visible)

    def classify_all(self, standing: Standing = Standing.ENTERS) -> None:
        for nome in [info.name for info in self.categories.values()]:
            self.classify(nome, standing)

    def uow_factory(self, actor: Actor) -> _UnitOfWork:
        return _UnitOfWork(self, actor)

    def use_cases(self) -> ScheduleUseCases:
        reader = ScheduleReader(_Categories(self), _WeddingDate(self), self.clock)
        categories = _Categories(self)
        return ScheduleUseCases(
            read_schedule=ReadSchedule(self.uow_factory, reader),
            update_milestone=UpdateMilestone(self.uow_factory, reader, categories),
            update_milestone_window=UpdateMilestoneWindow(self.uow_factory, reader),
            preview_date_change=PreviewDateChange(self.uow_factory, reader),
            change_milestone_state=ChangeMilestoneState(self.uow_factory, self.ids, reader),
            create_milestone=CreateMilestone(self.uow_factory, self.ids, reader, categories),
            delete_milestone=DeleteMilestone(self.uow_factory, self.clock, reader),
            restore_milestone=RestoreMilestone(self.uow_factory, reader),
            set_milestone_dependencies=SetMilestoneDependencies(
                self.uow_factory, self.ids, self.clock, reader
            ),
            create_phase=CreatePhase(self.uow_factory, self.ids, reader),
            rename_phase=RenamePhase(self.uow_factory, reader),
            reorder_phases=ReorderPhases(self.uow_factory, reader),
            create_task=CreateTask(self.uow_factory, self.ids, reader),
            update_task=UpdateTask(self.uow_factory, reader),
            change_task_state=ChangeTaskState(self.uow_factory, reader),
            delete_task=DeleteTask(self.uow_factory, self.clock, reader),
            restore_task=RestoreTask(self.uow_factory, reader),
            add_checklist_item=AddChecklistItem(self.uow_factory, self.ids, reader),
            update_checklist_item=UpdateChecklistItem(self.uow_factory, reader),
            remove_checklist_item=RemoveChecklistItem(self.uow_factory, self.clock, reader),
            reorder_checklist=ReorderChecklist(self.uow_factory, reader),
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
