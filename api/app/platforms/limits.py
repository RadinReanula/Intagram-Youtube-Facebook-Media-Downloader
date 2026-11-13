from __future__ import annotations

from app.config import Settings
from app.models import FormatOption

IMAGE_EXTS = {"jpg", "jpeg", "png", "webp", "gif"}


def filesize_of(info: dict) -> int | None:
    size = info.get("filesize") or info.get("filesize_approx")
    if isinstance(size, int) and size > 0:
        return size
    return None


def apply_limits(option: FormatOption, duration: float | None, settings: Settings) -> FormatOption:
    warnings: list[str] = []
    if duration and duration > settings.max_duration_seconds:
        warnings.append("This is longer than the allowed duration.")
    if option.filesize and option.filesize > settings.max_file_size_bytes:
        warnings.append("This is larger than the allowed file size.")
    option.over_limit = bool(warnings)
    option.warning = " ".join(warnings) or None
    return option


def is_image(info: dict) -> bool:
    if isinstance(info.get("duration"), (int, float)) and info["duration"] > 0:
        return False
    ext = str(info.get("ext") or "").lower()
    if ext in IMAGE_EXTS:
        return True
    vcodec = info.get("vcodec")
    formats = info.get("formats") or []
    if vcodec in (None, "none") and not info.get("duration"):
        if not formats:
            return ext in IMAGE_EXTS or ext == ""
        return all(item.get("vcodec") in (None, "none") for item in formats)
    return False
