from collections import deque
from collections.abc import Iterable, Sequence
from uuid import UUID

from wedding.modules.schedule.domain.entities import Dependency


def _adjacency(edges: Iterable[Dependency]) -> dict[UUID, list[UUID]]:
    """Para cada marco, os marcos de que ele depende, em ordem fixa (o caminho mostrado não
    depende da ordem em que o banco devolveu as linhas)."""
    adjacency: dict[UUID, list[UUID]] = {}
    for edge in edges:
        adjacency.setdefault(edge.milestone_id, []).append(edge.depends_on_id)
    for predecessors in adjacency.values():
        predecessors.sort()
    return adjacency


def depends_path(edges: Iterable[Dependency], start: UUID, goal: UUID) -> tuple[UUID, ...] | None:
    """O caminho mais curto de `start` até `goal` seguindo "depende de", com os dois extremos, ou
    `None` se `start` não depende de `goal`, nem transitivamente."""
    adjacency = _adjacency(edges)
    came_from: dict[UUID, UUID | None] = {start: None}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        if current == goal:
            path = [current]
            while (previous := came_from[path[-1]]) is not None:
                path.append(previous)
            return tuple(reversed(path))
        for predecessor in adjacency.get(current, ()):
            if predecessor not in came_from:
                came_from[predecessor] = current
                queue.append(predecessor)
    return None


def find_cycle(
    edges: Iterable[Dependency], milestone_id: UUID, predecessors: Sequence[UUID]
) -> tuple[UUID, ...] | None:
    """Fazer `milestone_id` depender de `predecessors` fecha um ciclo quando algum deles já depende
    dele, direta ou transitivamente (F-CRN-03, regra 2). Devolve o caminho do ciclo, do marco
    até ele mesmo (`C → A → B → C`), ou `None` se nada fecha. As dependências antigas do próprio
    marco não atrapalham: nenhum caminho até ele passa por elas."""
    known = list(edges)
    for predecessor in predecessors:
        path = depends_path(known, predecessor, milestone_id)
        if path is not None:
            return (milestone_id, *path)
    return None


def split_restorable(
    live_edges: Iterable[Dependency], candidates: Sequence[Dependency]
) -> tuple[list[Dependency], list[Dependency]]:
    """Das arestas que saíram junto com um marco, as que podem voltar e as que hoje fechariam um
    ciclo. Cada aceita já conta para as seguintes."""
    current = list(live_edges)
    accepted: list[Dependency] = []
    left_out: list[Dependency] = []
    for edge in candidates:
        if depends_path(current, edge.depends_on_id, edge.milestone_id) is None:
            accepted.append(edge)
            current.append(edge)
        else:
            left_out.append(edge)
    return accepted, left_out
