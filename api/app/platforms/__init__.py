from __future__ import annotations

from app.errors import unsupported
from app.platforms.facebook import Facebook
from app.platforms.instagram import Instagram
from app.platforms.youtube import YouTube

_PLATFORMS = {
    "instagram": Instagram(),
    "facebook": Facebook(),
    "youtube": YouTube(),
}


def get_platform(name: str):
    platform = _PLATFORMS.get(name)
    if platform is None:
        raise unsupported("This site isn't supported. Use a public Instagram, Facebook or YouTube link.")
    return platform
