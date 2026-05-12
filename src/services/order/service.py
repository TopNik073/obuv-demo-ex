from collections.abc import Collection
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from repository.order.models.pydantic import OrderItemModel
from repository.order.models.pydantic import OrderModel
from repository.order.models.status import OrderStatus
from repository.order.repository import OrderRepository
from repository.product.repository import ProductRepository
from repository.user.models.pydantic import UserModel
from repository.user.repository import UserRepository
from services.order.models import OrderCreate
from services.order.models import OrderItemRead
from services.order.models import OrderLineCreate
from services.order.models import OrderRead
from services.order.models import OrderUpdate


class OrderService:
    def __init__(
        self,
        order_repository: Annotated[OrderRepository, Depends(OrderRepository)],
        product_repository: Annotated[ProductRepository, Depends(ProductRepository)],
        user_repository: Annotated[UserRepository, Depends(UserRepository)],
    ) -> None:
        self._orders_repository = order_repository
        self._products_repository = product_repository
        self._users_repository = user_repository

    @staticmethod
    def _consumes_inventory(status: OrderStatus) -> bool:
        return status != OrderStatus.cancelled

    @staticmethod
    def _items_to_line_creates(items: list[OrderItemModel]) -> list[OrderLineCreate]:
        return [OrderLineCreate(product_id=i.product_id, quantity=i.quantity) for i in items]

    @staticmethod
    def _customer_label(user: UserModel) -> str:
        return f'{user.full_name()} ({user.username})'

    async def _customer_labels_for_ids(self, ids: Collection[UUID]) -> dict[UUID, str]:
        unique = set(ids)
        if not unique:
            return {}
        users = await self._users_repository.get_many_by_ids(unique)
        return {uid: (OrderService._customer_label(u) if (u := users.get(uid)) else '—') for uid in unique}

    def _order_model_to_read(
        self,
        row: OrderModel,
        names: dict[UUID, str],
        customer_label: str,
    ) -> OrderRead:
        if row.id is None or row.created_at is None or row.updated_at is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Invalid order payload',
            )
        items_read = [
            OrderItemRead(
                id=i.id,  # type: ignore[arg-type]
                product_id=i.product_id,
                product_name=names.get(i.product_id, '—'),
                quantity=i.quantity,
                unit_price=i.unit_price,
            )
            for i in row.items
        ]
        return OrderRead(
            id=row.id,
            customer_id=row.customer_id,
            customer_label=customer_label,
            status=row.status,
            total_amount=row.total_amount,
            items=items_read,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    async def _release_stock_for_items(self, items: list[OrderItemModel]) -> None:
        for it in items:
            ok = await self._products_repository.adjust_quantity(it.product_id, it.quantity)
            if not ok:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f'Could not restore stock for product {it.product_id}',
                )

    async def _reserve_stock_for_items(self, items: list[OrderItemModel]) -> None:
        for it in items:
            ok = await self._products_repository.adjust_quantity(it.product_id, -it.quantity)
            if not ok:
                pr = await self._products_repository.get_by_id(it.product_id)
                label = pr.name if pr else str(it.product_id)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'Недостаточно товара «{label}» на складе (нужно {it.quantity} шт.)',
                )

    async def _ensure_stock_for_order_items(self, items: list[OrderItemModel]) -> None:
        if not items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Нельзя перевести заказ из отмены: в заказе нет позиций',
            )
        await self._ensure_stock_for_lines(self._items_to_line_creates(items))

    async def _ensure_stock_for_lines(self, lines: list[OrderLineCreate]) -> None:
        totals: dict[UUID, int] = {}
        for line in lines:
            totals[line.product_id] = totals.get(line.product_id, 0) + line.quantity
        for product_id, qty in totals.items():
            product = await self._products_repository.get_by_id(product_id)
            if product is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f'Товар не найден: {product_id}',
                )
            if qty > product.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(f'Недостаточно товара «{product.name}»: нужно {qty} шт., на складе {product.quantity}'),
                )

    async def _lines_to_domain(
        self,
        lines: list[OrderLineCreate],
    ) -> tuple[list[OrderItemModel], Decimal]:
        items: list[OrderItemModel] = []
        total = Decimal('0')
        for line in lines:
            product = await self._products_repository.get_by_id(line.product_id)
            if product is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f'Product not found: {line.product_id}',
                )
            qty = line.quantity
            unit_price = product.price
            items.append(
                OrderItemModel(
                    product_id=line.product_id,
                    quantity=qty,
                    unit_price=unit_price,
                ),
            )
            total += unit_price * qty
        return items, total

    async def list_orders(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None = None,
        sort: str | None = None,
        sort_desc: bool = False,
    ) -> list[OrderRead]:
        rows = await self._orders_repository.get_many(
            page=page,
            page_size=page_size,
            search=search,
            order_by=sort,
            descending=sort_desc,
        )
        all_ids = {i.product_id for r in rows for i in r.items}
        names = await self._products_repository.get_names_by_ids(all_ids)
        cust_labels = await self._customer_labels_for_ids(r.customer_id for r in rows)
        return [self._order_model_to_read(r, names, cust_labels.get(r.customer_id, '—')) for r in rows]

    async def get_order(self, order_id: UUID) -> OrderRead:
        row = await self._orders_repository.get_by_id(order_id)
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Order not found')
        names = await self._products_repository.get_names_by_ids(i.product_id for i in row.items)
        cust_labels = await self._customer_labels_for_ids([row.customer_id])
        return self._order_model_to_read(row, names, cust_labels.get(row.customer_id, '—'))

    async def create_order(self, data: OrderCreate) -> OrderRead:
        customer = await self._users_repository.get_by_id(data.customer_id)
        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Customer user not found',
            )
        await self._ensure_stock_for_lines(data.items)
        items, total = await self._lines_to_domain(data.items)
        await self._reserve_stock_for_items(items)
        order = OrderModel(
            customer_id=data.customer_id,
            status=OrderStatus.pending,
            total_amount=total,
            items=items,
        )
        created = await self._orders_repository.create(order)
        names = await self._products_repository.get_names_by_ids(i.product_id for i in created.items)
        return self._order_model_to_read(created, names, self._customer_label(customer))

    async def update_order(
        self,
        order_id: UUID,
        data: OrderUpdate,
    ) -> OrderRead:
        existing = await self._orders_repository.get_by_id(order_id)
        if existing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Order not found')
        customer_id = data.customer_id if data.customer_id is not None else existing.customer_id
        if data.customer_id is not None:
            customer = await self._users_repository.get_by_id(customer_id)
            if customer is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='Customer user not found',
                )
        new_status = data.status if data.status is not None else existing.status
        old_consumed = self._consumes_inventory(existing.status)
        new_consumed = self._consumes_inventory(new_status)
        uncancel = not old_consumed and new_consumed

        if data.items is not None:
            if old_consumed:
                await self._release_stock_for_items(existing.items)
            if new_consumed:
                await self._ensure_stock_for_lines(data.items)
            items, total = await self._lines_to_domain(data.items)
            if new_consumed:
                await self._reserve_stock_for_items(items)
        else:
            items = existing.items
            total = existing.total_amount
            if old_consumed and not new_consumed:
                await self._release_stock_for_items(existing.items)
            elif uncancel:
                # Отменён → ожидает/подтверждён: снова списываем остаток по строкам заказа
                await self._ensure_stock_for_order_items(existing.items)
                await self._reserve_stock_for_items(existing.items)

        if new_consumed and not items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Активный заказ должен содержать хотя бы одну товарную позицию',
            )

        updated = OrderModel(
            id=existing.id,
            customer_id=customer_id,
            status=new_status,
            total_amount=total,
            items=items,
            created_at=existing.created_at,
            updated_at=existing.updated_at,
        )
        saved = await self._orders_repository.update(updated)
        names = await self._products_repository.get_names_by_ids(i.product_id for i in saved.items)
        cust_labels = await self._customer_labels_for_ids([saved.customer_id])
        return self._order_model_to_read(saved, names, cust_labels.get(saved.customer_id, '—'))

    async def delete_all_orders_for_customer(self, customer_id: UUID) -> None:
        orders = await self._orders_repository.get_all_by_customer_id(customer_id)
        for o in orders:
            if self._consumes_inventory(o.status):
                await self._release_stock_for_items(o.items)
        await self._orders_repository.delete_orders_by_customer_id(customer_id)

    async def delete_order(self, order_id: UUID) -> None:
        existing = await self._orders_repository.get_by_id(order_id)
        if existing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Order not found')
        if self._consumes_inventory(existing.status):
            await self._release_stock_for_items(existing.items)
        deleted = await self._orders_repository.delete(order_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Order not found')
