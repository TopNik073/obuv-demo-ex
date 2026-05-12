from typing import Annotated

from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from starlette import status

from repository.user.models.pydantic import UserModel
from services.security.service import SecurityService
from services.user.service import UserService

_optional_bearer = HTTPBearer(auto_error=False)


async def get_optional_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_optional_bearer)],
    security_service: Annotated[SecurityService, Depends(SecurityService)],
    user_service: Annotated[UserService, Depends(UserService)],
) -> UserModel | None:
    if credentials is None or credentials.scheme.lower() != 'bearer':
        return None
    user_id = security_service.decode_access_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid or expired token',
        )
    user = await user_service.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User not found',
        )
    return user
