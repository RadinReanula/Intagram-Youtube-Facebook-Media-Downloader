from __future__ import annotations

from typing import Protocol

from app.models import FormatOption, MediaItem


class Platform(Protocol):
    name: str

    def items_for(self, info: dict, media_type: str | None) -> list[MediaItem]:
        """Turn extractor metadata into the choices shown to the user."""

    def format_args(self, format_id: str) -> list[str]:
        """Arguments passed to yt-dlp for a format id this platform issued."""
