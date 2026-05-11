from fastapi import APIRouter

from handlers.api.v1.auth import auth_router
from handlers.api.v1.order import order_router
from handlers.api.v1.product import product_router
from handlers.api.v1.user import user_router

v1_router: APIRouter = APIRouter(prefix='/v1')

v1_router.include_router(auth_router)
v1_router.include_router(order_router)
v1_router.include_router(product_router)
v1_router.include_router(user_router)

__all__ = ['v1_router']
