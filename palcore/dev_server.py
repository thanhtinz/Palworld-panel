"""Dependency-free PALCORE panel server for local development.

Run with:
    python -m palcore.dev_server
"""

from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .domain import build_dashboard_state, build_demo_servers, build_event_topics, to_jsonable

STATIC_DIR = Path(__file__).with_name("static")
CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
}


class PalcoreRequestHandler(BaseHTTPRequestHandler):
    """Small stdlib HTTP handler for the bundled panel and demo API."""

    server_version = "PALCOREPanel/0.2"

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler naming
        path = urlparse(self.path).path
        if path == "/":
            self._send_file(STATIC_DIR / "index.html")
        elif path == "/health":
            self._send_json({"status": "ok", "service": "palcore-dev-server"})
        elif path == "/api/v1/dashboard":
            state = build_dashboard_state()
            self._send_json({"totals": state.totals(), "state": to_jsonable(state)})
        elif path == "/api/v1/modules":
            self._send_json(to_jsonable(build_dashboard_state().modules))
        elif path == "/api/v1/servers":
            self._send_json(to_jsonable(build_demo_servers()))
        elif path == "/api/v1/events/schema":
            self._send_json(
                {
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
            )
        elif path.startswith("/static/"):
            self._send_file(STATIC_DIR / path.removeprefix("/static/"))
        else:
            self._send_json({"detail": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args: object) -> None:
        """Keep local server logs compact and recognizable."""

        print(f"[palcore] {self.address_string()} - {format % args}")

    def _send_json(self, payload: object, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path) -> None:
        resolved = path.resolve()
        static_root = STATIC_DIR.resolve()
        if static_root not in resolved.parents and resolved != static_root:
            self._send_json({"detail": "Forbidden"}, status=HTTPStatus.FORBIDDEN)
            return
        if not resolved.is_file():
            self._send_json({"detail": "Not found"}, status=HTTPStatus.NOT_FOUND)
            return
        body = resolved.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", CONTENT_TYPES.get(resolved.suffix, "application/octet-stream"))
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Run the dependency-free PALCORE panel server."""

    server = ThreadingHTTPServer((host, port), PalcoreRequestHandler)
    print(f"PALCORE panel running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
