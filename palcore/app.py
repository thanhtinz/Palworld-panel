"""FastAPI entrypoint for the PALCORE control-plane and web panel."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .domain import EventEnvelope, build_dashboard_state, build_demo_servers, build_event_topics, to_jsonable

STATIC_DIR = Path(__file__).with_name("static")


def create_app():
    """Create the optional FastAPI application.

    The framework-free domain package and ``python -m palcore.dev_server`` remain
    available for environments that do not install the API extra.
    """

    app = FastAPI(
        title="PALCORE API",
        version="0.2.0",
        summary="Advanced Palworld server platform and mod ecosystem API.",
    )

    @app.get("/", include_in_schema=False)
    def panel() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "palcore-api"}

    @app.get("/api/v1/dashboard", tags=["platform"])
    def dashboard() -> dict[str, Any]:
        state = build_dashboard_state()
        return to_jsonable({"totals": state.totals(), "state": state})

    @app.get("/api/v1/modules", tags=["platform"])
    def modules() -> list[dict[str, Any]]:
        return to_jsonable(build_dashboard_state().modules)

    @app.get("/api/v1/servers", tags=["servers"])
    def servers() -> list[dict[str, Any]]:
        return to_jsonable(build_demo_servers())

    @app.get("/api/v1/events/schema", tags=["realtime"])
    def event_schema() -> dict[str, Any]:
        return {
            "transport": "websocket",
            "endpoint": "/ws/realtime",
            "topics": list(build_event_topics()),
            "envelope": {
                "event_id": "uuid",
                "topic": "string",
                "server_id": "uuid",
                "occurred_at": "iso-8601 datetime",
                "payload": "object",
            },
        }

    @app.websocket("/ws/realtime")
    async def realtime(websocket: WebSocket) -> None:
        await websocket.accept()
        demo_server = build_demo_servers()[0]
        await websocket.send_json(
            EventEnvelope(
                topic="server.health",
                server_id=demo_server.server_id,
                payload={
                    "name": demo_server.name,
                    "status": demo_server.status.value,
                    "online_players": demo_server.online_players,
                    "health_score": demo_server.health_score(),
                },
            ).to_wire()
        )
        await websocket.close()

    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    return app
