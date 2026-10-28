from typing import Any

from fastapi import FastAPI

from wedding.platform.http.problem import PROBLEM_JSON


def install_problem_media_type(app: FastAPI) -> None:
    """O FastAPI documenta o `model` de um erro como `application/json`; o corpo real é
    `application/problem+json`, e é esse o tipo que o cliente gerado precisa ver."""
    original = app.openapi

    def openapi() -> dict[str, Any]:
        schema = original()
        _retype_problem_responses(schema)
        return schema

    app.openapi = openapi  # type: ignore[method-assign]


def _retype_problem_responses(schema: dict[str, Any]) -> None:
    for path_item in schema.get("paths", {}).values():
        for operation in path_item.values():
            for status, response in operation.get("responses", {}).items():
                content = response.get("content", {})
                media = content.get("application/json")
                if (
                    int(status) >= 400
                    and media
                    and media["schema"].get("$ref", "").endswith("/ProblemDetails")
                ):
                    del content["application/json"]
                    content[PROBLEM_JSON] = media
