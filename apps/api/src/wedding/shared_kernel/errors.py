from typing import Any, ClassVar


class DomainError(Exception):
    """Erro de domínio com `code` estável de máquina; o `detail` em pt-BR vive na borda HTTP."""

    default_code: ClassVar[str | None] = None
    # Os `{campos}` que o texto do `code` pede em `detail_params`; só o erro dono do `code` os
    # declara (um teste confere que todo campo de `platform/http/messages.py` tem dono).
    detail_params_keys: ClassVar[frozenset[str]] = frozenset()

    def __init__(
        self,
        code: str | None = None,
        *,
        data: dict[str, Any] | None = None,
        detail_params: dict[str, str] | None = None,
    ) -> None:
        resolved = code or self.default_code
        if resolved is None:
            raise ValueError(f"{type(self).__name__} exige um code")
        super().__init__(resolved)
        self.code = resolved
        # Dados de máquina que vão no corpo do erro e os valores que completam o texto pt-BR (o
        # `{nome}` do `detail` cadastrado em `platform/http/messages.py`).
        self.data = data or {}
        self.detail_params = detail_params or {}


class NotFound(DomainError):
    default_code = "not_found"


class Forbidden(DomainError):
    default_code = "forbidden"


class Unauthenticated(DomainError):
    default_code = "unauthenticated"


class DomainRuleViolated(DomainError): ...


class Conflict(DomainError): ...


class VersionConflict(Conflict):
    default_code = "version_conflict"


class TooManyAttempts(DomainError):
    default_code = "too_many_attempts"

    def __init__(self, retry_after: int) -> None:
        super().__init__()
        self.retry_after = retry_after
