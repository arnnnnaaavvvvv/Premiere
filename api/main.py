"""Main FastAPI application entrypoint."""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from api.config import settings
from api.database import init_db
from api.rate_limit import check_rate_limit
from api.routes.jobs import router as jobs_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup and clean up on shutdown."""
    os.makedirs(settings.storage_dir, exist_ok=True)
    await init_db()
    yield

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Automated MNC-style product launch video generator API",
    lifespan=lifespan,
)

# Enable CORS for frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins if not settings.debug else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    """Enforce per-IP request rate limits."""
    # Skip rate limiting for static media or health check
    if not request.url.path.startswith("/storage") and request.url.path != "/health":
        try:
            check_rate_limit(request)
        except Exception as exc:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"error": "RateLimitExceeded", "detail": str(exc), "status_code": 429},
            )
    return await call_next(request)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all error handler producing consistent JSON error structure."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "detail": str(exc),
            "status_code": 500,
        },
    )

@app.get("/health", tags=["System"])
async def health_check():
    """Service health verification."""
    return {"status": "ok", "app": settings.app_name}

# Include routers
app.include_router(jobs_router, prefix="/api/v1")

# Mount storage directory for static access
if os.path.exists(settings.storage_dir):
    app.mount("/storage", StaticFiles(directory=settings.storage_dir), name="storage")
