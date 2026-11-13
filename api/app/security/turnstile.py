from __future__ import annotations

import hashlib
import hmac
import logging

import httpx
from fastapi import Request

from app.config import get_settings
from app.errors import blocked

logger = logging.getLogger(__name__)


def client_key(request: Request) -> str:
    host = request.client.host if request.client else "unknown"
    secret = get_settings().download_signing_secret.encode()
    return hmac.new(secret, host.encode(), hashlib.sha256).hexdigest()[:24]


async def verify_turnstile(token: str | None, request: Request) -> None:
    secret = get_settings().turnstile_secret
    if not secret:
        return
    if not token:
        raise blocked("Please confirm you are not a robot and try again.")
    host = request.client.host if request.client else None
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.post(
                "https://challenges.cloudflare.com/turnstile/v0/siteverify",
                data={"secret": secret, "response": token, "remoteip": host or ""},
            )
            payload = response.json()
    except httpx.HTTPError:
        logger.warning("turnstile verification request failed")
        raise blocked("The check could not be completed. Try again.") from None
    if not payload.get("success"):
        raise blocked("Please confirm you are not a robot and try again.")
