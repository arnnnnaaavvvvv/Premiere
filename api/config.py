"""Typed application configuration module loading from environment variables."""

from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory paths
BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_BASE_DIR = BASE_DIR / "storage"

# Video generation defaults
DEFAULT_FPS = 30
DEFAULT_CAPTURE_FPS = 60
DEFAULT_WIDTH = 1920
DEFAULT_HEIGHT = 1080
DEFAULT_MAX_JOB_DURATION_SEC = 300
DEFAULT_RATE_LIMIT_PER_MIN = 60

class Settings(BaseSettings):
    """Central typed settings for the application."""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Core environment
    app_name: str = "Premiere"
    debug: bool = False
    database_url: str = "sqlite+aiosqlite:///./reelforge.db"
    redis_url: str = "redis://localhost:6379/0"

    # LLM Settings
    llm_provider: str = "openai"  # openai, anthropic, or mock
    openai_api_key: str = Field(default="", validation_alias="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", validation_alias="ANTHROPIC_API_KEY")

    # Storage & Hosting
    storage_provider: str = "local"
    storage_dir: Path = STORAGE_BASE_DIR
    public_base_url: str = "http://localhost:8000"

    # Security & Limits
    ssrf_protection_enabled: bool = True
    rate_limit_per_minute: int = DEFAULT_RATE_LIMIT_PER_MIN

    # Video render specs
    render_fps: int = DEFAULT_FPS
    capture_fps: int = DEFAULT_CAPTURE_FPS
    render_width: int = DEFAULT_WIDTH
    render_height: int = DEFAULT_HEIGHT

settings = Settings()
