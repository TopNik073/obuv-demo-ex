from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status

from services.order.service import OrderService
from repository.user.models.pydantic import UserModel
from repository.user.repository import UserRepository
from services.security.service import SecurityService
from services.user.models import UserAdminCreate, UserAdminUpdate


class UserService:
    def __init__(
        self,
        user_repository: Annotated[UserRepository, Depends(UserRepository)],
        order_service: Annotated[OrderService, Depends(OrderService)],
    ) -> None:
        self._users = user_repository
        self._orders = order_service

    async def get_by_id(self, user_id: UUID) -> UserModel | None:
        return await self._users.get_by_id(user_id)

    async def list_users(  # noqa: PLR0913
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        role: str | None = None,
        sort: str | None = None,
        sort_desc: bool = False,
    ) -> list[UserModel]:
        return await self._users.get_many(
            page=page,
            page_size=page_size,
            search=search,
            role=role,
            order_by=sort,
            descending=sort_desc,
        )

    async def create_user(self, data: UserAdminCreate) -> UserModel:
        existing = await self._users.get_by_username(data.username)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Логин уже занят',
            )
        user = UserModel(
            username=data.username,
            password=SecurityService.hash_password(data.password),
            name=data.name,
            surname=data.surname,
            lastname=data.lastname,
            role=data.role,
        )
        return await self._users.create(user)

    async def update_user(
        self,
        user_id: UUID,
        data: UserAdminUpdate,
    ) -> UserModel:
        existing = await self._users.get_by_id(user_id)
        if existing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пользователь не найден')
        patch = data.model_dump(exclude_unset=True)
        if 'username' in patch and patch['username'] != existing.username:
            taken = await self._users.get_by_username(patch['username'])
            if taken is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail='Логин уже занят',
                )
        if 'password' in patch and patch['password'] is not None:
            patch['password'] = SecurityService.hash_password(patch['password'])
        merged = existing.model_copy(update=patch)
        return await self._users.update(merged)

    async def delete_user(
        self,
        actor_id: UUID,
        target_id: UUID,
    ) -> None:
        if actor_id == target_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Нельзя удалить собственную учётную запись',
            )
        target = await self._users.get_by_id(target_id)
        if target is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пользователь не найден')
        await self._orders.delete_all_orders_for_customer(target_id)
        deleted = await self._users.delete(target_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пользователь не найден')
