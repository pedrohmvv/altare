from wedding.modules.wedding.adapters.http.scope_schemas import (
    AlignmentOut,
    CategoryOut,
    EvaluationOut,
    GroupOut,
    ProgressOut,
    ScopeMapOut,
    StatusChangeOut,
    TotalsOut,
)
from wedding.modules.wedding.application.scope_dto import (
    CategoryDto,
    EvaluationDto,
    GroupDto,
    ScopeMapDto,
    StatusChangeDto,
)


def _evaluation(dto: EvaluationDto) -> EvaluationOut:
    return EvaluationOut.model_validate(
        {"priority": dto.priority, "note": dto.note, "version": dto.version}
    )


def _category(dto: CategoryDto) -> CategoryOut:
    return CategoryOut.model_validate(
        {
            "id": dto.id,
            "group_id": dto.group_id,
            "name": dto.name,
            "position": dto.position,
            "origin": dto.origin,
            "hidden": dto.hidden,
            "visible": dto.visible,
            "status": dto.status,
            "estimate_cents": dto.estimate_cents,
            "discard_reason": dto.discard_reason,
            "noivo": _evaluation(dto.noivo),
            "noiva": _evaluation(dto.noiva),
            "alignment": AlignmentOut.model_validate(
                {"state": dto.alignment.state, "missing": list(dto.alignment.missing)}
            ),
            "can_delete": dto.can_delete,
            "version": dto.version,
        }
    )


def _group(dto: GroupDto) -> GroupOut:
    return GroupOut.model_validate(
        {
            "id": dto.id,
            "name": dto.name,
            "position": dto.position,
            "origin": dto.origin,
            "hidden": dto.hidden,
            "can_delete": dto.can_delete,
            "version": dto.version,
            "categories": [_category(category) for category in dto.categories],
        }
    )


def to_scope_map_out(dto: ScopeMapDto) -> ScopeMapOut:
    return ScopeMapOut(
        groups=[_group(group) for group in dto.groups],
        progress=ProgressOut(classified=dto.progress.classified, total=dto.progress.total),
        totals=TotalsOut(
            essential_cents=dto.totals.essential_cents,
            essential_without_estimate=dto.totals.essential_without_estimate,
            maybe_cents=dto.totals.maybe_cents,
            maybe_without_estimate=dto.totals.maybe_without_estimate,
        ),
    )


def to_status_change_out(dto: StatusChangeDto) -> StatusChangeOut:
    return StatusChangeOut.model_validate(
        {
            "id": dto.id,
            "from_status": dto.from_status,
            "to_status": dto.to_status,
            "reason": dto.reason,
            "by": dto.profile,
            "at": dto.changed_at,
        }
    )
