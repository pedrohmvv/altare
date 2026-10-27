from typing import ClassVar


class DomainError(Exception):
    """Erro de domínio com `code` estável de máquina; o `detail` em pt-BR vive na borda HTTP."""

    default_code: ClassVar[str | None] = None

    def __init__(self, code: str | None = None) -> None:
        resolved = code or self.default_code
        if resolved is None:
            raise ValueError(f"{type(self).__name__} exige um code")
        super().__init__(resolved)
        self.code = resolved


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
