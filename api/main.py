"""Main FastAPI application entrypoint with security headers and isolated storage."""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
from api.config import settings
from api.database import init_db
from api.rate_limit import check_rate_limit
from api.routes.jobs import router as jobs_router

logger = structlog.get_logger()

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
async def security_headers_and_rate_limit_middleware(request: Request, call_next):
    """Enforce per-IP request rate limits and inject OWASP security headers."""
    if request.url.path != "/health":
        try:
            check_rate_limit(request)
        except Exception as exc:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"error": "RateLimitExceeded", "detail": str(exc), "status_code": 429},
            )

    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none';"
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all error handler producing safe error envelopes without leaking internals."""
    logger.error("Unhandled server exception", path=request.url.path, error=str(exc))
    detail_msg = str(exc) if settings.debug else "An internal server error occurred."
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "detail": detail_msg,
            "status_code": 500,
        },
    )

@app.get("/health", tags=["System"])
async def health_check():
    """Service health verification."""
    return {"status": "ok", "app": settings.app_name}

# Include routers
app.include_router(jobs_router, prefix="/api/v1")

