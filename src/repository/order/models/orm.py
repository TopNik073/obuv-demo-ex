import uuid

from decimal import Decimal

from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from repository.base.models.orm import BaseORM
from repository.base.models.orm import TimestampMixin
from repository.order.models.status import OrderStatus


class OrderORM(BaseORM, TimestampMixin):
    __tablename__ = 'orders'

    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=OrderStatus.pending.value)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal('0'))

    items: Mapped[list['OrderItemORM']] = relationship(
        back_populates='order',
        cascade='all, delete-orphan',
        lazy='selectin',
    )


class OrderItemORM(BaseORM):
    __tablename__ = 'order_items'

    order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('orders.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('products.id', ondelete='RESTRICT'),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    order: Mapped['OrderORM'] = relationship(back_populates='items')
