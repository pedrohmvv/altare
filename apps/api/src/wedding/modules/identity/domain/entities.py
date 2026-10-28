from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from wedding.shared_kernel.errors import DomainRuleViolated
from wedding.shared_kernel.profile import ProfileKind


@dataclass
class User:
    id: UUID
    username: str
    profile: ProfileKind
    password_hash: str

    def __post_init__(self) -> None:
        if self.profile is ProfileKind.AMBOS:
            raise DomainRuleViolated("invalid_profile")


@dataclass
class UserSession:
    id: UUID
    user_id: UUID
    token_hash: str
    created_at: datetime
    last_seen_at: datetime
