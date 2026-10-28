from collections.abc import Callable
from dataclasses import dataclass

from wedding.modules.wedding.application.commands.add_image_reference import AddImageReference
from wedding.modules.wedding.application.commands.add_link_reference import AddLinkReference
from wedding.modules.wedding.application.commands.remove_reference import RemoveReference
from wedding.modules.wedding.application.queries.list_references import ListReferences


@dataclass(frozen=True)
class ReferenceUseCases:
    list_references: ListReferences
    add_link_reference: AddLinkReference
    add_image_reference: AddImageReference
    remove_reference: RemoveReference


ReferenceProvider = Callable[[], ReferenceUseCases]
