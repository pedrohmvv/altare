from collections.abc import Callable
from dataclasses import dataclass

from wedding.modules.files.application.commands.upload_file import UploadFile
from wedding.modules.files.application.queries.get_file import GetFile
from wedding.modules.files.application.queries.get_file_info import GetFileInfo


@dataclass(frozen=True)
class FilesUseCases:
    upload_file: UploadFile
    get_file: GetFile
    get_file_info: GetFileInfo


FilesProvider = Callable[[], FilesUseCases]
