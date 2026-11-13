from __future__ import annotations

from app.config import get_settings
from app.models import FormatOption, MediaItem
from app.platforms.limits import apply_limits, filesize_of


class YouTube:
    name = "youtube"

    def items_for(self, info: dict, media_type: str | None) -> list[MediaItem]:
        settings = get_settings()
        duration = info.get("duration")
        duration_value = float(duration) if isinstance(duration, (int, float)) and duration > 0 else None
        options = _quality_options(info)
        if not options:
            options = [FormatOption(id="best[ext=mp4]/best", label="Best quality", ext="mp4", kind="video", filesize=filesize_of(info))]
        for option in options:
            apply_limits(option, duration_value, settings)
        return [
            MediaItem(
                index=0,
                title=info.get("title"),
                thumbnail=info.get("thumbnail"),
                duration=duration_value,
                media_type=media_type or "video",
                formats=options,
            )
        ]

    def format_args(self, format_id: str) -> list[str]:
        if format_id == "audio":
            quality = get_settings().mp3_quality
            if quality not in {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"}:
                quality = "5"
            return ["-f", "bestaudio/best", "-x", "--audio-format", "mp3", "--audio-quality", quality]
        return ["-f", format_id, "--merge-output-format", "mp4"]


def _quality_options(info: dict) -> list[FormatOption]:
    formats = [item for item in (info.get("formats") or []) if isinstance(item, dict)]
    audio_sizes = [
        filesize_of(item)
        for item in formats
        if item.get("acodec") not in (None, "none") and item.get("vcodec") in (None, "none")
    ]
    audio_size = next((size for size in audio_sizes if size), None)
    by_height: dict[int, int | None] = {}
    has_audio = audio_size is not None or any(item.get("acodec") not in (None, "none") for item in formats)
    for item in formats:
        if item.get("vcodec") in (None, "none"):
            continue
        height = item.get("height")
        if not isinstance(height, int) or height < 144:
            continue
        size = filesize_of(item)
        progressive = item.get("acodec") not in (None, "none")
        if size and not progressive and audio_size:
            size += audio_size
        current = by_height.get(height)
        prefer = item.get("ext") == "mp4"
        if current is None or (prefer and size):
            by_height[height] = size
        elif size and (current is None or size > (current or 0)):
            by_height[height] = size
    options: list[FormatOption] = []
    for height in sorted(by_height):
        selector = (
            f"bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]"
            f"/best[height<={height}][ext=mp4]/best[height<={height}]"
        )
        options.append(
            FormatOption(id=selector, label=f"{height}p", ext="mp4", kind="video", filesize=by_height[height])
        )
    if has_audio:
        options.append(FormatOption(id="audio", label="Audio only", ext="mp3", kind="audio", filesize=audio_size))
    return options
