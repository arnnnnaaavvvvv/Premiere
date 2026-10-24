"""Database models for Premiere job execution pipeline."""

import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import BigInteger, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from api.database import Base

def utc_now() -> datetime:
    """Return timezone-aware current UTC datetime."""
    return datetime.now(timezone.utc)

class JobStatus(str, enum.Enum):
    """Execution status lifecycle for an automated video generation job."""
    QUEUED = "queued"
    ANALYZING = "analyzing"
    SCRIPTING = "scripting"
    CAPTURING = "capturing"
    RENDERING = "rendering"
    DONE = "done"
    FAILED = "failed"

class Job(Base):
    """Primary job tracking submission, parameters, and lifecycle progression."""
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    live_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    repo_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    mood: Mapped[str] = mapped_column(String(32), default="energetic")
    music: Mapped[str] = mapped_column(String(64), default="default")
    narration: Mapped[bool] = mapped_column(default=False)
    credentials_json: Mapped[dict | None] = mapped_column(SQLiteJSON, nullable=True)

    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.QUEUED, index=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    current_stage: Mapped[str] = mapped_column(String(64), default="Initialized")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    script: Mapped["Script"] = relationship(back_populates="job", uselist=False, cascade="all, delete-orphan")
    assets: Mapped[list["Asset"]] = relationship(back_populates="job", cascade="all, delete-orphan")
    render: Mapped["Render"] = relationship(back_populates="job", uselist=False, cascade="all, delete-orphan")

class Script(Base):
    """Stores LLM product brief and beat-aligned scene plan."""
    __tablename__ = "scripts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), unique=True)
    product_brief: Mapped[dict] = mapped_column(SQLiteJSON, nullable=False)
    scene_plan: Mapped[dict] = mapped_column(SQLiteJSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    job: Mapped["Job"] = relationship(back_populates="script")

class Asset(Base):
    """Captured web screenshots, 60fps video clips, and audio stems."""
    __tablename__ = "assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    asset_type: Mapped[str] = mapped_column(String(32))  # clip, screenshot, audio
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    metadata_json: Mapped[dict | None] = mapped_column(SQLiteJSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    job: Mapped["Job"] = relationship(back_populates="assets")

class Render(Base):
    """Final rendered MP4 video artifact metadata and download link."""
    __tablename__ = "renders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), unique=True)
    video_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    resolution: Mapped[str] = mapped_column(String(32), default="1920x1080")
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    job: Mapped["Job"] = relationship(back_populates="render")
