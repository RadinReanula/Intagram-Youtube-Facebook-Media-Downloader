from __future__ import annotations

from app.config import get_settings
from app.models import FormatOption, MediaItem
from app.platforms.limits import apply_limits, filesize_of, is_image


class Instagram:
    name = "instagram"

    def items_for(self, info: dict, media_type: str | None) -> list[MediaItem]:
        return social_items(info, media_type or "post")

    def format_args(self, format_id: str) -> list[str]:
        return social_format_args(format_id)


class Facebook:
    name = "facebook"

    def items_for(self, info: dict, media_type: str | None) -> list[MediaItem]:
        return social_items(info, media_type or "video")

    def format_args(self, format_id: str) -> list[str]:
        return social_format_args(format_id)


def social_items(info: dict, media_type: str) -> list[MediaItem]:
    settings = get_settings()
    entries = [entry for entry in (info.get("entries") or []) if isinstance(entry, dict)]
    if not entries:
        entries = [info]
    items: list[MediaItem] = []
    for index, entry in enumerate(entries):
        image = is_image(entry)
        duration = _duration(entry)
        if image:
            option = FormatOption(
                id="best",
                label="Image",
                ext=_ext(entry, "jpg"),
                kind="image",
                filesize=filesize_of(entry),
            )
            item_type = "post"
        else:
            option = FormatOption(
                id="best[ext=mp4]/best",
                label="Best quality",
                ext="mp4",
                kind="video",
                filesize=filesize_of(entry),
            )
            item_type = media_type if media_type in {"reel", "video", "story", "post"} else "video"
        apply_limits(option, duration, settings)
        items.append(
            MediaItem(
                index=index,
                title=entry.get("title") or info.get("title"),
                thumbnail=entry.get("thumbnail") or info.get("thumbnail"),
                duration=duration,
                media_type=item_type,
                formats=[option],
            )
        )
    return items


def social_format_args(format_id: str) -> list[str]:
    if format_id in {"best", "all"}:
        return ["-f", "best"]
    return ["-f", format_id, "--merge-output-format", "mp4"]


def _duration(info: dict) -> float | None:
    duration = info.get("duration")
    if isinstance(duration, (int, float)) and duration > 0:
        return float(duration)
    return None


def _ext(info: dict, fallback: str) -> str:
    ext = str(info.get("ext") or fallback).lower().lstrip(".")
    return ext or fallback
