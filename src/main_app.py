"""ASGI application for Uvicorn / PyWebview."""

from app_factory import AppFactory
from core.config import config
from handlers import ROUTERS
from middlewares import MIDDLEWARES

_factory = AppFactory(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    debug=config.DEBUG,
    routers=ROUTERS,
    middlewares=MIDDLEWARES,
)

app = _factory.app
