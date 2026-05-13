from collections.abc import Collection
from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import asc
from sqlalchemy import desc
from sqlalchemy import or_
from sqlalchemy import select

from repository.base.session import BaseSessionRepository
from repository.user.models.orm import UserORM
from repository.user.models.pydantic import UserModel
from repository.user.translator import UserModelTranslator


class UserRepository(BaseSessionRepository[UserORM, UserModel]):
    _orm_class = UserORM
    _translator = UserModelTranslator()

    async def get_by_username(self, username: str) -> UserModel | None:
        stmt = select(UserORM).where(UserORM.username == username)
        orm = await self._session.scalar(stmt)
        return self._translator.to_model(orm) if orm else None

    async def get_many_by_ids(self, ids: Collection[UUID]) -> dict[UUID, UserModel]:
        id_list = list(set(ids))
        if not id_list:
            return {}
        stmt = select(UserORM).where(UserORM.id.in_(id_list))
        rows: Sequence[UserORM] = (await self._session.scalars(stmt)).all()
        return {orm.id: self._translator.to_model(orm) for orm in rows}

    def _order_column(self, order_by: str | None):
        if not order_by:
            return None
        mapping = {
            'username': UserORM.username,
            'created_at': UserORM.created_at,
            'role': UserORM.role,
            'name': UserORM.name,
            'surname': UserORM.surname,
        }
        return mapping.get(order_by.strip().lower())

    async def get_many(  # noqa: PLR0913
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        role: str | None = None,
        order_by: str | None = None,
        descending: bool = False,
    ) -> list[UserModel]:
        safe_page = max(1, page)
        offset = (safe_page - 1) * page_size
        stmt = select(UserORM)
        if search and search.strip():
            pattern = f'%{search.strip()}%'
            stmt = stmt.where(
                or_(
                    UserORM.username.ilike(pattern),
                    UserORM.name.ilike(pattern),
                    UserORM.surname.ilike(pattern),
                    UserORM.lastname.ilike(pattern),
                ),
            )
        if role and role.strip():
            stmt = stmt.where(UserORM.role == role.strip())
        column = self._order_column(order_by)
        if column is not None:
            stmt = stmt.order_by(desc(column) if descending else asc(column))
        else:
            stmt = stmt.order_by(asc(UserORM.username))
        stmt = stmt.offset(offset).limit(page_size)
        rows: Sequence[UserORM] = (await self._session.scalars(stmt)).all()
        return [self._translator.to_model(orm) for orm in rows]
