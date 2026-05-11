from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import UUID
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt

from core.config import config
from repository.user.models.pydantic import UserModel
from repository.user.models.roles import UserRole
from repository.user.repository import UserRepository
from services.security.models import LoginRequest, RefreshRequest, TokenPairResponse
from services.user.models import RegisterRequest

JWT_TYP_ACCESS = 'access'
JWT_TYP_REFRESH = 'refresh'


class SecurityService:
    _password_hasher = PasswordHasher()

    def __init__(self, user_repository: Annotated[UserRepository, Depends(UserRepository)]) -> None:
        self._users = user_repository

    @classmethod
    def hash_password(cls, plain: str) -> str:
        return cls._password_hasher.hash(plain)

    @classmethod
    def verify_password(
        cls,
        plain: str,
        stored_hash: str,
    ) -> bool:
        try:
            cls._password_hasher.verify(stored_hash, plain)
        except VerifyMismatchError:
            return False
        return True

    def create_token(
        self,
        subject_user_id: UUID,
        *,
        token_type: str,
        expires_at: datetime,
    ) -> str:
        payload = {
            'sub': str(subject_user_id),
            'exp': expires_at,
            'typ': token_type,
        }
        return jwt.encode(
            payload,
            config.JWT_SECRET.get_secret_value(),
            algorithm=config.JWT_ALGORITHM,
        )

    def validate_token(
        self,
        token: str,
        *,
        expected_type: str,
    ) -> UUID | None:
        try:
            payload = jwt.decode(
                token,
                config.JWT_SECRET.get_secret_value(),
                algorithms=[config.JWT_ALGORITHM],
            )
        except (JWTError, ValueError):
            return None
        if payload.get('typ') != expected_type:
            return None
        sub = payload.get('sub')
        if sub is None:
            return None
        try:
            return UUID(str(sub))
        except ValueError:
            return None

    def decode_access_token(self, token: str) -> UUID | None:
        return self.validate_token(token, expected_type=JWT_TYP_ACCESS)

    def decode_refresh_token(self, token: str) -> UUID | None:
        return self.validate_token(token, expected_type=JWT_TYP_REFRESH)

    def issue_token_pair(self, user_id: UUID) -> TokenPairResponse:
        now = datetime.now(UTC)
        access_exp = now + timedelta(minutes=config.JWT_ACCESS_EXPIRE_MINUTES)
        refresh_exp = now + timedelta(minutes=config.JWT_REFRESH_EXPIRE_MINUTES)
        return TokenPairResponse(
            access_token=self.create_token(
                user_id,
                token_type=JWT_TYP_ACCESS,
                expires_at=access_exp,
            ),
            refresh_token=self.create_token(
                user_id,
                token_type=JWT_TYP_REFRESH,
                expires_at=refresh_exp,
            ),
        )

    async def login(self, body: LoginRequest) -> TokenPairResponse:
        user = await self._users.get_by_username(body.username)
        if user is None or not self.verify_password(body.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid username or password',
            )
        if user.id is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='User id is missing',
            )
        return self.issue_token_pair(user.id)

    async def register(self, body: RegisterRequest) -> TokenPairResponse:
        existing = await self._users.get_by_username(body.username)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Username already registered',
            )
        user = UserModel(
            username=body.username,
            password=self.hash_password(body.password),
            name=body.name,
            surname=body.surname,
            lastname=body.lastname,
            role=UserRole.client,
        )
        created = await self._users.create(user)
        if created.id is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='User id is missing',
            )
        return self.issue_token_pair(created.id)

    async def refresh(self, body: RefreshRequest) -> TokenPairResponse:
        user_id = self.decode_refresh_token(body.refresh_token)
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid or expired refresh token',
            )
        user: UserModel | None = await self._users.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='User not found',
            )
        return self.issue_token_pair(user_id)
