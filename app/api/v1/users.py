"""User profile API endpoints.

Endpoints for retrieving and updating the authenticated user's profile.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.user import UserResponse, UserUpdateRequest
from app.services import user_service

router = APIRouter(prefix="/users")


@router.get("/me", response_model=APIResponse[UserResponse])
async def get_me(
    current_user: User = Depends(get_current_user),
) -> APIResponse[UserResponse]:
    """Get the current authenticated user's profile."""
    return APIResponse(data=UserResponse.model_validate(current_user))


@router.put("/me", response_model=APIResponse[UserResponse])
async def update_me(
    data: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[UserResponse]:
    """Update the current user's profile.

    Only the fields included in the request body will be updated (partial update).
    Fields omitted from the request remain unchanged.
    """
    updated_user = await user_service.update_profile(db, current_user, data)
    return APIResponse(data=UserResponse.model_validate(updated_user))
