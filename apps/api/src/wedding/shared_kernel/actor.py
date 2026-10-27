from dataclasses import dataclass
from uuid import UUID

from wedding.shared_kernel.profile import ProfileKind


@dataclass(frozen=True, slots=True)
class Actor:
    """Quem age, sempre montado da sessão e nunca de um campo enviado pelo cliente."""

    user_id: UUID
    profile: ProfileKind

    def __post_init__(self) -> None:
        if self.profile is ProfileKind.AMBOS:
            raise ValueError("Ambos não é um perfil de login")
