from collections.abc import AsyncGenerator
from pathlib import Path

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from core.config import config


def _ensure_sqlite_parent_dir(database_url: str) -> None:
    if '+aiosqlite' not in database_url:
        return
    prefix = 'sqlite+aiosqlite:///'
    if not database_url.startswith(prefix):
        return
    raw = database_url.removeprefix(prefix)
    parent = Path(raw).parent
    if parent != Path() and not parent.is_dir():
        parent.mkdir(parents=True, exist_ok=True)


_ensure_sqlite_parent_dir(config.DATABASE_URL)

engine = create_async_engine(
    config.DATABASE_URL,
    echo=bool(config.DEBUG and config.SQLALCHEMY_ECHO),
    future=True,
)


@event.listens_for(engine.sync_engine, 'connect')
def _sqlite_enable_foreign_keys(dbapi_connection, _connection_record) -> None:
    if engine.dialect.name != 'sqlite':
        return
    cursor = dbapi_connection.cursor()
    cursor.execute('PRAGMA foreign_keys=ON')
    cursor.close()


session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
