import socket
import threading
import time
from pathlib import Path

import uvicorn
import webview

from main_app import app

from core.config import config as app_config

APP_HOST = app_config.APP_HOST
APP_PORT = app_config.APP_PORT

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_WEBVIEW_STORAGE = Path.home() / '.obuv-demo-ex' / 'webview'
_APP_ICON = _PROJECT_ROOT / 'static' / 'icon.png'


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
    icon_arg = str(_APP_ICON) if _APP_ICON.is_file() else None
    webview.start(
        private_mode=False,
        storage_path=str(_WEBVIEW_STORAGE),
        icon=icon_arg,
    )
    server.should_exit = True
    thread.join(timeout=5.0)


if __name__ == '__main__':
    main()
