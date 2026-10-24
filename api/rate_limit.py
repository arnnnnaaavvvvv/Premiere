"""Lightweight sliding-window rate limiter per client IP."""

import time
from collections import defaultdict
from fastapi import HTTPException, Request, status
from api.config import settings

# In-memory timestamp log per client IP: { ip: [timestamp1, timestamp2, ...] }
_ip_requests: dict[str, list[float]] = defaultdict(list)

def check_rate_limit(request: Request) -> None:
    """Enforce request limits per client IP within a 60-second window."""
    now = time.time()
    window_start = now - 60.0
    client_ip = request.client.host if request.client else "unknown"

    # Purge expired timestamps
    recent = [ts for ts in _ip_requests[client_ip] if ts > window_start]
    _ip_requests[client_ip] = recent

    if len(recent) >= settings.rate_limit_per_minute:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Maximum {settings.rate_limit_per_minute} requests per minute.",
        )

    _ip_requests[client_ip].append(now)
