from __future__ import annotations

import asyncio
import secrets
import time
from dataclasses import dataclass

from pydantic import SecretStr

from app.errors import ApiError, blocked

_PENDING: dict[str, "PendingLogin"] = {}
_GENERIC = "Instagram didn't accept that sign-in. Check the username and password, then try again."
_CHECKPOINT = "Instagram asked you to approve this sign-in in the app. Open Instagram, approve it, then try again."


@dataclass
class PendingLogin:
    client: object
    username: str
    password: SecretStr
    created: float
    user_agent: str


def _purge() -> None:
    now = time.time()
    stale = [key for key, item in _PENDING.items() if now - item.created > 300]
    for key in stale:
        _PENDING.pop(key, None)


def _client():
    from instagrapi import Client

    client = Client()
    client.delay_range = [1, 2]
    return client


def _settings(client) -> dict:
    payload = client.get_settings()
    if hasattr(client, "password"):
        client.password = ""
    return payload


def _login_sync(username: str, password: str, code: str | None, challenge_id: str | None, user_agent: str) -> dict:
    from instagrapi.exceptions import (
        BadPassword,
        ChallengeRequired,
        PleaseWaitFewMinutes,
        TwoFactorRequired,
    )

    _purge()
    if challenge_id:
        pending = _PENDING.pop(challenge_id, None)
        if pending is None or pending.user_agent != user_agent or time.time() - pending.created > 300:
            raise ApiError("login_required", "That sign-in step expired. Start again.", 401)
        if pending.username.lower() != username.lower():
            raise ApiError("login_required", _GENERIC, 401)
        client = pending.client
        secret = pending.password.get_secret_value()
        try:
            client.login(username, secret, verification_code=code or "")
        except TwoFactorRequired as exc:
            raise ApiError("login_required", "That code was not accepted. Try again.", 401) from exc
        except (BadPassword, ChallengeRequired, PleaseWaitFewMinutes) as exc:
            raise ApiError("blocked", _CHECKPOINT if isinstance(exc, ChallengeRequired) else _GENERIC, 401) from exc
        finally:
            pending.password = SecretStr("")
        return {"status": "ok", "username": username, "settings": _settings(client)}

    client = _client()
    try:
        client.login(username, password, verification_code=code or "")
    except TwoFactorRequired:
        pending_id = secrets.token_urlsafe(24)
        _PENDING[pending_id] = PendingLogin(
            client=client,
            username=username,
            password=SecretStr(password),
            created=time.time(),
            user_agent=user_agent,
        )
        return {"status": "two_factor", "challenge_id": pending_id, "username": username}
    except ChallengeRequired as exc:
        raise ApiError("blocked", _CHECKPOINT, 401) from exc
    except (BadPassword, PleaseWaitFewMinutes) as exc:
        raise ApiError("blocked", _GENERIC, 401) from exc
    except Exception as exc:
        raise blocked(_GENERIC) from exc
    return {"status": "ok", "username": username, "settings": _settings(client)}


async def sign_in(username: str, password: str, code: str | None, challenge_id: str | None, user_agent: str) -> dict:
    return await asyncio.to_thread(_login_sync, username, password, code, challenge_id, user_agent)


def sign_out_sync(instagram_settings: dict | None) -> None:
    if not instagram_settings:
        return
    try:
        client = _client()
        client.set_settings(instagram_settings)
        client.logout()
    except Exception:
        return


async def sign_out(instagram_settings: dict | None) -> None:
    await asyncio.to_thread(sign_out_sync, instagram_settings)


def reset_pending() -> None:
    _PENDING.clear()
