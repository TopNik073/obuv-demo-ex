from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

from repository.order.models.status import OrderStatus


class OrderLineCreate(BaseModel):
    product_id: UUID
    quantity: int = Field(ge=1)


class OrderCreate(BaseModel):
    customer_id: UUID
    items: list[OrderLineCreate] = Field(min_length=1)


class OrderUpdate(BaseModel):
    status: OrderStatus | None = None
    customer_id: UUID | None = None
    items: list[OrderLineCreate] | None = None


class OrderItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID
    product_name: str
    quantity: int
    unit_price: Decimal


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    customer_id: UUID
    customer_label: str
    status: OrderStatus
    total_amount: Decimal
    items: list[OrderItemRead]
    created_at: datetime
    updated_at: datetime
