from typing import Any

from sqlalchemy import Column, Integer, Uuid, event
from sqlalchemy.orm import Session, object_mapper

from wedding.platform.db.types import UtcDateTime

ACTOR_KEY = "audit.actor_id"
CLOCK_KEY = "audit.clock"


def audit_columns() -> list[Column[Any]]:
    """Histórico básico de todo registro (architecture.md §10). Uma fábrica: um `Column` não se
    reaproveita entre tabelas."""
    return [
        Column("id", Uuid, primary_key=True, comment="Identificador do registro (UUID)."),
        Column("created_at", UtcDateTime, nullable=False, comment="Instante da criação, em UTC."),
        Column("updated_at", UtcDateTime, nullable=False, comment="Instante da última alteração."),
        Column("created_by", Uuid, comment="Usuário da sessão que criou; nulo se veio da CLI."),
        Column("updated_by", Uuid, comment="Usuário da sessão que alterou por último."),
        Column("deleted_at", UtcDateTime, comment="Instante da exclusão lógica; nulo se ativo."),
        Column("deleted_by", Uuid, comment="Usuário da sessão que excluiu."),
        Column("version", Integer, nullable=False, comment="Bloqueio otimista."),
    ]


def _is_audited(instance: object) -> bool:
    return "updated_at" in object_mapper(instance).columns


@event.listens_for(Session, "before_flush")
def stamp_audit_columns(session: Session, _context: Any, _instances: Any) -> None:
    created: list[Any] = [obj for obj in session.new if _is_audited(obj)]
    changed: list[Any] = [
        obj for obj in session.dirty if _is_audited(obj) and session.is_modified(obj)
    ]
    if not created and not changed:
        return
    if CLOCK_KEY not in session.info:
        raise RuntimeError("Entidade com histórico básico gravada fora de uma UnitOfWork")

    now = session.info[CLOCK_KEY].now()
    actor_id = session.info.get(ACTOR_KEY)
    for obj in created:
        obj.created_at = obj.updated_at = now
        obj.created_by = obj.updated_by = actor_id
    for obj in changed:
        obj.updated_at = now
        obj.updated_by = actor_id
