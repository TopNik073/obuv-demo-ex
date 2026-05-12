from fastapi import APIRouter

from handlers.api import api_router
from handlers.public.index import public_index_router

app_router: APIRouter = APIRouter()

app_router.include_router(api_router)
app_router.include_router(public_index_router)

ROUTERS: list[APIRouter] = [
    app_router,
]

__all__ = [
    'ROUTERS',
]
