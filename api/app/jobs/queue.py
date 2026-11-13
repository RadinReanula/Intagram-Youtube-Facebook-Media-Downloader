from __future__ import annotations

import asyncio
import logging
import shutil

from app.auth.cookies import discard_job_cookie
from app.config import get_settings
from app.errors import ApiError
from app.jobs.runner import run_download
from app.jobs.store import JobStore
from app.platforms.ytdlp import terminate

logger = logging.getLogger(__name__)


class JobManager:
    def __init__(self, store: JobStore) -> None:
        settings = get_settings()
        self.store = store
        self.semaphore = asyncio.Semaphore(max(1, settings.max_concurrent_jobs))
        self.tasks: dict[str, asyncio.Task[None]] = {}

    async def submit(self, job_id: str) -> None:
        self.tasks[job_id] = asyncio.create_task(self._worker(job_id), name=f"job-{job_id}")

    async def _worker(self, job_id: str) -> None:
        settings = get_settings()
        try:
            async with self.semaphore:
                job = self.store.get(job_id)
                if not job or job["status"] in {"cancelled", "ready", "failed"}:
                    return
                self.store.update(job_id, status="processing", progress=0)
                current = self.store.get(job_id)
                if current is None:
                    return
                await run_download(current, self.store)
        except asyncio.CancelledError:
            await terminate(job_id)
            shutil.rmtree(settings.temp_dir / "work" / job_id, ignore_errors=True)
            job = self.store.get(job_id)
            if job and job["status"] not in {"ready", "failed", "cancelled"}:
                self.store.update(job_id, status="cancelled", error_message="The download was cancelled.")
            raise
        except ApiError as exc:
            logger.info("job %s failed code=%s", job_id, exc.code)
            self.store.update(job_id, status="failed", error_code=exc.code, error_message=exc.message)
        except Exception:
            logger.exception("job %s failed", job_id)
            self.store.update(
                job_id,
                status="failed",
                error_code="blocked",
                error_message="The download failed. Try again.",
            )
        finally:
            discard_job_cookie(job_id)
            self.tasks.pop(job_id, None)

    async def cancel(self, job_id: str) -> None:
        job = self.store.get(job_id)
        if not job or job["status"] not in {"queued", "processing"}:
            return
        self.store.update(job_id, status="cancelled", error_message="The download was cancelled.")
        await terminate(job_id)
        task = self.tasks.get(job_id)
        if task is not None:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
