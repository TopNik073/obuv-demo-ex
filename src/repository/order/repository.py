from uuid import UUID

from sqlalchemy import String
from sqlalchemy import asc
from sqlalchemy import cast
from sqlalchemy import delete
from sqlalchemy import desc
from sqlalchemy import func
from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from repository.base.session import BaseSessionRepository
from repository.order.models.orm import OrderItemORM
from repository.order.models.orm import OrderORM
from repository.order.models.pydantic import OrderModel
from repository.order.translator import OrderModelTranslator
from repository.user.models.orm import UserORM


class OrderRepository(BaseSessionRepository[OrderORM, OrderModel]):
    _orm_class = OrderORM
    _translator = OrderModelTranslator()

    async def get_by_id(self, _id: UUID) -> OrderModel | None:
        stmt = select(OrderORM).where(OrderORM.id == _id).options(selectinload(OrderORM.items))
        orm = await self._session.scalar(stmt)
        return self._translator.to_model(orm) if orm else None

    async def get_all_by_customer_id(self, customer_id: UUID) -> list[OrderModel]:
        stmt = select(OrderORM).where(OrderORM.customer_id == customer_id).options(selectinload(OrderORM.items))
        rows = (await self._session.scalars(stmt)).all()
        return [self._translator.to_model(orm) for orm in rows]

    def _order_column(self, order_by: str | None):
        if not order_by:
            return None
        mapping = {
            'created_at': OrderORM.created_at,
            'total_amount': OrderORM.total_amount,
            'status': OrderORM.status,
            'customer': UserORM.username,
        }
        return mapping.get(order_by.strip().lower())

    async def get_many(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        order_by: str | None = None,
        descending: bool = False,
    ) -> list[OrderModel]:
        safe_page = max(1, page)
        offset = (safe_page - 1) * page_size
        stmt = select(OrderORM).join(UserORM, OrderORM.customer_id == UserORM.id).options(selectinload(OrderORM.items))
        if search and search.strip():
            pattern = f'%{search.strip()}%'
            stmt = stmt.where(
                or_(
                    OrderORM.status.ilike(pattern),
                    cast(OrderORM.total_amount, String).ilike(pattern),
                    cast(OrderORM.id, String).ilike(pattern),
                    cast(OrderORM.customer_id, String).ilike(pattern),
                    UserORM.username.ilike(pattern),
                    UserORM.name.ilike(pattern),
                    UserORM.surname.ilike(pattern),
                    UserORM.lastname.ilike(pattern),
                ),
            )
        column = self._order_column(order_by)
        if column is not None:
            stmt = stmt.order_by(desc(column) if descending else asc(column))
        else:
            stmt = stmt.order_by(desc(OrderORM.created_at))
        stmt = stmt.offset(offset).limit(page_size)
        rows = (await self._session.scalars(stmt)).all()
        return [self._translator.to_model(orm) for orm in rows]

    async def create(self, entity: OrderModel) -> OrderModel:
        orm = self._translator.to_db(entity)
        self._session.add(orm)
        await self._session.flush()
        await self._session.refresh(orm, attribute_names=['items'])
        return self._translator.to_model(orm)

    async def update(self, entity: OrderModel) -> OrderModel:
        if entity.id is None:
            raise ValueError('Order id is required for update')
        stmt = select(OrderORM).where(OrderORM.id == entity.id).options(selectinload(OrderORM.items))
        orm = await self._session.scalar(stmt)
        if orm is None:
            raise ValueError(f'Order {entity.id} not found')
        orm.customer_id = entity.customer_id
        orm.status = entity.status.value
        orm.total_amount = entity.total_amount
        orm.items.clear()
        for item in entity.items:
            orm.items.append(
                OrderItemORM(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                ),
            )
        await self._session.flush()
        await self._session.refresh(orm, attribute_names=['items'])
        return self._translator.to_model(orm)

    async def delete_orders_by_customer_id(self, customer_id: UUID) -> None:
        await self._session.execute(delete(OrderORM).where(OrderORM.customer_id == customer_id))

    async def remove_line_items_for_product(self, product_id: UUID) -> None:
        stmt = select(OrderItemORM.order_id).where(OrderItemORM.product_id == product_id)
        order_ids = list(set((await self._session.scalars(stmt)).all()))
        await self._session.execute(delete(OrderItemORM).where(OrderItemORM.product_id == product_id))
        for oid in order_ids:
            cnt = await self._session.scalar(
                select(func.count()).select_from(OrderItemORM).where(OrderItemORM.order_id == oid)
            )
            if cnt == 0:
                await self._session.execute(delete(OrderORM).where(OrderORM.id == oid))
            else:
                stmt_items = select(OrderItemORM).where(OrderItemORM.order_id == oid)
                items = (await self._session.scalars(stmt_items)).all()
                total = sum(i.quantity * i.unit_price for i in items)
                orm = await self._session.get(OrderORM, oid)
                if orm is not None:
                    orm.total_amount = total
