from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import StreamingResponse

from wedding.modules.files.adapters.http.mappers import content_disposition, to_file_asset_out
from wedding.modules.files.adapters.http.schemas import FileAssetOut
from wedding.modules.files.application.commands.upload_file import UploadFileCommand
from wedding.modules.files.application.use_cases import FilesProvider
from wedding.modules.files.domain.rules import MAX_FILE_BYTES
from wedding.modules.files.domain.value_objects import FileKind
from wedding.platform.http.problem import problem_responses
from wedding.platform.http.session import current_actor
from wedding.shared_kernel.actor import Actor

_BINARY = {"schema": {"type": "string", "format": "binary"}}
_DOWNLOAD_OK = {
    200: {
        "description": "O conteúdo do arquivo, com o tipo que a assinatura dele mostrou.",
        "content": {kind.value: _BINARY for kind in FileKind},
    }
}


def build_router(provide: FilesProvider) -> APIRouter:
    router = APIRouter(prefix="/files", tags=["files"])

    @router.post(
        "",
        operation_id="upload_file",
        status_code=201,
        response_model=FileAssetOut,
        responses=problem_responses(401, 403, 422),
    )
    def upload_file(
        file: UploadFile, actor: Annotated[Actor, Depends(current_actor)]
    ) -> FileAssetOut:
        # Lê um byte além do limite: basta para o domínio recusar, sem carregar o excedente.
        content = file.file.read(MAX_FILE_BYTES + 1)
        uploaded = provide().upload_file.execute(UploadFileCommand(file.filename, content), actor)
        return to_file_asset_out(uploaded)

    @router.get(
        "/{file_id}",
        operation_id="download_file",
        response_class=StreamingResponse,
        responses={**_DOWNLOAD_OK, **problem_responses(401, 404, 422)},
    )
    def download_file(
        file_id: UUID, actor: Annotated[Actor, Depends(current_actor)]
    ) -> StreamingResponse:
        found = provide().get_file.execute(file_id, actor)
        return StreamingResponse(
            found.chunks,
            media_type=found.file.content_type,
            headers={
                "Content-Length": str(found.file.size_bytes),
                "Content-Disposition": content_disposition(found.file.name),
                # O tipo servido é o da assinatura validada: o navegador não pode adivinhar outro.
                "X-Content-Type-Options": "nosniff",
                "Cache-Control": "private, no-store",
            },
        )

    return router
