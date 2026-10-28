from sqlalchemy import inspect

from wedding.modules.wedding.domain.entities import BaselineChange, BaselineField
from wedding.modules.wedding.domain.reference import ScopeReference
from wedding.modules.wedding.domain.scope_entities import (
    ScopeCategory,
    ScopeEvaluation,
    ScopeGroup,
    ScopeStatusChange,
)
from wedding.modules.wedding.infrastructure.reference_tables import scope_references
from wedding.modules.wedding.infrastructure.scope_tables import (
    scope_categories,
    scope_evaluations,
    scope_groups,
    scope_status_changes,
)
from wedding.modules.wedding.infrastructure.tables import baseline_changes, baseline_fields
from wedding.platform.db.metadata import mapper_registry


def start_mappers() -> None:
    """Liga as dataclasses do domínio às tabelas; pode ser chamada mais de uma vez."""
    if inspect(BaselineField, raiseerr=False) is None:
        mapper_registry.map_imperatively(
            BaselineField,
            baseline_fields,
            version_id_col=baseline_fields.c.version,
            # O domínio chama de `key`; a coluna diz de que variável é.
            properties={"key": baseline_fields.c.field_key},
        )
    if inspect(BaselineChange, raiseerr=False) is None:
        mapper_registry.map_imperatively(
            BaselineChange,
            baseline_changes,
            version_id_col=baseline_changes.c.version,
            properties={
                "key": baseline_changes.c.field_key,
                "before": baseline_changes.c.state_before,
                "after": baseline_changes.c.state_after,
            },
        )
    for entity, table in (
        (ScopeGroup, scope_groups),
        (ScopeCategory, scope_categories),
        (ScopeEvaluation, scope_evaluations),
        (ScopeStatusChange, scope_status_changes),
        (ScopeReference, scope_references),
    ):
        if inspect(entity, raiseerr=False) is None:
            mapper_registry.map_imperatively(entity, table, version_id_col=table.c.version)
