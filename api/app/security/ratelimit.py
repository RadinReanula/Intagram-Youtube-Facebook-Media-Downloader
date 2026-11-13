from __future__ import annotations

from slowapi import Limiter

from app.config import get_settings
from app.security.turnstile import client_key

limiter = Limiter(key_func=client_key, headers_enabled=False)


def limit_value() -> str:
    return get_settings().rate_limit
