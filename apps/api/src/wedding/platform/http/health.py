from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthOut(BaseModel):
    status: Literal["ok"]


@router.get("/health", operation_id="health_check", tags=["health"])
def health_check() -> HealthOut:
    return HealthOut(status="ok")
