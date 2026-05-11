from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from repository.base.models.postgres import BaseORM, TimestampMixin
from repository.user.models.roles import UserRole


class UserORM(BaseORM, TimestampMixin):
    __tablename__ = 'users'

    username: Mapped[str] = mapped_column(String(), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(), nullable=False)

    name: Mapped[str] = mapped_column(String(), nullable=False)
    surname: Mapped[str] = mapped_column(String(), nullable=False)
    lastname: Mapped[str] = mapped_column(String(), nullable=False)

    role: Mapped[str] = mapped_column(String(), nullable=False)

    def role_enum(self) -> UserRole:
        return UserRole(self.role)
