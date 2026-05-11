from decimal import Decimal

from repository.base.models import BaseModelIdentifiable
from repository.base.models import TimestampedModelMixin


class ProductModel(BaseModelIdentifiable, TimestampedModelMixin):
    name: str
    description: str | None = None
    price: Decimal
    quantity: int
    image_url: str | None = None
    category: str | None = None
    manufacturer: str | None = None
    supplier: str | None = None
    unit: str | None = None
    discount_percent: int = 0
    base_price: Decimal | None = None
