from decimal import Decimal

from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from repository.base.models.postgres import BaseORM
from repository.base.models.postgres import TimestampMixin


class ProductORM(BaseORM, TimestampMixin):
    __tablename__ = 'products'

    name: Mapped[str] = mapped_column(String(), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(default=0, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(), nullable=True)
    category: Mapped[str | None] = mapped_column(String(), nullable=True)
    manufacturer: Mapped[str | None] = mapped_column(String(), nullable=True)
    supplier: Mapped[str | None] = mapped_column(String(), nullable=True)
    unit: Mapped[str | None] = mapped_column(String(), nullable=True)
    discount_percent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    base_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
