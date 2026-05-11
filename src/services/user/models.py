from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from repository.user.models.roles import UserRole

PASSWORD_MIN_LEN = 6


class RegisterRequest(BaseModel):
    username: str
    password: str = Field(min_length=PASSWORD_MIN_LEN)
    name: str
    surname: str
    lastname: str


class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    full_name: str
    role: UserRole


class UserAdminRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    name: str
    surname: str
    lastname: str
    role: UserRole
    created_at: datetime | None = None
    updated_at: datetime | None = None


class UserAdminCreate(BaseModel):
    username: str
    password: str = Field(min_length=PASSWORD_MIN_LEN)
    name: str = ''
    surname: str = ''
    lastname: str = ''
    role: UserRole


class UserAdminUpdate(BaseModel):
    username: str | None = None
    password: str | None = None
    name: str | None = None
    surname: str | None = None
    lastname: str | None = None
    role: UserRole | None = None

    @field_validator('password')
    @classmethod
    def password_min_length(cls, v: str | None) -> str | None:
        if v is not None and len(v) < PASSWORD_MIN_LEN:
            raise ValueError('Пароль должен быть не короче 6 символов')
        return v
