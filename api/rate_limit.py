"""Lightweight bounded sliding-window rate limiter per client IP."""

import time
from collections import defaultdict
from fastapi import HTTPException, Request, status
from api.config import settings

_ip_requests: dict[str, list[float]] = defaultdict(list)
_ip_job_requests: dict[str, list[float]] = defaultdict(list)
MAX_TRACKED_IPS = 10000

def _prune_expired(now: float, window_start: float):
    """Prune inactive IPs when tracked count exceeds threshold to prevent memory leaks."""
    if len(_ip_requests) > MAX_TRACKED_IPS:
        dead_ips = [ip for ip, tss in _ip_requests.items() if not tss or max(tss) < window_start]
        for ip in dead_ips:
            _ip_requests.pop(ip, None)
            _ip_job_requests.pop(ip, None)

def get_client_ip(request: Request) -> str:
    """Extract client IP, considering trusted forwarded headers if provided."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

def check_rate_limit(request: Request) -> None:
    """Enforce request limits and job creation limits per client IP within a 60-second window."""
    now = time.time()
    window_start = now - 60.0
    client_ip = get_client_ip(request)

    _prune_expired(now, window_start)

    # General request rate limit
    recent = [ts for ts in _ip_requests[client_ip] if ts > window_start]
    _ip_requests[client_ip] = recent

    if len(recent) >= settings.rate_limit_per_minute:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Maximum {settings.rate_limit_per_minute} requests per minute.",
        )

    # Stricter job creation quota
    if request.method == "POST" and request.url.path.endswith("/jobs"):
        recent_jobs = [ts for ts in _ip_job_requests[client_ip] if ts > window_start]
        _ip_job_requests[client_ip] = recent_jobs
        if len(recent_jobs) >= settings.job_rate_limit_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Job creation limit exceeded. Maximum {settings.job_rate_limit_per_minute} jobs per minute.",
            )
        _ip_job_requests[client_ip].append(now)

    _ip_requests[client_ip].append(now)

