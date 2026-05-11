from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from repository.base.models import BaseModelIdentifiable, TimestampedModelMixin
from repository.order.models.status import OrderStatus


class OrderItemModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID | None = None
    product_id: UUID
    quantity: int
    unit_price: Decimal


class OrderModel(BaseModelIdentifiable, TimestampedModelMixin):
    customer_id: UUID
    status: OrderStatus
    total_amount: Decimal
    items: list[OrderItemModel]
