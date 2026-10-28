from wedding.modules.wedding.adapters.http.schemas import (
    BaselineChangeOut,
    BaselineOut,
    CeilingFieldOut,
    CeilingValueSchema,
    CeremonyFieldOut,
    CeremonyValueSchema,
    DateFieldOut,
    DateValueSchema,
    MonthYearSchema,
    SizeFieldOut,
    SizeValueSchema,
    SnapshotOut,
    TextFieldOut,
)
from wedding.modules.wedding.application.dto import (
    BaselineChangeDto,
    BaselineDto,
    BaselineFieldDto,
    FieldSnapshotDto,
)
from wedding.modules.wedding.domain.value_objects import (
    BaselineValue,
    CeilingValue,
    CeremonyValue,
    DateKind,
    DateValue,
    MonthYear,
    SizeValue,
    TextValue,
)

# Da entrada para o domínio: o formulário manda campos soltos; o domínio decide se formam um valor.


def to_date_value(schema: DateValueSchema) -> DateValue | None:
    if schema.kind is DateKind.NONE:
        return None
    return DateValue(
        kind=schema.kind,
        window_start=_month_year(schema.window_start),
        window_end=_month_year(schema.window_end),
        label=schema.label,
        exact=schema.exact,
    )


def _month_year(schema: MonthYearSchema | None) -> MonthYear | None:
    return MonthYear(schema.year, schema.month) if schema else None


def to_text_value(text: str | None) -> TextValue | None:
    # Em branco vale como vazio: o domínio decide se o campo pode ficar assim.
    return TextValue(text) if text is not None and text.strip() else None


def to_size_value(schema: SizeValueSchema) -> SizeValue | None:
    if schema.minimum is None and schema.maximum is None:
        return None
    return SizeValue(schema.minimum, schema.maximum)  # type: ignore[arg-type]


def to_ceiling_value(schema: CeilingValueSchema) -> CeilingValue | None:
    return CeilingValue(schema.cents) if schema.cents is not None else None


def to_ceremony_value(schema: CeremonyValueSchema) -> CeremonyValue | None:
    if not schema.kinds:
        return None
    return CeremonyValue(kinds=frozenset(schema.kinds), detail=schema.detail)


# Do domínio para a saída.


def _date_schema(value: DateValue | None) -> DateValueSchema:
    if value is None:
        return DateValueSchema(kind=DateKind.NONE)
    return DateValueSchema(
        kind=value.kind,
        window_start=_month_year_schema(value.window_start),
        window_end=_month_year_schema(value.window_end),
        label=value.label,
        exact=value.exact,
    )


def _month_year_schema(value: MonthYear | None) -> MonthYearSchema | None:
    return MonthYearSchema(year=value.year, month=value.month) if value else None


def _size_schema(value: SizeValue | None) -> SizeValueSchema:
    return (
        SizeValueSchema(minimum=value.minimum, maximum=value.maximum)
        if value
        else SizeValueSchema()
    )


def _ceiling_schema(value: CeilingValue | None) -> CeilingValueSchema:
    return CeilingValueSchema(cents=value.cents if value else None)


def _ceremony_schema(value: CeremonyValue | None) -> CeremonyValueSchema:
    if value is None:
        return CeremonyValueSchema()
    return CeremonyValueSchema(kinds=sorted(value.kinds), detail=value.detail)


def to_baseline_out(dto: BaselineDto) -> BaselineOut:
    return BaselineOut(
        date=DateFieldOut(
            status=dto.date.status,
            note=dto.date.note,
            version=dto.date.version,
            value=_date_schema(dto.date.value),
        ),
        city=_text_field(dto.city),
        format=_text_field(dto.format),
        size=SizeFieldOut(
            status=dto.size.status,
            note=dto.size.note,
            version=dto.size.version,
            value=_size_schema(dto.size.value),
        ),
        ceiling=CeilingFieldOut(
            status=dto.ceiling.status,
            note=dto.ceiling.note,
            version=dto.ceiling.version,
            value=_ceiling_schema(dto.ceiling.value),
        ),
        ceremony=CeremonyFieldOut(
            status=dto.ceremony.status,
            note=dto.ceremony.note,
            version=dto.ceremony.version,
            value=_ceremony_schema(dto.ceremony.value),
        ),
    )


def _text_field(field: BaselineFieldDto[TextValue]) -> TextFieldOut:
    return TextFieldOut(
        status=field.status,
        note=field.note,
        version=field.version,
        value=field.value.text if field.value else None,
    )


def _snapshot_value(
    value: BaselineValue | None,
) -> DateValueSchema | SizeValueSchema | CeilingValueSchema | CeremonyValueSchema | str | None:
    match value:
        case None:
            return None
        case DateValue():
            return _date_schema(value)
        case TextValue():
            return value.text
        case SizeValue():
            return _size_schema(value)
        case CeilingValue():
            return _ceiling_schema(value)
        case CeremonyValue():
            return _ceremony_schema(value)


def _snapshot(snapshot: FieldSnapshotDto) -> SnapshotOut:
    return SnapshotOut(
        status=snapshot.status, note=snapshot.note, value=_snapshot_value(snapshot.value)
    )


def to_change_out(dto: BaselineChangeDto) -> BaselineChangeOut:
    return BaselineChangeOut.model_validate(
        {
            "id": dto.id,
            "field": dto.key,
            "before": _snapshot(dto.before),
            "after": _snapshot(dto.after),
            "by": dto.profile,
            "at": dto.changed_at,
        }
    )
