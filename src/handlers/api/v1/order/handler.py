from typing import Annotated
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from fastapi import Response
from fastapi import status

from handlers.dependencies.require_roles import require_roles
from repository.user.models.pydantic import UserModel
from repository.user.models.roles import UserRole
from services.order.models import OrderCreate
from services.order.models import OrderRead
from services.order.models import OrderUpdate
from services.order.service import OrderService

order_router = APIRouter(prefix='/orders', tags=['orders'])


@order_router.get('', response_model=list[OrderRead])
async def list_orders(  # noqa: PLR0913
    order_service: Annotated[OrderService, Depends(OrderService)],
    _: Annotated[UserModel, Depends(require_roles(UserRole.manager, UserRole.admin))],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=500)] = 20,
    q: str | None = None,
    sort: str | None = None,
    sort_desc: bool = False,
) -> list[OrderRead]:
    return await order_service.list_orders(
        page=page,
        page_size=page_size,
        search=q,
        sort=sort,
        sort_desc=sort_desc,
    )


@order_router.get('/{order_id}', response_model=OrderRead)
async def get_order(
    order_id: UUID,
    order_service: Annotated[OrderService, Depends(OrderService)],
    _: Annotated[UserModel, Depends(require_roles(UserRole.manager, UserRole.admin))],
) -> OrderRead:
    return await order_service.get_order(order_id)


@order_router.post('', response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def create_order(
    body: OrderCreate,
    order_service: Annotated[OrderService, Depends(OrderService)],
    _: Annotated[UserModel, Depends(require_roles(UserRole.admin))],
) -> OrderRead:
    return await order_service.create_order(body)


@order_router.patch('/{order_id}', response_model=OrderRead)
async def update_order(
    order_id: UUID,
    body: OrderUpdate,
    order_service: Annotated[OrderService, Depends(OrderService)],
    _: Annotated[UserModel, Depends(require_roles(UserRole.admin))],
) -> OrderRead:
    return await order_service.update_order(order_id, body)


@order_router.delete('/{order_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: UUID,
    order_service: Annotated[OrderService, Depends(OrderService)],
    _: Annotated[UserModel, Depends(require_roles(UserRole.admin))],
) -> Response:
    await order_service.delete_order(order_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
