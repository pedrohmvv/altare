from dataclasses import dataclass
from uuid import UUID

from wedding.shared_kernel.profile import ProfileKind


@dataclass(frozen=True)
class CurrentUser:
    user_id: UUID
    username: str
    profile: ProfileKind


@dataclass(frozen=True)
class LoginResult:
    token: str
    user: CurrentUser
