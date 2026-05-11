from collections.abc import Collection
from uuid import UUID

from sqlalchemy import String, asc, cast, desc, or_, select, update

from repository.base.postgres import BasePostgresRepository
from repository.product.models.postgres import ProductORM
from repository.product.models.pydantic import ProductModel
from repository.product.translator import ProductModelTranslator


class ProductRepository(BasePostgresRepository[ProductORM, ProductModel]):
    _orm_class = ProductORM
    _translator = ProductModelTranslator()

    async def get_many(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        order_by: str | None = None,
        descending: bool = False,
    ) -> list[ProductModel]:
        safe_page = max(1, page)
        offset = (safe_page - 1) * page_size
        stmt = select(self._orm_class)
        if search and search.strip():
            pattern = f'%{search.strip()}%'
            stmt = stmt.where(
                or_(
                    ProductORM.name.ilike(pattern),
                    ProductORM.category.ilike(pattern),
                    ProductORM.manufacturer.ilike(pattern),
                    ProductORM.supplier.ilike(pattern),
                    cast(ProductORM.price, String).ilike(pattern),
                    cast(ProductORM.discount_percent, String).ilike(pattern),
                ),
            )
        column = self._order_column(order_by)
        if column is not None:
            stmt = stmt.order_by(desc(column) if descending else asc(column))
        else:
            stmt = stmt.order_by(asc(ProductORM.name))
        stmt = stmt.offset(offset).limit(page_size)
        orms = (await self._session.scalars(stmt)).all()
        return [self._translator.to_model(orm) for orm in orms]

    def _order_column(self, order_by: str | None):
        if not order_by:
            return None
        mapping = {
            'name': ProductORM.name,
            'price': ProductORM.price,
            'quantity': ProductORM.quantity,
            'category': ProductORM.category,
            'discount_percent': ProductORM.discount_percent,
            'created_at': ProductORM.created_at,
        }
        return mapping.get(order_by.strip().lower())

    async def adjust_quantity(
        self,
        product_id: UUID,
        delta: int,
    ) -> bool:
        if delta == 0:
            return True
        stmt = update(self._orm_class).where(self._orm_class.id == product_id)
        if delta < 0:
            stmt = stmt.where(self._orm_class.quantity >= -delta)
        stmt = stmt.values(quantity=self._orm_class.quantity + delta)
        result = await self._session.execute(stmt)
        return (result.rowcount or 0) > 0

    async def get_names_by_ids(self, ids: Collection[UUID]) -> dict[UUID, str]:
        id_list = list(set(ids))
        if not id_list:
            return {}
        stmt = select(self._orm_class.id, self._orm_class.name).where(self._orm_class.id.in_(id_list))
        rows = (await self._session.execute(stmt)).all()
        return {row[0]: row[1] for row in rows}
