import socket
import sys
import threading
import time

from pathlib import Path

import uvicorn
import webview

from core.config import config as app_config
from core.paths import bundle_root
from main_app import app
from utils.db_migrate import run_migrations

APP_HOST = app_config.APP_HOST
APP_PORT = app_config.APP_PORT

_WEBVIEW_STORAGE = Path.home() / '.obuv-demo-ex' / 'webview'


def _webview_icon_path() -> str | None:
    static_dir = bundle_root() / 'static'
    for name in ('logo.ico', 'icon.ico'):
        path = static_dir / name
        if path.is_file():
            return str(path)
    png = static_dir / 'icon.png'
    if sys.platform == 'win32':
        return None
    if png.is_file():
        return str(png)
    return None


def _wait_for_tcp(
    host: str,
    port: int,
    timeout_seconds: float = 15.0,
) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.3):
                return
        except OSError:
            time.sleep(0.05)
    msg = f'Server did not become ready on {host}:{port} within {timeout_seconds}s'
    raise RuntimeError(msg)


def main() -> None:
    run_migrations()
    uvicorn_cfg = uvicorn.Config(
        app,
        host=APP_HOST,
        port=APP_PORT,
        log_level='warning',
    )
    server = uvicorn.Server(uvicorn_cfg)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    _wait_for_tcp(APP_HOST, APP_PORT)

    window = webview.create_window(
        'Обувь — склад',
        url=f'http://{APP_HOST}:{APP_PORT}/',
        width=1440,
        height=900,
    )

    def on_closed() -> None:
        server.should_exit = True

    window.events.closed += on_closed
    _WEBVIEW_STORAGE.mkdir(parents=True, exist_ok=True)
    icon_arg = _webview_icon_path()
    webview.start(
        private_mode=False,
        storage_path=str(_WEBVIEW_STORAGE),
        icon=icon_arg,
    )
    server.should_exit = True
    thread.join(timeout=5.0)


if __name__ == '__main__':
    main()
