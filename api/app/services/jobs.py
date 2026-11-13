from __future__ import annotations

import re
from datetime import timedelta
from pathlib import Path

from app.config import get_settings
from app.errors import busy, not_found, unsupported
from app.jobs.queue import JobManager
from app.jobs.resources import ensure_capacity
from app.jobs.store import JobStore, iso, utcnow
from app.models import JobView
from app.security.tokens import sign_download
from app.security.urls import normalized_key, validate_public_url
from app.services.analyze import analyze_url, resolve_format

_FORMAT_ID = re.compile(r"^[A-Za-z0-9_+\-\[\]=<>./]{1,180}$")


def present(store: JobStore, job: dict) -> JobView:
    download_url = None
    if job["status"] == "ready" and job.get("file_path"):
        download_url = f"/api/jobs/{job['id']}/download?{sign_download(job['id'])}"
    return JobView(
        id=job["id"],
        status=job["status"],
        progress=float(job["progress"] or 0),
        position=store.position(job["id"]),
        error_code=job.get("error_code"),
        error_message=job.get("error_message"),
        file_name=job.get("file_name"),
        file_size=job.get("file_size"),
        download_url=download_url,
    )


async def create_download(store: JobStore, manager: JobManager, url: str, format_id: str, item_index: int | None) -> JobView:
    if not _FORMAT_ID.match(format_id):
        raise unsupported("That download option is not available for this link.")
    if item_index is not None and item_index < 0:
        raise unsupported("That item is not available.")
    cleaned = validate_public_url(url)
    result = await analyze_url(cleaned)
    resolve_format(result, format_id, item_index)
    settings = get_settings()
    if store.queued_count() >= settings.max_queue_length:
        raise busy("The server is busy. Try again later.", position=store.queued_count())
    ensure_capacity(settings)
    url_hash = normalized_key(cleaned)
    existing = store.find_ready(url_hash, format_id, item_index if format_id != "all" else None)
    if existing and Path(existing["file_path"]).is_file():
        job = store.create(
            url=cleaned,
            url_hash=url_hash,
            platform=result.platform,
            media_type=result.media_type,
            format_id=format_id,
            item_index=item_index,
            status="ready",
            title=result.title,
            file_path=existing["file_path"],
            file_name=existing["file_name"],
            file_size=existing["file_size"],
            ttl_seconds=settings.file_ttl_seconds,
        )
        return present(store, job)

    job = store.create(
        url=cleaned,
        url_hash=url_hash,
        platform=result.platform,
        media_type=result.media_type,
        format_id=format_id,
        item_index=item_index,
        status="queued",
        title=result.title,
    )
    await manager.submit(job["id"])
    created = store.get(job["id"])
    if created is None:
        raise not_found("The download could not be started.")
    return present(store, created)


def shorten_after_download(store: JobStore, job: dict) -> None:
    path = job.get("file_path")
    if not path:
        return
    now = utcnow()
    grace = iso(now + timedelta(seconds=180))
    if store.ready_using(path, now) <= 1:
        store.update(job["id"], downloaded_at=iso(now), expires_at=grace)
    else:
        store.update(job["id"], downloaded_at=iso(now))
