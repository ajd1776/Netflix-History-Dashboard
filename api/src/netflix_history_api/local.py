"""Run the dashboard on this machine only.

The server binds to 127.0.0.1, so nothing outside the computer can reach it.
"""

from __future__ import annotations

import socket
import threading
import time
import webbrowser

import uvicorn

from .app import WEB_DIST, app

HOST = "127.0.0.1"


def free_port() -> int:
    with socket.socket() as s:
        s.bind((HOST, 0))
        return s.getsockname()[1]


def start_in_background(port: int | None = None) -> tuple[uvicorn.Server, str]:
    """Start the server on a thread and return once it's accepting requests."""
    port = port or free_port()
    server = uvicorn.Server(uvicorn.Config(app, host=HOST, port=port, log_level="warning"))
    threading.Thread(target=server.run, daemon=True).start()
    while not server.started:
        time.sleep(0.02)
    return server, f"http://{HOST}:{port}/"


def main() -> None:
    """`netflix-history`: serve the built app locally and open it in the browser."""
    if not WEB_DIST.is_dir():
        raise SystemExit("Build the web app first: npm run build")
    server, url = start_in_background()
    print(f"Netflix History is running at {url}  (Ctrl+C to stop)")
    webbrowser.open(url)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.should_exit = True
