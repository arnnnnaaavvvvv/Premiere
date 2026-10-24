"""Main FastAPI application entrypoint with security headers, startup health checks, and unified error handling."""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import structlog
from api.config import settings
from api.database import init_db
from api.rate_limit import check_rate_limit
from api.routes.jobs import router as jobs_router

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources and perform startup dependency verification."""
    os.makedirs(settings.storage_dir, exist_ok=True)
    await init_db()
    font_path = settings.storage_dir.parent / "worker" / "assets" / "fonts" / "BebasNeue-Regular.ttf"
    if not font_path.exists():
        logger.warning("Bebas Neue TrueType font file is missing", path=str(font_path))
    logger.info("Application initialized", app=settings.app_name, storage=str(settings.storage_dir))
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

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Produce standardized JSON error responses for all HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "HttpException", "detail": exc.detail, "status_code": exc.status_code},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all error handler producing safe error envelopes without leaking internals."""
    logger.error("Unhandled server exception", path=request.url.path, error=str(exc))
    detail_msg = str(exc) if settings.debug else "An internal server error occurred."
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "InternalServerError", "detail": detail_msg, "status_code": 500},
    )

@app.get("/health", tags=["System"])
async def health_check():
    """Service health verification."""
    return {"status": "ok", "app": settings.app_name}

# Include routers
app.include_router(jobs_router, prefix="/api/v1")
