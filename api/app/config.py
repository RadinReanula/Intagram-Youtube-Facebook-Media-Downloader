from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_override: "Settings | None" = None


class Settings(BaseSettings):
    """Limits and paths. Change them in the environment, not in code."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    host: str = "127.0.0.1"
    port: int = 8000
    cors_origins: str = "http://localhost:3000"
    admin_token: str = ""
    download_signing_secret: str = "dev-change-me"
    turnstile_secret: str = ""

    max_concurrent_jobs: int = 1
    max_queue_length: int = 20
    max_duration_seconds: int = 1800
    max_file_size_bytes: int = 500 * 1024 * 1024
    job_timeout_seconds: int = 600
    file_ttl_seconds: int = 900
    metadata_cache_ttl_seconds: int = 300
    rate_limit: str = "20/minute"
    memory_threshold_percent: float = 85
    disk_threshold_percent: float = 90
    disk_limit_bytes: int = 2 * 1024 * 1024 * 1024
    mp3_quality: str = "5"

    temp_dir: Path = Field(default=Path("./data/tmp"))
    database_path: Path = Field(default=Path("./data/jobs.sqlite"))

    enable_instagram: bool = True
    enable_facebook: bool = True
    enable_youtube: bool = True

    ytdlp_path: str = "yt-dlp"
    ffmpeg_path: str = "ffmpeg"
    log_level: str = "INFO"

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    def platform_enabled(self, platform: str) -> bool:
        return {
            "instagram": self.enable_instagram,
            "facebook": self.enable_facebook,
            "youtube": self.enable_youtube,
        }.get(platform, False)

    def ensure_dirs(self) -> None:
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)


@lru_cache
def _load_settings() -> Settings:
    return Settings()


def get_settings() -> Settings:
    if _override is not None:
        return _override
    return _load_settings()


def set_settings(settings: Settings | None) -> None:
    global _override
    _override = settings
    _load_settings.cache_clear()
