from core.config import config
from repository.user.models.postgres import UserORM
from repository.user.models.roles import UserRole
from repository.user.repository import UserRepository
from services.security.service import SecurityService
from utils.db_connection import session_factory


async def seed_admin() -> None:
    async with session_factory() as session:
        repo = UserRepository(session)
        if await repo.get_by_username(config.ADMIN_BOOTSTRAP_USERNAME):
            return
        pwd = config.ADMIN_BOOTSTRAP_PASSWORD
        if pwd is None:
            return
        user = UserORM(
            username=config.ADMIN_BOOTSTRAP_USERNAME,
            password=SecurityService.hash_password(pwd.get_secret_value()),
            name='Админ',
            surname='',
            lastname='',
            role=UserRole.admin.value,
        )
        session.add(user)
        await session.commit()
