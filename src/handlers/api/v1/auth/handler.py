from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from handlers.dependencies.get_current_user import get_current_user
from repository.user.models.pydantic import UserModel
from services.security.models import LoginRequest
from services.security.models import RefreshRequest
from services.security.models import TokenPairResponse
from services.security.service import SecurityService
from services.user.models import RegisterRequest
from services.user.models import UserProfileResponse

auth_router = APIRouter(prefix='/auth', tags=['auth'])


@auth_router.post('/login', response_model=TokenPairResponse)
async def login(
    body: LoginRequest,
    security_service: Annotated[SecurityService, Depends(SecurityService)],
) -> TokenPairResponse:
    return await security_service.login(body)


@auth_router.post('/register', response_model=TokenPairResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    security_service: Annotated[SecurityService, Depends(SecurityService)],
) -> TokenPairResponse:
    return await security_service.register(body)


@auth_router.post('/refresh', response_model=TokenPairResponse)
async def refresh_tokens(
    body: RefreshRequest,
    security_service: Annotated[SecurityService, Depends(SecurityService)],
) -> TokenPairResponse:
    return await security_service.refresh(body)


@auth_router.get('/profile', response_model=UserProfileResponse)
async def get_profile(
    current_user: Annotated[UserModel, Depends(get_current_user)],
) -> UserProfileResponse:
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='User id is missing',
        )
    return UserProfileResponse(
        id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name(),
        role=current_user.role,
    )
