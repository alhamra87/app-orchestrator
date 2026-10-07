# app-orchestrator

A small application orchestrator built with Python, FastAPI, Docker, and Redis.

Features:
- register apps
- list and inspect apps
- start and stop apps
- store state in Redis
- simple health endpoint
- Docker Compose setup for local development

## Architecture

- FastAPI API: exposes orchestration endpoints
- Redis: stores app state and metadata
- Docker Compose: runs the API and Redis together

## Run locally with Docker Compose

```bash
docker compose up --build
```

Then open:
- http://localhost:8000/docs

## API overview

- GET /health
- POST /apps
- GET /apps
- GET /apps/{app_id}
- POST /apps/{app_id}/start
- POST /apps/{app_id}/stop

## Example request

```bash
curl -X POST http://localhost:8000/apps \
  -H "Content-Type: application/json" \
  -d '{
    "name": "api-service",
    "image": "nginx:latest",
    "command": "nginx -g 'daemon off;'",
    "replicas": 1,
    "port": 8080
  }'
```

This project is intentionally lightweight and is designed as a foundation for a larger orchestrator system.
