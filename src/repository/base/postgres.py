from collections.abc import Sequence
from typing import Annotated
from typing import TypeVar
from uuid import UUID

from fastapi import Depends
from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from repository.base import BaseModelTranslator
from repository.base.models.postgres import BaseORM
from repository.base.models.pydantic import BaseModelIdentifiable
from repository.base.repository import BaseRepository
from utils.db_connection import get_db_session

ORMType = TypeVar('ORMType', bound=BaseORM)
ModelType = TypeVar('ModelType', bound=BaseModelIdentifiable)


class BasePostgresRepository(BaseRepository[ORMType, ModelType]):
    _orm_class: type[ORMType]
    _translator: BaseModelTranslator

    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_db_session)],
    ) -> None:
        self._session: AsyncSession = session

    async def get_by_id(self, _id: UUID) -> ModelType | None:
        orm: ORMType | None = await self._session.scalar(select(self._orm_class).where(self._orm_class.id == _id))
        return self._translator.to_model(orm) if orm else None

    async def get_many(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> list[ModelType]:
        safe_page = max(1, page)
        offset = (safe_page - 1) * page_size
        stmt = select(self._orm_class).offset(offset).limit(page_size)
        result: Sequence[ORMType] = (await self._session.scalars(stmt)).all()
        return [self._translator.to_model(orm) for orm in result]

    async def create(self, entity: ModelType) -> ModelType:
        orm: ORMType = self._translator.to_db(entity)
        self._session.add(orm)
        await self._session.flush()
        await self._session.refresh(orm)
        return self._translator.to_model(orm)

    async def update(self, entity: ModelType) -> ModelType:
        orm: ORMType | None = await self._session.get(self._orm_class, entity.id)

        if not orm:
            raise ValueError(f'Entity with id {entity.id} not found')

        updated_orm: ORMType = self._translator.to_db(entity)

        for col in self._orm_class.__table__.columns:
            key = col.key
            if key == 'id':
                continue
            new_val = getattr(updated_orm, key)
            setattr(orm, key, new_val)

        return self._translator.to_model(orm)

    async def delete(self, _id: UUID) -> bool:
        result = await self._session.execute(delete(self._orm_class).where(self._orm_class.id == _id))
        return (result.rowcount or 0) > 0
