from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from wedding.shared_kernel.profile import ProfileKind


class LoginIn(BaseModel):
    # Só limites de tamanho contra abuso: a política de usuário e de senha vale na criação, e
    # mostrá-la aqui diria a quem erra o que uma conta pode ter.
    username: str = Field(min_length=1, max_length=256)
    password: str = Field(min_length=1, max_length=1024)


class CurrentUserOut(BaseModel):
    user_id: UUID
    username: str
    profile: Literal[ProfileKind.NOIVO, ProfileKind.NOIVA]
