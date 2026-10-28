from uuid import UUID

from wedding.modules.wedding.application.ports import ScopeRepository
from wedding.modules.wedding.application.scope_dto import (
    CategoryDto,
    EvaluationDto,
    GroupDto,
    ScopeMapDto,
)
from wedding.modules.wedding.domain.scope_entities import ScopeCategory, ScopeEvaluation
from wedding.modules.wedding.domain.scope_rules import (
    CategoryFacts,
    alignment,
    is_visible,
    progress,
    totals,
)
from wedding.modules.wedding.domain.scope_values import Origin
from wedding.shared_kernel.errors import NotFound
from wedding.shared_kernel.profile import ProfileKind


def _evaluation_dto(evaluation: ScopeEvaluation) -> EvaluationDto:
    return EvaluationDto(evaluation.priority, evaluation.note, evaluation.version)


def build_scope_map(scope: ScopeRepository) -> ScopeMapDto:
    """O mapa inteiro, com tudo o que é derivado calculado aqui e nunca gravado (`architecture.md`
    §5): alinhamento, visibilidade, progresso e totais."""
    groups = sorted(scope.list_groups(), key=lambda group: (group.position, group.name_key))
    categories = scope.list_categories()
    reasons = scope.discard_reasons()
    pairs: dict[UUID, dict[ProfileKind, ScopeEvaluation]] = {}
    for evaluation in scope.list_evaluations():
        pairs.setdefault(evaluation.category_id, {})[evaluation.profile] = evaluation
    group_hidden = {group.id: group.hidden_at is not None for group in groups}

    facts: list[CategoryFacts] = []

    def category_dto(category: ScopeCategory) -> CategoryDto:
        pair = pairs.get(category.id, {})
        noivo, noiva = pair.get(ProfileKind.NOIVO), pair.get(ProfileKind.NOIVA)
        if noivo is None or noiva is None:
            # O par nasce junto com a categoria; faltar um lado é dado corrompido, não erro de uso.
            raise RuntimeError(f"Categoria {category.id} sem o par de avaliações")
        visible = is_visible(
            category_hidden=category.hidden_at is not None,
            group_hidden=group_hidden.get(category.group_id, False),
            deleted=False,
        )
        facts.append(CategoryFacts(category.status, category.estimate_cents, visible))
        return CategoryDto(
            id=category.id,
            group_id=category.group_id,
            name=category.name,
            position=category.position,
            origin=category.origin,
            hidden=category.hidden_at is not None,
            visible=visible,
            status=category.status,
            estimate_cents=category.estimate_cents,
            discard_reason=reasons.get(category.id),
            noivo=_evaluation_dto(noivo),
            noiva=_evaluation_dto(noiva),
            alignment=alignment(noivo.priority, noiva.priority),
            can_delete=category.origin is Origin.COUPLE,
            version=category.version,
        )

    group_dtos = []
    for group in groups:
        members = sorted(
            (c for c in categories if c.group_id == group.id),
            key=lambda category: (category.position, category.name_key),
        )
        group_dtos.append(
            GroupDto(
                id=group.id,
                name=group.name,
                position=group.position,
                origin=group.origin,
                hidden=group.hidden_at is not None,
                can_delete=group.origin is Origin.COUPLE and not members,
                version=group.version,
                categories=tuple(category_dto(category) for category in members),
            )
        )
    return ScopeMapDto(tuple(group_dtos), progress(facts), totals(facts))


def require_category(scope: ScopeRepository, category_id: UUID) -> ScopeCategory:
    category = scope.get_category(category_id)
    if category is None:
        raise NotFound()
    return category
