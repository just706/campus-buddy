"""FastAPI application entry point.

Creates the FastAPI instance, configures CORS middleware, registers
exception handlers, and mounts API routers.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    generic_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.db.init_db import init_db

# ===== Swagger Tag Metadata =====
tags_metadata = [
    {
        "name": "health",
        "description": "Health check endpoint for monitoring and readiness probes.",
    },
    {
        "name": "auth",
        "description": "User registration, login, and JWT token refresh. These endpoints are public (no authentication required).",
    },
    {
        "name": "users",
        "description": "User profile management — view and update your own profile. Requires authentication.",
    },
    {
        "name": "posts",
        "description": "Buddy-finding posts — create, browse, filter, update, and close posts. Requires authentication.",
    },
    {
        "name": "matches",
        "description": "AI-powered buddy matching — get recommendations, send match requests, and view match status. Requires authentication.",
    },
    {
        "name": "chats",
        "description": "Real-time chat between matched buddies — send messages (HTTP), view conversation history, and manage read status. Requires authentication.",
    },
    {
        "name": "websocket",
        "description": "WebSocket endpoint for real-time chat messaging. Connect with a JWT token to receive live messages.",
    },
    {
        "name": "notifications",
        "description": "User notifications — view notification list, mark as read individually or in batch. Requires authentication.",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — runs startup and shutdown logic."""
    await init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="校园找搭子系统 — Campus Buddy Finding API. Find study partners, sports buddies, dining companions, and travel mates with AI-powered matching.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    openapi_tags=tags_metadata,
)

# ===== CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Exception Handlers =====
# Order matters: more specific handlers should be registered first.
# FastAPI resolves handlers by exception type hierarchy.
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# ===== Routers =====
app.include_router(api_v1_router)


@app.get("/", tags=["health"])
async def root() -> dict[str, str]:
    """Health check endpoint."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }
