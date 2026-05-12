from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import field_validator
from pydantic import model_validator

DISCOUNT_PERCENT_MAX = 100


class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: Decimal
    quantity: int = 0
    image_url: str | None = None
    category: str | None = None
    manufacturer: str | None = None
    supplier: str | None = None
    unit: str | None = None
    discount_percent: int = 0
    base_price: Decimal | None = None

    @field_validator('discount_percent')
    @classmethod
    def discount_range(cls, v: int) -> int:
        if v < 0 or v > DISCOUNT_PERCENT_MAX:
            msg = 'Скидка должна быть от 0 до 100 процентов'
            raise ValueError(msg)
        return v

    @model_validator(mode='after')
    def base_vs_price(self) -> 'ProductCreate':
        if self.base_price is not None and self.base_price < self.price:
            msg = 'Базовая цена не может быть ниже текущей цены продажи'
            raise ValueError(msg)
        return self


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: Decimal | None = None
    quantity: int | None = None
    image_url: str | None = None
    category: str | None = None
    manufacturer: str | None = None
    supplier: str | None = None
    unit: str | None = None
    discount_percent: int | None = None
    base_price: Decimal | None = None

    @field_validator('discount_percent')
    @classmethod
    def discount_range(cls, v: int | None) -> int | None:
        if v is None:
            return v
        if v < 0 or v > DISCOUNT_PERCENT_MAX:
            msg = 'Скидка должна быть от 0 до 100 процентов'
            raise ValueError(msg)
        return v


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    price: Decimal
    quantity: int
    image_url: str | None
    category: str | None
    manufacturer: str | None
    supplier: str | None
    unit: str | None
    discount_percent: int
    base_price: Decimal | None


class ProductImportResult(BaseModel):
    created: int
