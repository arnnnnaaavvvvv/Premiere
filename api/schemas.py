"""Pydantic schemas for request validation and standardized API responses."""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field, field_validator
from api.models import JobStatus
from api.security import validate_public_url

import re
from urllib.parse import urlparse

class JobCredentials(BaseModel):
    """Optional credentials for authenticating web apps before capture."""
    login_url: str = Field(max_length=1024, description="URL of login page")
    username: str = Field(max_length=128, description="Username or email")
    password: str = Field(max_length=256, description="Account password")

    @field_validator("login_url")
    @classmethod
    def check_login_url(cls, v: str) -> str:
        return validate_public_url(v)

class CreateJobRequest(BaseModel):
    """Request payload for initiating an automated video generation pipeline."""
    live_url: str = Field(max_length=1024, description="Public live application URL")
    repo_url: str = Field(max_length=1024, description="Public GitHub repository URL")
    mood: str = Field(default="energetic", description="minimal, energetic, or futuristic")
    music: str = Field(default="default", max_length=64, description="Track ID or default")
    narration: bool = Field(default=False, description="Enable AI voiceover narration")
    credentials: JobCredentials | None = Field(default=None, description="Optional login details")

    @field_validator("live_url")
    @classmethod
    def check_live_url(cls, v: str) -> str:
        return validate_public_url(v)

    @field_validator("repo_url")
    @classmethod
    def check_repo_url(cls, v: str) -> str:
        clean = validate_public_url(v)
        parsed = urlparse(clean)
        if parsed.netloc.lower() not in ("github.com", "www.github.com"):
            raise ValueError("repo_url must be a GitHub URL hosted on github.com")
        path = parsed.path.strip("/")
        parts = [p for p in path.split("/") if p]
        if len(parts) < 2 or not re.match(r"^[a-zA-Z0-9_\-\.]+$", parts[0]) or not re.match(r"^[a-zA-Z0-9_\-\.]+$", parts[1]) or ".." in path:
            raise ValueError("repo_url must match format: https://github.com/owner/repository")
        return clean

    @field_validator("mood")
    @classmethod
    def check_mood(cls, v: str) -> str:
        allowed = {"energetic", "minimal", "futuristic"}
        if v.lower() not in allowed:
            raise ValueError(f"Invalid mood: '{v}'. Must be one of: {allowed}")
        return v.lower()


class JobResponse(BaseModel):
    """Full job status, progress percentage, and render metadata."""
    id: str
    live_url: str
    repo_url: str
    mood: str
    music: str
    narration: bool
    status: JobStatus
    progress: int
    current_stage: str
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime
    video_url: str | None = None

    model_config = ConfigDict(from_attributes=True)

class ErrorResponse(BaseModel):
    """Consistent RFC 7807-style error envelope across all API endpoints."""
    error: str
    detail: str
    status_code: int
    data: dict[str, Any] | None = None
