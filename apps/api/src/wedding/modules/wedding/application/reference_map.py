from datetime import datetime

from wedding.modules.wedding.application.scope_dto import ReferenceDto
from wedding.modules.wedding.domain.reference import ScopeReference
from wedding.shared_kernel.actor import Actor


def to_reference_dto(reference: ScopeReference, actor: Actor, fallback: datetime) -> ReferenceDto:
    return ReferenceDto(
        id=reference.id,
        kind=reference.kind,
        url=reference.url,
        domain=reference.domain,
        file_id=reference.file_id,
        title=reference.title,
        comment=reference.comment,
        profile=reference.profile,
        added_at=reference.created_at or fallback,
        can_remove=reference.profile is actor.profile,
    )
