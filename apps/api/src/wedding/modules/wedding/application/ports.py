from collections.abc import Callable
from types import TracebackType
from typing import Protocol, Self
from uuid import UUID

from wedding.modules.wedding.application.dto import BaselineChangeDto
from wedding.modules.wedding.application.scope_dto import StatusChangeDto
from wedding.modules.wedding.domain.entities import BaselineChange, BaselineField
from wedding.modules.wedding.domain.reference import ScopeReference
from wedding.modules.wedding.domain.scope_entities import (
    ScopeCategory,
    ScopeEvaluation,
    ScopeGroup,
    ScopeStatusChange,
)
from wedding.modules.wedding.domain.value_objects import BaselineKey
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.profile import ProfileKind


class BaselineRepository(Protocol):
    def get(self, key: BaselineKey) -> BaselineField | None: ...

    def all(self) -> list[BaselineField]: ...

    def add_change(self, change: BaselineChange) -> None: ...

    def changes(self, limit: int) -> list[BaselineChangeDto]:
        """As alterações mais recentes primeiro (consulta: devolve DTO, não entidade)."""
        ...


class ScopeRepository(Protocol):
    """Grupos, categorias, avaliações e histórico do Mapa de Escopo. Tudo o que lê já filtra a
    exclusão lógica; ocultas continuam aparecendo (o domínio decide o que é visível)."""

    def get_group(self, group_id: UUID) -> ScopeGroup | None: ...

    def list_groups(self) -> list[ScopeGroup]: ...

    def add_group(self, group: ScopeGroup) -> None: ...

    def next_group_position(self) -> int: ...

    def group_name_taken(self, key: str, *, excluding: UUID | None = None) -> bool: ...

    def count_categories(self, group_id: UUID) -> int: ...

    def get_category(self, category_id: UUID) -> ScopeCategory | None: ...

    def list_categories(self) -> list[ScopeCategory]: ...

    def add_category(self, category: ScopeCategory) -> None: ...

    def next_category_position(self, group_id: UUID) -> int: ...

    def category_name_taken(self, key: str, *, excluding: UUID | None = None) -> bool: ...

    def get_evaluation(self, category_id: UUID, profile: ProfileKind) -> ScopeEvaluation | None: ...

    def list_evaluations(self) -> list[ScopeEvaluation]: ...

    def add_evaluation(self, evaluation: ScopeEvaluation) -> None: ...

    def add_status_change(self, change: ScopeStatusChange) -> None: ...

    def status_history(self, category_id: UUID) -> list[StatusChangeDto]:
        """Do mais recente ao mais antigo (consulta: devolve DTO, não entidade)."""
        ...

    def discard_reasons(self) -> dict[UUID, str | None]:
        """Por categoria, o motivo da última mudança para `Fica de fora` (F-PLN-03, regra 3)."""
        ...


class WeddingUnitOfWork(Protocol):
    @property
    def baseline(self) -> BaselineRepository: ...

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...


# Quem lê ou altera é sempre alguém na sessão: o ator vai para o histórico do registro.
WeddingUnitOfWorkFactory = Callable[[Actor], WeddingUnitOfWork]


class ScopeUnitOfWork(Protocol):
    @property
    def scope(self) -> ScopeRepository: ...

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...


ScopeUnitOfWorkFactory = Callable[[Actor], ScopeUnitOfWork]


class ReferenceRepository(Protocol):
    """Referências por frente; só lê as não removidas (exclusão lógica)."""

    def add(self, reference: ScopeReference) -> None: ...

    def get(self, reference_id: UUID) -> ScopeReference | None: ...

    def list_for(self, category_id: UUID) -> list[ScopeReference]:
        """Da mais nova para a mais antiga."""
        ...


class ReferenceUnitOfWork(Protocol):
    @property
    def scope(self) -> ScopeRepository: ...

    @property
    def references(self) -> ReferenceRepository: ...

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...


ReferenceUnitOfWorkFactory = Callable[[Actor], ReferenceUnitOfWork]


class StoredFile:
    """O que o Mapa precisa saber de um arquivo enviado: que existe e se é imagem."""

    def __init__(self, file_id: UUID, is_image: bool) -> None:
        self.file_id = file_id
        self.is_image = is_image


class FileCatalog(Protocol):
    """Porta para o módulo de arquivos: o `wedding` não o importa; o bootstrap liga os dois."""

    def find(self, file_id: UUID, actor: Actor) -> StoredFile | None: ...


class GuestCountReader(Protocol):
    """Porta para a lista de convidados: o `wedding` não importa o módulo `guests`; o bootstrap
    liga os dois. Devolve o Total Nominal, a "contagem de cabeças" que o Porte mostra ao lado da
    faixa que o casal definiu, derivada na hora e nunca copiada (`F-PLN-01`, `D-067`)."""

    def total_nominal(self, actor: Actor) -> int: ...
