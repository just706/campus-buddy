"""FastAPI application entry point.

Creates the FastAPI instance, configures CORS middleware, registers
exception handlers, and mounts API routers.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.exceptions import AppException, app_exception_handler
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — runs startup and shutdown logic."""
    await init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="校园找搭子系统 — Campus Buddy Finding API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
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
app.add_exception_handler(AppException, app_exception_handler)

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
