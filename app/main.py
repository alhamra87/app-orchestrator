from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone

import redis.asyncio as redis

from app.schemas import AppDefinition, AppStatus


class AppOrchestrator:
    def __init__(self, redis_url: str | None = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.client = redis.Redis.from_url(self.redis_url, decode_responses=True)

    async def register_app(self, definition: AppDefinition) -> AppStatus:
        app_id = str(uuid.uuid4())
        now = self._utc_now()
        data = {
            "app_id": app_id,
            "name": definition.name,
            "image": definition.image,
            "command": definition.command,
            "replicas": definition.replicas,
            "port": definition.port,
            "status": "registered",
            "created_at": now,
            "updated_at": now,
            "last_message": "Application registered and awaiting start.",
        }
        await self.client.set(f"app:{app_id}", json.dumps(data))
        return AppStatus(**data)

    async def list_apps(self) -> list[AppStatus]:
        keys = await self.client.keys("app:*")
        apps: list[AppStatus] = []
        for key in keys:
            raw = await self.client.get(key)
            if raw:
                apps.append(AppStatus(**json.loads(raw)))
        return sorted(apps, key=lambda item: item.created_at)

    async def get_app(self, app_id: str) -> AppStatus | None:
        raw = await self.client.get(f"app:{app_id}")
        if not raw:
            return None
        return AppStatus(**json.loads(raw))

    async def start_app(self, app_id: str) -> AppStatus:
        app = await self.get_app(app_id)
        if app is None:
            raise ValueError("Application not found")

        updated = app.model_dump()
        updated["status"] = "starting"
        updated["updated_at"] = self._utc_now()
        updated["last_message"] = "Application startup initiated."
        await self.client.set(f"app:{app_id}", json.dumps(updated))

        await self._set_status_after_delay(app_id, "running", "Application started successfully.")

        return AppStatus(**await self._load_raw(app_id))

    async def stop_app(self, app_id: str) -> AppStatus:
        app = await self.get_app(app_id)
        if app is None:
            raise ValueError("Application not found")

        updated = app.model_dump()
        updated["status"] = "stopping"
        updated["updated_at"] = self._utc_now()
        updated["last_message"] = "Application stop requested."
        await self.client.set(f"app:{app_id}", json.dumps(updated))

        await self._set_status_after_delay(app_id, "stopped", "Application stopped successfully.")

        return AppStatus(**await self._load_raw(app_id))

    async def _set_status_after_delay(self, app_id: str, status: str, message: str) -> None:
        import asyncio
        await asyncio.sleep(1)
        raw = await self.client.get(f"app:{app_id}")
        if not raw:
            return
        app_data = json.loads(raw)
        app_data["status"] = status
        app_data["updated_at"] = self._utc_now()
        app_data["last_message"] = message
        await self.client.set(f"app:{app_id}", json.dumps(app_data))

    async def _load_raw(self, app_id: str) -> dict:
        raw = await self.client.get(f"app:{app_id}")
        if not raw:
            raise ValueError("Application not found")
        return json.loads(raw)

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
