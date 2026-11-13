from __future__ import annotations

from contextlib import asynccontextmanager
from urllib.parse import urlparse

from app.cache import TtlCache
from app.config import get_settings
from app.auth.cookies import temporary_cookie
from app.errors import limit_exceeded, login_required, not_found, unsupported
from app.models import AnalyzeResult, FormatOption
from app.platforms import get_platform
from app.platforms.detect import detect
from app.platforms.ytdlp import dump_info
from app.security.urls import host_platform, normalized_key, validate_public_url

_cache = TtlCache()


def get_metadata_cache() -> TtlCache:
    return _cache


async def analyze_url(url: str, session_hash: str = "", instagram_settings: dict | None = None) -> AnalyzeResult:
    cleaned = validate_public_url(url)
    hostname = urlparse(cleaned).hostname or ""
    platform_name = host_platform(hostname)
    if platform_name is None:
        raise unsupported("This site isn't supported. Use a public Instagram, Facebook or YouTube link.")
    settings = get_settings()
    if not settings.platform_enabled(platform_name):
        raise unsupported(f"{platform_name.title()} downloads are turned off right now.")
    detection = detect(cleaned, platform_name)
    if detection.media_type == "story" and not session_hash:
        if settings.enable_instagram_login:
            raise login_required("Sign in to Instagram to open this story.")
        raise unsupported("Instagram stories need a sign-in, and sign-in is turned off on this server.")
    key = f"{session_hash}:{normalized_key(cleaned)}" if session_hash else normalized_key(cleaned)
    cached = _cache.get(key)
    if isinstance(cached, AnalyzeResult):
        return cached.model_copy(update={"cached": True})
    async with _cookie_extra(instagram_settings) as extra:
        info = await dump_info(cleaned, extra) if extra else await dump_info(cleaned)
    result = build_result(detection.platform, detection.media_type, info)
    _cache.set(key, result, settings.metadata_cache_ttl_seconds)
    return result


@asynccontextmanager
async def _cookie_extra(instagram_settings: dict | None):
    with temporary_cookie(instagram_settings) as extra:
        yield extra


def build_result(platform_name: str, media_type: str | None, info: dict) -> AnalyzeResult:
    if info.get("is_live"):
        raise unsupported("Live streams are not supported.")
    extractor = str(info.get("extractor_key") or "")
    if extractor in {"YoutubeTab", "InstagramUser"}:
        raise unsupported("Profiles, channels and playlists are not supported. Paste one public video, reel or post.")
    items = get_platform(platform_name).items_for(info, media_type)
    if not items:
        raise not_found()
    resolved_type = media_type or ("post" if len(items) > 1 else items[0].media_type)
    duration = info.get("duration")
    duration_value = float(duration) if isinstance(duration, (int, float)) and duration > 0 else items[0].duration
    return AnalyzeResult(
        platform=platform_name,
        media_type=resolved_type,
        title=info.get("title") or items[0].title,
        thumbnail=info.get("thumbnail") or items[0].thumbnail,
        duration=duration_value,
        uploader=info.get("uploader") or info.get("channel") or info.get("uploader_id"),
        items=items,
        can_download_all=len(items) > 1,
    )


def resolve_format(result: AnalyzeResult, format_id: str, item_index: int | None) -> FormatOption:
    if format_id == "all":
        if not result.can_download_all:
            raise unsupported("There is only one item in this link.")
        warnings = [option.warning for item in result.items for option in item.formats if option.warning]
        if any(option.over_limit for item in result.items for option in item.formats):
            raise limit_exceeded(warnings[0] if warnings else "This file is over the allowed limit.")
        return FormatOption(id="all", label="All items", ext="zip", kind="video")
    index = 0 if item_index is None else item_index
    for item in result.items:
        if item.index != index:
            continue
        for option in item.formats:
            if option.id == format_id:
                if option.over_limit:
                    raise limit_exceeded(option.warning or "This file is over the allowed limit.")
                return option
    raise unsupported("That download option is not available for this link.")
