from __future__ import annotations

from fastapi import FastAPI, HTTPException

from app.orchestrator import AppOrchestrator
from app.schemas import AppDefinition

app = FastAPI(title="Application Orchestrator", version="0.1.0")
orchestrator = AppOrchestrator()


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok"}


@app.post("/apps")
async def register_app(definition: AppDefinition):
    return await orchestrator.register_app(definition)


@app.get("/apps")
async def list_apps():
    return await orchestrator.list_apps()


@app.get("/apps/{app_id}")
async def get_app(app_id: str):
    app = await orchestrator.get_app(app_id)
    if app is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


@app.post("/apps/{app_id}/start")
async def start_app(app_id: str):
    try:
        return await orchestrator.start_app(app_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/apps/{app_id}/stop")
async def stop_app(app_id: str):
    try:
        return await orchestrator.stop_app(app_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
