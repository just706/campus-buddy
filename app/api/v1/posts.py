"""Post API endpoints.

CRUD operations for campus buddy-finding posts with filtering and pagination.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.post import PostCreate, PostFilter, PostListResponse, PostResponse, PostUpdate
from app.services import post_service

router = APIRouter(prefix="/posts")


@router.post("", response_model=APIResponse[PostResponse], status_code=201)
async def create_post(
    data: PostCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[PostResponse]:
    """Create a new buddy-finding post.

    Posts include category, tags, target participant count, and optional
    expiry time for automatic closing.
    """
    post = await post_service.create_post(db, current_user.id, data)
    return APIResponse(code=201, message="Post created", data=PostResponse.model_validate(post))


@router.get("", response_model=APIResponse[PostListResponse])
async def list_posts(
    category: str | None = Query(default=None, description="Filter by category"),
    tag: str | None = Query(default=None, description="Filter by a single tag"),
    keyword: str | None = Query(default=None, description="Search title and description"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[PostListResponse]:
    """List active posts with optional filtering and pagination.

    Expired posts are always excluded. Results are sorted by newest first.
    """
    filters = PostFilter(
        category=category,
        tag=tag,
        keyword=keyword,
        page=page,
        page_size=page_size,
    )
    posts, total = await post_service.get_posts(db, filters)
    return APIResponse(
        data=PostListResponse(
            items=[PostResponse.model_validate(p) for p in posts],
            total=total,
            page=filters.page,
            page_size=filters.page_size,
        )
    )


@router.get("/{post_id}", response_model=APIResponse[PostResponse])
async def get_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[PostResponse]:
    """Get a single post by ID. Lazily closes expired posts on access."""
    post = await post_service.get_post(db, post_id)
    return APIResponse(data=PostResponse.model_validate(post))


@router.put("/{post_id}", response_model=APIResponse[PostResponse])
async def update_post(
    post_id: int,
    data: PostUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[PostResponse]:
    """Update a post. Only the author can edit.

    Only the fields provided in the request body are changed.
    """
    post = await post_service.update_post(db, post_id, current_user.id, data)
    return APIResponse(data=PostResponse.model_validate(post))


@router.delete("/{post_id}", response_model=APIResponse[PostResponse])
async def close_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[PostResponse]:
    """Close a post (soft delete). Only the author can close."""
    post = await post_service.close_post(db, post_id, current_user.id)
    return APIResponse(message="Post closed", data=PostResponse.model_validate(post))
