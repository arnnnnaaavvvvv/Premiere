"""Pydantic schemas for request validation and standardized API responses."""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field, field_validator
from api.models import JobStatus
from api.security import validate_public_url

class JobCredentials(BaseModel):
    """Optional credentials for authenticating web apps before capture."""
    login_url: str = Field(description="URL of login page")
    username: str = Field(description="Username or email")
    password: str = Field(description="Account password")

class CreateJobRequest(BaseModel):
    """Request payload for initiating an automated video generation pipeline."""
    live_url: str = Field(description="Public live application URL")
    repo_url: str = Field(description="Public or token-accessible GitHub repository URL")
    mood: str = Field(default="energetic", description="minimal, energetic, or futuristic")
    music: str = Field(default="default", description="Track ID or default")
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
        if "github.com" not in clean:
            raise ValueError("repo_url must be a valid GitHub URL (e.g. https://github.com/owner/repo)")
        return clean

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
