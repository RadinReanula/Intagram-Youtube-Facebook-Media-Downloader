from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.auth.cookies import session_dir
from app.auth.sessions import assert_origin
from app.config import get_settings
from app.errors import ApiError
from app.jobs.cleanup import cleanup_loop
from app.jobs.queue import JobManager
from app.jobs.store import JobStore
from app.logging_setup import configure_logging, truncate_ip
from app.routes import admin, analyze, auth, health, jobs
from app.security.ratelimit import limiter

logger = logging.getLogger("media_downloader")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    settings.ensure_dirs()
    for leftover in session_dir().glob("*.txt"):
        leftover.unlink(missing_ok=True)
    store = JobStore(settings.database_path)
    store.init()
    store.fail_interrupted()
    manager = JobManager(store)
    app.state.store = store
    app.state.manager = manager
    for job_id in store.queued_ids():
        await manager.submit(job_id)
    task = asyncio.create_task(cleanup_loop(store, settings))
    if settings.download_signing_secret == "dev-change-me":
        logger.warning("DOWNLOAD_SIGNING_SECRET is still the default value")
    try:
        yield
    finally:
        task.cancel()
        for job_id in list(manager.tasks):
            await manager.cancel(job_id)
        store.close()


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)
    app = FastAPI(title="Media Downloader", lifespan=lifespan)
    app.state.limiter = limiter

    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
    app.add_exception_handler(ApiError, api_error_handler)
    app.add_exception_handler(RequestValidationError, validation_handler)
    app.middleware("http")(guard_errors)
    app.middleware("http")(origin_guard)
    app.middleware("http")(access_log)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list or ["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(analyze.router)
    app.include_router(jobs.router)
    app.include_router(admin.router)
    return app


def rate_limit_handler(_request: Request, _exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=429, content={"code": "busy", "message": "Too many requests. Try again later."})


def api_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, ApiError)
    return JSONResponse(status_code=exc.status, content={"code": exc.code, "message": exc.message, **exc.extra})


def validation_handler(_request: Request, _exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=400, content={"code": "invalid_link", "message": "That doesn't look like a valid link."})


async def access_log(request: Request, call_next):
    response = await call_next(request)
    host = request.client.host if request.client else "-"
    logger.info("%s %s %s %s", request.method, request.url.path, response.status_code, truncate_ip(host))
    return response


async def origin_guard(request: Request, call_next):
    try:
        assert_origin(request)
    except ApiError as exc:
        return JSONResponse(status_code=exc.status, content={"code": exc.code, "message": exc.message})
    return await call_next(request)


async def guard_errors(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception:
        logger.exception("unhandled error on %s", request.url.path)
        return JSONResponse(
            status_code=500,
            content={"code": "blocked", "message": "The media could not be fetched. Try again later."},
        )


app = create_app()
