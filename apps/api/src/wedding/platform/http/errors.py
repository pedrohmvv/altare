import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import Response

from wedding.platform.http.problem import FieldError, problem_response
from wedding.shared_kernel.errors import (
    Conflict,
    DomainError,
    DomainRuleViolated,
    Forbidden,
    NotFound,
    TooManyAttempts,
    Unauthenticated,
    VersionConflict,
)

logger = logging.getLogger(__name__)

# Mais específico primeiro: VersionConflict é um Conflict (architecture.md §8).
_STATUS_BY_ERROR: tuple[tuple[type[DomainError], int], ...] = (
    (TooManyAttempts, 429),
    (VersionConflict, 409),
    (Conflict, 409),
    (DomainRuleViolated, 422),
    (NotFound, 404),
    (Forbidden, 403),
    (Unauthenticated, 401),
)

_CODE_BY_HTTP_STATUS = {404: "not_found", 405: "method_not_allowed"}

_FIELD_MESSAGES = {
    "missing": "Campo obrigatório.",
    "int_parsing": "Informe um número inteiro.",
}


def status_for(error_type: type[DomainError]) -> int | None:
    return next((status for kind, status in _STATUS_BY_ERROR if issubclass(error_type, kind)), None)


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def _domain_error(_: Request, exc: DomainError) -> Response:
        status = status_for(type(exc))
        if status is None:
            logger.error("Erro de domínio sem status HTTP: %s", type(exc).__name__)
            return problem_response(500, "internal_error")
        headers = (
            {"Retry-After": str(exc.retry_after)} if isinstance(exc, TooManyAttempts) else None
        )
        return problem_response(status, exc.code, headers=headers)

    @app.exception_handler(RequestValidationError)
    async def _validation_error(_: Request, exc: RequestValidationError) -> Response:
        errors = [
            FieldError(
                field=".".join(str(part) for part in error["loc"][1:]),
                message=_FIELD_MESSAGES.get(error["type"], "Valor inválido."),
            )
            for error in exc.errors()
        ]
        return problem_response(422, "validation_error", errors)

    @app.exception_handler(StarletteHTTPException)
    async def _http_error(_: Request, exc: StarletteHTTPException) -> Response:
        return problem_response(
            exc.status_code, _CODE_BY_HTTP_STATUS.get(exc.status_code, "http_error")
        )

    @app.exception_handler(Exception)
    async def _unexpected_error(_: Request, __: Exception) -> Response:
        return problem_response(500, "internal_error")
