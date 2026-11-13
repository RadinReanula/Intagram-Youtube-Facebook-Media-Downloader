from __future__ import annotations

import logging
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.config import Settings
from app.jobs.store import JobStore, utcnow

logger = logging.getLogger(__name__)


def cleanup_once(store: JobStore, settings: Settings) -> int:
    now = utcnow()
    removed = 0
    seen: set[str] = set()
    for job in store.expired(now):
        path = job.get("file_path")
        if not path or path in seen:
            continue
        seen.add(path)
        if store.ready_using(path, now) > 0:
            if job["status"] != "ready":
                store.clear_file(job["id"])
            continue
        file_path = Path(path)
        try:
            if file_path.is_file():
                file_path.unlink(missing_ok=True)
            elif file_path.is_dir():
                shutil.rmtree(file_path, ignore_errors=True)
            work = settings.temp_dir / "work" / job["id"]
            if work.exists():
                shutil.rmtree(work, ignore_errors=True)
            store.clear_file(job["id"])
            removed += 1
        except OSError:
            logger.warning("could not remove temporary file for job %s", job["id"])
    _remove_empty(settings.temp_dir / "work")
    _remove_stale_work(settings.temp_dir / "work", now - timedelta(seconds=settings.file_ttl_seconds))
    return removed


def _remove_empty(path: Path) -> None:
    if not path.exists():
        return
    for child in path.iterdir():
        if child.is_dir() and not any(child.iterdir()):
            child.rmdir()


def _remove_stale_work(path: Path, cutoff: datetime) -> None:
    if not path.exists():
        return
    for child in path.iterdir():
        if not child.is_dir():
            continue
        try:
            modified = datetime.fromtimestamp(child.stat().st_mtime, timezone.utc)
        except OSError:
            continue
        if modified < cutoff:
            shutil.rmtree(child, ignore_errors=True)


async def cleanup_loop(store: JobStore, settings: Settings) -> None:
    import asyncio

    while True:
        await asyncio.sleep(60)
        try:
            cleanup_once(store, settings)
        except Exception:
            logger.exception("temporary file cleanup failed")
