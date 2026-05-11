from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile, status

from handlers.dependencies.get_optional_user import get_optional_user
from handlers.dependencies.require_roles import require_roles
from repository.user.models.pydantic import UserModel
from repository.user.models.roles import UserRole
from services.product.models import ProductCreate, ProductImportResult, ProductRead, ProductUpdate
from services.product.service import ProductService

product_router = APIRouter(prefix='/products', tags=['products'])


@product_router.get('', response_model=list[ProductRead])
async def list_products(  # noqa: PLR0913
    product_service: Annotated[ProductService, Depends(ProductService)],
    optional_user: Annotated[UserModel | None, Depends(get_optional_user)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=500)] = 20,
    q: str | None = None,
    sort: str | None = None,
    sort_desc: bool = False,
) -> list[ProductRead]:
    rows = await product_service.list_products(
        optional_user,
        page=page,
        page_size=page_size,
        search=q,
        sort=sort,
        sort_desc=sort_desc,
    )
    return [ProductRead.model_validate(p) for p in rows]


@product_router.post('/import', response_model=ProductImportResult)
async def import_products_csv(
    product_service: Annotated[ProductService, Depends(ProductService)],
    _: Annotated[UserModel, Depends(require_roles(UserRole.admin))],
    file: Annotated[UploadFile, File(description='CSV UTF-8')],
) -> ProductImportResult:
    raw = await file.read()
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Файл должен быть в кодировке UTF-8',
        ) from exc
    created = await product_service.import_products_csv(text)
    return ProductImportResult(created=created)


@product_router.get('/{product_id}', response_model=ProductRead)
async def get_product(
    product_id: UUID,
    product_service: Annotated[ProductService, Depends(ProductService)],
) -> ProductRead:
    row = await product_service.get_product(product_id)
    return ProductRead.model_validate(row)


@product_router.post('', response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(
    body: ProductCreate,
    product_service: Annotated[ProductService, Depends(ProductService)],
    _: Annotated[UserModel, Depends(require_roles(UserRole.admin))],
) -> ProductRead:
    row = await product_service.create_product(body)
    return ProductRead.model_validate(row)


@product_router.patch('/{product_id}', response_model=ProductRead)
async def update_product(
    product_id: UUID,
    body: ProductUpdate,
    product_service: Annotated[ProductService, Depends(ProductService)],
    _: Annotated[UserModel, Depends(require_roles(UserRole.admin))],
) -> ProductRead:
    row = await product_service.update_product(product_id, body)
    return ProductRead.model_validate(row)


@product_router.delete('/{product_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: UUID,
    product_service: Annotated[ProductService, Depends(ProductService)],
    _: Annotated[UserModel, Depends(require_roles(UserRole.admin))],
) -> Response:
    await product_service.delete_product(product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
