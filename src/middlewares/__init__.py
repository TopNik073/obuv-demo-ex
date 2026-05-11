from starlette.middleware.base import BaseHTTPMiddleware

from middlewares.logging_middleware import RequestLoggingMiddleware

MIDDLEWARES: list[type[BaseHTTPMiddleware]] = [
    RequestLoggingMiddleware,
]

__all__ = [
    'MIDDLEWARES',
]
