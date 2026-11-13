from __future__ import annotations

import hmac

from fastapi import APIRouter, Header, Request

from app.config import get_settings
from app.errors import ApiError
from app.jobs.resources import snapshot

router = APIRouter()


def _require_admin(authorization: str | None) -> None:
    token = get_settings().admin_token
    if not token:
        raise ApiError("unsupported", "Admin access is not configured.", 404)
    expected = f"Bearer {token}"
    supplied = authorization or ""
    if len(supplied) != len(expected) or not hmac.compare_digest(supplied, expected):
        raise ApiError("unsupported", "Admin access was denied.", 401)


@router.get("/api/admin/stats")
async def stats(request: Request, authorization: str | None = Header(default=None)) -> dict[str, object]:
    _require_admin(authorization)
    settings = get_settings()
    store = request.app.state.store
    return {
        "jobs": store.counts(),
        "queued": store.queued_count(),
        "resources": snapshot(settings),
        "platforms": {
            "instagram": settings.enable_instagram,
            "facebook": settings.enable_facebook,
            "youtube": settings.enable_youtube,
        },
        "limits": {
            "max_concurrent_jobs": settings.max_concurrent_jobs,
            "max_duration_seconds": settings.max_duration_seconds,
            "max_file_size_bytes": settings.max_file_size_bytes,
            "rate_limit": settings.rate_limit,
            "job_timeout_seconds": settings.job_timeout_seconds,
            "file_ttl_seconds": settings.file_ttl_seconds,
        },
        "recent_errors": store.recent_errors(),
    }
