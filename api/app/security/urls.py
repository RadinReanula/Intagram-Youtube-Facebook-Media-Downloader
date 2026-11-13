from __future__ import annotations

import ipaddress
import re
from urllib.parse import parse_qsl, urlencode, urlparse

from app.errors import invalid_link, unsupported

ALLOWED_HOSTS: dict[str, str] = {
    "instagram.com": "instagram",
    "instagr.am": "instagram",
    "facebook.com": "facebook",
    "fb.com": "facebook",
    "fb.watch": "facebook",
    "youtube.com": "youtube",
    "youtu.be": "youtube",
}

_TRACKING_PARAMS = {
    "igshid",
    "igsh",
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "fbclid",
    "si",
    "feature",
}


def host_platform(hostname: str) -> str | None:
    host = hostname.lower().rstrip(".")
    for suffix, platform in ALLOWED_HOSTS.items():
        if host == suffix or host.endswith("." + suffix):
            return platform
    return None


def validate_public_url(raw: str) -> str:
    text = raw.strip()
    if not text or any(char in text for char in ("\n", "\r", "\x00")):
        raise invalid_link()
    parsed = urlparse(text)
    if parsed.scheme not in {"http", "https"}:
        raise invalid_link("The link must start with http or https.")
    if parsed.username or parsed.password:
        raise invalid_link()
    hostname = parsed.hostname
    if not hostname:
        raise invalid_link()
    try:
        ipaddress.ip_address(hostname)
    except ValueError:
        pass
    else:
        raise unsupported("Links to raw IP addresses are not supported.")
    if host_platform(hostname) is None:
        raise unsupported("This site isn't supported. Use a public Instagram, Facebook or YouTube link.")
    return text


def normalized_key(url: str) -> str:
    parsed = urlparse(url.strip())
    host = (parsed.hostname or "").lower()
    path = re.sub(r"/+$", "", parsed.path) or "/"
    query = urlencode(sorted((key, value) for key, value in parse_qsl(parsed.query, keep_blank_values=True) if key.lower() not in _TRACKING_PARAMS))
    suffix = f"?{query}" if query else ""
    return f"{parsed.scheme.lower()}://{host}{path}{suffix}"
