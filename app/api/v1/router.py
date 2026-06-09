"""API v1 route aggregator.

Collects all v1 sub-routers under the /api/v1 prefix.
"""

from fastapi import APIRouter

from app.api.v1 import auth, matches, posts, users

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(auth.router, tags=["auth"])
api_v1_router.include_router(users.router, tags=["users"])
api_v1_router.include_router(posts.router, tags=["posts"])
api_v1_router.include_router(matches.router, tags=["matches"])
