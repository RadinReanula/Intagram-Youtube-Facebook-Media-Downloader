from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.responses import FileResponse

from app.errors import not_found
from app.models import JobCreate, JobView
from app.security.ratelimit import limit_value, limiter
from app.security.tokens import verify_download
from app.security.turnstile import verify_turnstile
from app.services.jobs import create_download, present, same_session, shorten_after_download

router = APIRouter()


@router.post("/api/jobs", response_model=JobView)
@limiter.limit(limit_value)
async def create_job(request: Request, body: JobCreate) -> JobView:
    await verify_turnstile(body.turnstile_token, request)
    return await create_download(request.app.state.store, request.app.state.manager, body.url, body.format_id, body.item_index, request)


@router.get("/api/jobs/{job_id}", response_model=JobView)
@limiter.limit("240/minute")
async def read_job(request: Request, job_id: str) -> JobView:
    job = request.app.state.store.get(job_id)
    if job is None:
        raise not_found("That download was not found.")
    same_session(job, request)
    return present(request.app.state.store, job)


@router.delete("/api/jobs/{job_id}", response_model=JobView)
@limiter.limit(limit_value)
async def cancel_job(request: Request, job_id: str) -> JobView:
    store = request.app.state.store
    job = store.get(job_id)
    if job is None:
        raise not_found("That download was not found.")
    same_session(job, request)
    await request.app.state.manager.cancel(job_id)
    current = store.get(job_id)
    if current is None:
        raise not_found("That download was not found.")
    return present(store, current)


@router.get("/api/jobs/{job_id}/download")
@limiter.limit(limit_value)
async def download_job(request: Request, job_id: str, expires: str, token: str, background: BackgroundTasks) -> FileResponse:
    verify_download(job_id, expires, token)
    store = request.app.state.store
    job = store.get(job_id)
    if job is None or job["status"] != "ready" or not job.get("file_path"):
        raise not_found("That download is not ready.")
    same_session(job, request)
    path = Path(job["file_path"])
    if not path.is_file():
        raise not_found("That file is no longer available. Start the download again.")
    background.add_task(shorten_after_download, store, job)
    return FileResponse(path, filename=job.get("file_name") or path.name)
