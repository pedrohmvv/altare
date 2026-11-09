from collections.abc import Callable
from dataclasses import dataclass

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
from wedding.modules.wedding.application.commands.update_scope_category import UpdateScopeCategory
from wedding.modules.wedding.application.queries.get_scope_map import GetScopeMap
from wedding.modules.wedding.application.queries.get_scope_standings import GetScopeStandings
from wedding.modules.wedding.application.queries.list_scope_category_history import (
    ListScopeCategoryHistory,
)


@dataclass(frozen=True)
class ScopeUseCases:
    """Os casos de uso do Mapa de Escopo, separados dos das Definições Base (cada um tem o seu
    pacote e o seu provedor)."""

    get_scope_map: GetScopeMap
    get_scope_standings: GetScopeStandings
    list_scope_category_history: ListScopeCategoryHistory
    create_scope_group: CreateScopeGroup
    rename_scope_group: RenameScopeGroup
    set_scope_group_visibility: SetScopeGroupVisibility
    delete_scope_group: DeleteScopeGroup
    create_scope_category: CreateScopeCategory
    update_scope_category: UpdateScopeCategory
    set_scope_category_visibility: SetScopeCategoryVisibility
    delete_scope_category: DeleteScopeCategory
    change_scope_status: ChangeScopeStatus
    set_my_evaluation: SetMyEvaluation


ScopeProvider = Callable[[], ScopeUseCases]
