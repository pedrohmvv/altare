from starlette.types import ASGIApp, Receive, Scope, Send

from wedding.platform.http.constants import API_ROOT, CSRF_HEADER
from wedding.platform.http.problem import problem_response

_MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
_HEADER_NAME = CSRF_HEADER.lower().encode()


class CsrfMiddleware:
    """Todo método que altera dados sob `/api` exige o header customizado (stack.md §3).

    Um formulário ou uma página de outra origem não consegue enviá-lo sem uma permissão de CORS,
    que a API não concede: é isso que impede o pedido forjado, além do `SameSite=Lax` do cookie.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if self._needs_header(scope) and not self._has_header(scope):
            await problem_response(403, "csrf_missing")(scope, receive, send)
            return
        await self.app(scope, receive, send)

    @staticmethod
    def _needs_header(scope: Scope) -> bool:
        return (
            scope["type"] == "http"
            and scope["method"] in _MUTATING_METHODS
            and scope["path"].startswith(f"{API_ROOT}/")
        )

    @staticmethod
    def _has_header(scope: Scope) -> bool:
        return any(name == _HEADER_NAME and value == b"1" for name, value in scope["headers"])
