from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import parse_qs, urlparse

from app.errors import unsupported

_YT_ID = re.compile(r"^[A-Za-z0-9_-]{6,}$")


@dataclass(frozen=True)
class Detection:
    platform: str
    media_type: str | None


def detect(url: str, platform: str) -> Detection:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    path = parsed.path or "/"
    parts = [part for part in path.split("/") if part]
    query = parse_qs(parsed.query)

    if platform == "youtube":
        return Detection("youtube", _youtube(host, parts, query))
    if platform == "instagram":
        return Detection("instagram", _instagram(parts))
    if platform == "facebook":
        return Detection("facebook", _facebook(host, parts))
    raise unsupported("This site isn't supported. Use a public Instagram, Facebook or YouTube link.")


def _youtube(host: str, parts: list[str], query: dict[str, list[str]]) -> str:
    head = parts[0].lower() if parts else ""
    if head in {"playlist", "channel", "c", "user", "feed", "results"} or head.startswith("@"):
        raise unsupported("Playlists, channels and search pages are not supported. Paste a single video link.")
    if head == "live":
        raise unsupported("Live streams are not supported.")
    if "list" in query and "v" not in query and head != "watch" and not host.endswith("youtu.be"):
        raise unsupported("Playlists are not supported. Paste a single video link.")
    if head == "shorts" and len(parts) >= 2 and _YT_ID.match(parts[1]):
        return "short"
    if head == "watch" and query.get("v"):
        return "video"
    if head == "embed" and len(parts) >= 2:
        return "video"
    if host.endswith("youtu.be") and parts and _YT_ID.match(parts[0]):
        return "video"
    if head in {"watch", "shorts", "embed", "live", "playlist"}:
        raise unsupported("This YouTube link is not a single video.")
    raise unsupported("This YouTube link is not a single video.")


def _instagram(parts: list[str]) -> str | None:
    if not parts:
        raise unsupported("Instagram profiles are not supported. Paste a reel, post, video or story link.")
    head = parts[0].lower()
    if head in {"reel", "reels"} and len(parts) >= 2:
        return "reel"
    if head == "p" and len(parts) >= 2:
        return "post"
    if head == "tv" and len(parts) >= 2:
        return "video"
    if head == "stories" and len(parts) >= 2:
        raise unsupported("Instagram stories need a login, so they aren't supported.")
    if head in {"explore", "direct", "accounts", "about"}:
        raise unsupported("This Instagram page is not supported.")
    if len(parts) == 1:
        raise unsupported("Instagram profiles are not supported. Paste a reel, post, video or story link.")
    return None


def _facebook(host: str, parts: list[str]) -> str | None:
    if host.endswith("fb.watch") and parts:
        return "video"
    if not parts:
        raise unsupported("Facebook profiles and pages are not supported. Paste a public video, reel or post.")
    lowered = [part.lower() for part in parts]
    if "live" in lowered:
        raise unsupported("Live streams are not supported.")
    if "reel" in lowered or "reels" in lowered:
        return "reel"
    if "videos" in lowered or "video" in lowered or "watch" in lowered:
        return "video"
    if "posts" in lowered or "photos" in lowered or "photo" in lowered or "permalink" in lowered:
        return "post"
    if "groups" in lowered and len(parts) <= 2:
        raise unsupported("Facebook groups and profiles are not supported.")
    if len(parts) == 1:
        raise unsupported("Facebook profiles and pages are not supported. Paste a public video, reel or post.")
    return None
