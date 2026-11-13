from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from dataclasses import dataclass, field

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from fastapi import Request, Response

from app.config import Settings, get_settings

_SALT = b"media-downloader-ig-session"


@dataclass
class SessionRecord:
    token_hash: str
    ciphertext: bytes
    username: str
    user_agent: str
    created: float
    seen: float
    job_ids: set[str] = field(default_factory=set)


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, SessionRecord] = {}
        self._attempts: dict[str, list[float]] = {}

    def reset(self) -> None:
        self._sessions.clear()
        self._attempts.clear()

    def cookie_name(self, settings: Settings | None = None) -> str:
        settings = settings or get_settings()
        return "__Host-md_session" if settings.cookie_secure else "md_session"

    def read_token(self, request: Request) -> str | None:
        return request.cookies.get("__Host-md_session") or request.cookies.get("md_session")

    def token_hash(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    def allow_attempt(self, key: str, limit: int = 5, window: int = 900) -> bool:
        now = time.time()
        stamps = [stamp for stamp in self._attempts.get(key, []) if now - stamp < window]
        if len(stamps) >= limit:
            self._attempts[key] = stamps
            return False
        stamps.append(now)
        self._attempts[key] = stamps
        return True

    def open_session(self, *, username: str, settings_dict: dict, user_agent: str) -> str:
        settings = get_settings()
        self._purge()
        if len(self._sessions) >= settings.max_sessions:
            oldest = min(self._sessions, key=lambda key: self._sessions[key].seen)
            self._sessions.pop(oldest, None)
        token = secrets.token_urlsafe(32)
        digest = self.token_hash(token)
        now = time.time()
        self._sessions[digest] = SessionRecord(
            token_hash=digest,
            ciphertext=self._encrypt(token, settings_dict),
            username=username,
            user_agent=user_agent[:300],
            created=now,
            seen=now,
        )
        return token

    def remember_job(self, token: str, job_id: str) -> None:
        record = self._record(token, touch=False)
        if record is not None:
            record.job_ids.add(job_id)

    def current(self, request: Request) -> SessionRecord | None:
        token = self.read_token(request)
        if not token:
            return None
        record = self._record(token, touch=True)
        if record is None:
            return None
        agent = request.headers.get("user-agent", "")[:300]
        if not hmac.compare_digest(record.user_agent, agent):
            return None
        return record

    def instagram_settings(self, request: Request) -> dict | None:
        token = self.read_token(request)
        record = self.current(request)
        if token is None or record is None:
            return None
        try:
            raw = self._decrypt(token, record.ciphertext)
        except InvalidToken:
            return None
        return json.loads(raw)

    def drop(self, request: Request) -> tuple[str | None, dict | None, set[str]]:
        token = self.read_token(request)
        if not token:
            return None, None, set()
        digest = self.token_hash(token)
        record = self._sessions.pop(digest, None)
        if record is None:
            return None, None, set()
        try:
            raw = self._decrypt(token, record.ciphertext)
            payload = json.loads(raw)
        except (InvalidToken, json.JSONDecodeError):
            payload = None
        return record.username, payload, set(record.job_ids)

    def write_cookie(self, response: Response, token: str) -> None:
        settings = get_settings()
        response.set_cookie(
            self.cookie_name(settings),
            token,
            max_age=settings.session_absolute_seconds,
            httponly=True,
            secure=settings.cookie_secure,
            samesite="lax",
            path="/",
        )

    def clear_cookie(self, response: Response) -> None:
        settings = get_settings()
        response.delete_cookie(self.cookie_name(settings), path="/", secure=settings.cookie_secure, httponly=True, samesite="lax")

    def _record(self, token: str, touch: bool) -> SessionRecord | None:
        settings = get_settings()
        digest = self.token_hash(token)
        record = self._sessions.get(digest)
        if record is None:
            return None
        now = time.time()
        if now - record.created > settings.session_absolute_seconds or now - record.seen > settings.session_idle_seconds:
            self._sessions.pop(digest, None)
            return None
        if touch:
            record.seen = now
        return record

    def _purge(self) -> None:
        settings = get_settings()
        now = time.time()
        stale = [
            key
            for key, record in self._sessions.items()
            if now - record.created > settings.session_absolute_seconds or now - record.seen > settings.session_idle_seconds
        ]
        for key in stale:
            self._sessions.pop(key, None)

    def _encrypt(self, token: str, payload: dict) -> bytes:
        return self._fernet(token).encrypt(json.dumps(payload).encode())

    def _decrypt(self, token: str, ciphertext: bytes) -> bytes:
        return self._fernet(token).decrypt(ciphertext)

    def _fernet(self, token: str) -> Fernet:
        material = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=_SALT,
            info=b"instagram-session",
        ).derive(token.encode())
        return Fernet(base64.urlsafe_b64encode(material))


sessions = SessionStore()


def session_hash(request: Request) -> str:
    token = sessions.read_token(request)
    record = sessions.current(request)
    if token is None or record is None:
        return ""
    return record.token_hash


def public_state(request: Request) -> dict:
    record = sessions.current(request)
    if record is None:
        return {"signed_in": False, "username": None}
    return {"signed_in": True, "username": record.username}


def assert_origin(request: Request) -> None:
    if request.method in {"GET", "HEAD", "OPTIONS"}:
        return
    origin = request.headers.get("origin")
    allowed = set(get_settings().cors_origin_list)
    cookie = sessions.read_token(request)
    from app.errors import ApiError

    if origin:
        if origin not in allowed:
            raise ApiError("blocked", "This request was blocked.", 403)
        return
    if cookie or request.url.path.startswith("/api/auth"):
        raise ApiError("blocked", "This request was blocked.", 403)
