from dataclasses import dataclass
from uuid import UUID

from wedding.modules.wedding.application.ports import FileCatalog, ReferenceUnitOfWorkFactory
from wedding.modules.wedding.application.reference_map import to_reference_dto
from wedding.modules.wedding.application.scope_dto import ReferenceDto
from wedding.modules.wedding.application.scope_map import require_category
from wedding.modules.wedding.domain.errors import ReferenceFileNotImage
from wedding.modules.wedding.domain.reference import ScopeReference
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.clock import Clock
from wedding.shared_kernel.errors import NotFound
from wedding.shared_kernel.ids import IdGenerator


@dataclass(frozen=True)
class AddImageReferenceCommand:
    category_id: UUID
    file_id: UUID
    title: str | None
    comment: str | None


class AddImageReference:
    def __init__(
        self,
        uow_factory: ReferenceUnitOfWorkFactory,
        ids: IdGenerator,
        clock: Clock,
        files: FileCatalog,
    ) -> None:
        self._uow_factory = uow_factory
        self._ids = ids
        self._clock = clock
        self._files = files

    def execute(self, command: AddImageReferenceCommand, actor: Actor) -> list[ReferenceDto]:
        """A imagem é um arquivo já enviado (`POST /files`, com o tipo conferido pela assinatura
        real). Aqui só se confere que ele existe e é imagem: PDF não entra como referência."""
        stored = self._files.find(command.file_id, actor)
        if stored is None:
            raise NotFound()
        if not stored.is_image:
            raise ReferenceFileNotImage()
        with self._uow_factory(actor) as uow:
            category = require_category(uow.scope, command.category_id)
            uow.references.add(
                ScopeReference.new_image(
                    id=self._ids.new_id(),
                    category_id=category.id,
                    profile=actor.profile,
                    file_id=stored.file_id,
                    title=command.title,
                    comment=command.comment,
                )
            )
            uow.commit()
            return [
                to_reference_dto(r, actor, self._clock.now())
                for r in uow.references.list_for(category.id)
            ]
