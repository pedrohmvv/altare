from http import HTTPStatus
from typing import Any

from pydantic import BaseModel
from starlette.responses import JSONResponse

from wedding.platform.http.messages import message_for

PROBLEM_JSON = "application/problem+json"


class FieldError(BaseModel):
    field: str
    message: str


class ProblemDetails(BaseModel):
    """Erro no formato RFC 9457, com `code` estável de máquina e `detail` em pt-BR."""

    type: str = "about:blank"
    title: str
    status: int
    code: str
    detail: str
    errors: list[FieldError] | None = None
    data: dict[str, Any] | None = None


class _Params(dict[str, str]):
    def __missing__(self, key: str) -> str:
        # Um code com campo lançado sem o parâmetro vira um texto sem o detalhe, nunca um 500.
        return "…"


def _fill(detail: str, params: dict[str, str]) -> str:
    return detail.format_map(_Params(params))


def problem_response(
    status: int,
    code: str,
    errors: list[FieldError] | None = None,
    headers: dict[str, str] | None = None,
    data: dict[str, Any] | None = None,
    detail_params: dict[str, str] | None = None,
) -> JSONResponse:
    message = message_for(code)
    detail = _fill(message.detail, detail_params or {})
    problem = ProblemDetails(
        title=message.title,
        status=status,
        code=code,
        detail=detail,
        errors=errors,
        data=data or None,
    )
    return JSONResponse(
        problem.model_dump(mode="json", exclude_none=True),
        status_code=status,
        media_type=PROBLEM_JSON,
        headers=headers,
    )


def problem_responses(*statuses: int) -> dict[int | str, dict[str, Any]]:
    """Os erros que uma rota documenta no OpenAPI, para o cliente tipado enxergá-los.

    Declarar o 422 também dispensa o `HTTPValidationError` que o FastAPI acrescentaria.
    """
    return {
        status: {"model": ProblemDetails, "description": HTTPStatus(status).phrase}
        for status in statuses
    }
