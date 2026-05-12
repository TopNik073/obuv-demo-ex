import csv

from decimal import Decimal
from decimal import InvalidOperation
from io import StringIO
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from repository.order.repository import OrderRepository
from repository.product.models.pydantic import ProductModel
from repository.product.repository import ProductRepository
from repository.user.models.pydantic import UserModel
from repository.user.models.roles import UserRole
from services.product.models import DISCOUNT_PERCENT_MAX
from services.product.models import ProductCreate
from services.product.models import ProductUpdate


class ProductService:
    def __init__(
        self,
        product_repository: Annotated[ProductRepository, Depends(ProductRepository)],
        order_repository: Annotated[OrderRepository, Depends(OrderRepository)],
    ) -> None:
        self._products_repository = product_repository
        self._orders_repository = order_repository

    def _ensure_filters_allowed(self, user: UserModel | None) -> bool:
        return user is not None and user.role in (UserRole.manager, UserRole.admin)

    @staticmethod
    def _validate_product_row(model: ProductModel) -> None:
        if model.discount_percent < 0 or model.discount_percent > DISCOUNT_PERCENT_MAX:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Скидка должна быть от 0 до 100 процентов',
            )
        if model.base_price is not None and model.base_price < model.price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Базовая цена не может быть ниже текущей цены продажи',
            )

    async def list_products(  # noqa: PLR0913
        self,
        user: UserModel | None,
        *,
        page: int,
        page_size: int,
        search: str | None,
        sort: str | None,
        sort_desc: bool,
    ) -> list[ProductModel]:
        wants_filters = bool((search or '').strip()) or bool((sort or '').strip())
        if wants_filters and not self._ensure_filters_allowed(user):
            wants_filters = False

        return await self._products_repository.get_many(
            page=page,
            page_size=page_size,
            search=search if wants_filters else None,
            order_by=sort if wants_filters else None,
            descending=sort_desc if wants_filters else False,
        )

    async def get_product(self, product_id: UUID) -> ProductModel:
        entity = await self._products_repository.get_by_id(product_id)
        if entity is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found')
        return entity

    async def create_product(self, data: ProductCreate) -> ProductModel:
        model = ProductModel(
            name=data.name,
            description=data.description,
            price=data.price,
            quantity=data.quantity,
            image_url=data.image_url,
            category=data.category,
            manufacturer=data.manufacturer,
            supplier=data.supplier,
            unit=data.unit,
            discount_percent=data.discount_percent,
            base_price=data.base_price,
        )
        self._validate_product_row(model)
        return await self._products_repository.create(model)

    async def update_product(
        self,
        product_id: UUID,
        data: ProductUpdate,
    ) -> ProductModel:
        existing = await self._products_repository.get_by_id(product_id)
        if existing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found')
        patch = data.model_dump(exclude_unset=True)
        merged = existing.model_copy(update=patch)
        self._validate_product_row(merged)
        return await self._products_repository.update(merged)

    async def delete_product(self, product_id: UUID) -> None:
        existing = await self._products_repository.get_by_id(product_id)
        if existing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found')
        await self._orders_repository.remove_line_items_for_product(product_id)
        deleted = await self._products_repository.delete(product_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found')

    @staticmethod
    def _empty_to_none(value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped if stripped else None

    @staticmethod
    def _parse_decimal_cell(value: str) -> Decimal:
        text = value.strip().replace(',', '.')
        if not text:
            msg = 'Пустая цена'
            raise ValueError(msg)
        return Decimal(text)

    @staticmethod
    def _parse_optional_decimal(value: str) -> Decimal | None:
        text = value.strip().replace(',', '.')
        if not text:
            return None
        return Decimal(text)

    @staticmethod
    def _parse_int_cell(value: str, default: int = 0) -> int:
        text = value.strip()
        if not text:
            return default
        return int(float(text))

    async def import_products_csv(self, text: str) -> int:
        stream = StringIO(text)
        reader = csv.DictReader(stream)
        if not reader.fieldnames:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Нет строки заголовка колонок в CSV',
            )
        created = 0
        for raw in reader:
            row = {(k or '').strip().lower(): (v if v is not None else '') for k, v in raw.items()}
            name = (row.get('name') or '').strip()
            if not name:
                continue
            try:
                price = self._parse_decimal_cell(row.get('price', ''))
                qty = self._parse_int_cell(row.get('quantity', ''), 0)
                discount = self._parse_int_cell(row.get('discount_percent', ''), 0)
                base_raw = row.get('base_price', '')
                base_price = self._parse_optional_decimal(base_raw) if base_raw else None
                pc = ProductCreate(
                    name=name,
                    description=self._empty_to_none(row.get('description', '')),
                    price=price,
                    quantity=qty,
                    image_url=self._empty_to_none(row.get('image_url', '')),
                    category=self._empty_to_none(row.get('category', '')),
                    manufacturer=self._empty_to_none(row.get('manufacturer', '')),
                    supplier=self._empty_to_none(row.get('supplier', '')),
                    unit=self._empty_to_none(row.get('unit', '')),
                    discount_percent=discount,
                    base_price=base_price,
                )
            except (ValueError, InvalidOperation) as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'Ошибка в строке CSV для «{name}»: {exc}',
                ) from exc
            model = ProductModel(
                name=pc.name,
                description=pc.description,
                price=pc.price,
                quantity=pc.quantity,
                image_url=pc.image_url,
                category=pc.category,
                manufacturer=pc.manufacturer,
                supplier=pc.supplier,
                unit=pc.unit,
                discount_percent=pc.discount_percent,
                base_price=pc.base_price,
            )
            self._validate_product_row(model)
            await self._products_repository.create(model)
            created += 1
        return created
