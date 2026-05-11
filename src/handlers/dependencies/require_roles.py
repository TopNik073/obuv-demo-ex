from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException
from starlette import status

from handlers.dependencies.get_current_user import get_current_user
from repository.user.models.pydantic import UserModel
from repository.user.models.roles import UserRole


def require_roles(*allowed: UserRole) -> Callable[..., UserModel]:
    allowed_set = frozenset(allowed)

    async def _dep(user: Annotated[UserModel, Depends(get_current_user)]) -> UserModel:
        if user.role not in allowed_set:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Insufficient permissions',
            )
        return user

    return _dep
