from __future__ import annotations

from pydantic import BaseModel, Field


class AppDefinition(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    image: str = Field(..., min_length=1, max_length=200)
    command: str = Field(default="sleep 3600")
    replicas: int = Field(default=1, ge=1, le=10)
    port: int | None = Field(default=None, ge=1, le=65535)


class AppStatus(BaseModel):
    app_id: str
    name: str
    image: str
    command: str
    replicas: int
    port: int | None
    status: str
    created_at: str
    updated_at: str
    last_message: str
