from __future__ import annotations

import hashlib
import hmac
import time
from urllib.parse import urlencode

from app.config import get_settings
from app.errors import invalid_link


def sign_download(job_id: str, expires_at: int | None = None) -> str:
    settings = get_settings()
    expiry = expires_at if expires_at is not None else int(time.time()) + settings.file_ttl_seconds
    payload = f"{job_id}.{expiry}"
    digest = hmac.new(settings.download_signing_secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return urlencode({"expires": expiry, "token": digest})


def verify_download(job_id: str, expires: str, token: str) -> None:
    settings = get_settings()
    try:
        expiry = int(expires)
    except (TypeError, ValueError):
        raise invalid_link("This download link is not valid.") from None
    if expiry < int(time.time()):
        raise invalid_link("This download link has expired.")
    payload = f"{job_id}.{expiry}"
    expected = hmac.new(settings.download_signing_secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, token or ""):
        raise invalid_link("This download link is not valid.")
