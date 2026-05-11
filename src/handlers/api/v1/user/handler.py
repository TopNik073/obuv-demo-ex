from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from handlers.dependencies.require_roles import require_roles
from repository.user.models.pydantic import UserModel
from repository.user.models.roles import UserRole
from services.user.models import UserAdminCreate, UserAdminRead, UserAdminUpdate
from services.user.service import UserService

user_router = APIRouter(prefix='/users', tags=['users'])


def _to_admin_read(model: UserModel) -> UserAdminRead:
    return UserAdminRead.model_validate(model.model_dump(exclude={'password'}))


@user_router.get('', response_model=list[UserAdminRead])
async def list_users(  # noqa: PLR0913
    user_service: Annotated[UserService, Depends(UserService)],
    _: Annotated[UserModel, Depends(require_roles(UserRole.admin))],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=500)] = 20,
    q: str | None = None,
    role: Annotated[UserRole | None, Query(description='Фильтр по роли')] = None,
    sort: str | None = None,
    sort_desc: bool = False,
) -> list[UserAdminRead]:
    role_val = role.value if role is not None else None
    rows = await user_service.list_users(
        page=page,
        page_size=page_size,
        search=q,
        role=role_val,
        sort=sort,
        sort_desc=sort_desc,
    )
    return [_to_admin_read(m) for m in rows]


@user_router.get('/{user_id}', response_model=UserAdminRead)
async def get_user(
    user_id: UUID,
    user_service: Annotated[UserService, Depends(UserService)],
    _: Annotated[UserModel, Depends(require_roles(UserRole.admin))],
) -> UserAdminRead:
    row = await user_service.get_by_id(user_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пользователь не найден')
    return _to_admin_read(row)


@user_router.post('', response_model=UserAdminRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: UserAdminCreate,
    user_service: Annotated[UserService, Depends(UserService)],
    _: Annotated[UserModel, Depends(require_roles(UserRole.admin))],
) -> UserAdminRead:
    created = await user_service.create_user(body)
    return _to_admin_read(created)


@user_router.patch('/{user_id}', response_model=UserAdminRead)
async def update_user(
    user_id: UUID,
    body: UserAdminUpdate,
    user_service: Annotated[UserService, Depends(UserService)],
    _: Annotated[UserModel, Depends(require_roles(UserRole.admin))],
) -> UserAdminRead:
    updated = await user_service.update_user(user_id, body)
    return _to_admin_read(updated)


@user_router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    user_service: Annotated[UserService, Depends(UserService)],
    current_user: Annotated[UserModel, Depends(require_roles(UserRole.admin))],
) -> Response:
    if current_user.id is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='User id is missing')
    await user_service.delete_user(current_user.id, user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
