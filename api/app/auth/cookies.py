from __future__ import annotations

import os
import tempfile
from contextlib import contextmanager
from pathlib import Path

from app.config import get_settings


def session_dir() -> Path:
    path = get_settings().temp_dir / "sessions"
    path.mkdir(parents=True, exist_ok=True)
    return path


def job_cookie_path(job_id: str) -> Path:
    return session_dir() / f"{job_id}.txt"


def write_cookie_file(path: Path, instagram_settings: dict) -> None:
    cookies = instagram_settings.get("cookies") or {}
    if not isinstance(cookies, dict) or not cookies:
        authorization = (instagram_settings.get("authorization_data") or {}).get("sessionid")
        if authorization:
            cookies = {"sessionid": authorization}
    lines = ["# Netscape HTTP Cookie File"]
    for name, value in cookies.items():
        if value is None:
            continue
        lines.append(f".instagram.com\tTRUE\t/\tTRUE\t0\t{name}\t{value}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


def discard_cookie(path: Path) -> None:
    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass


def discard_job_cookie(job_id: str) -> None:
    discard_cookie(job_cookie_path(job_id))


def clear_session_files(job_ids: set[str]) -> None:
    for job_id in job_ids:
        discard_job_cookie(job_id)


@contextmanager
def temporary_cookie(instagram_settings: dict | None):
    if not instagram_settings:
        yield []
        return
    handle = tempfile.NamedTemporaryFile(prefix="ig-", suffix=".txt", dir=session_dir(), delete=False)
    path = Path(handle.name)
    handle.close()
    try:
        write_cookie_file(path, instagram_settings)
        yield ["--cookies", str(path)]
    finally:
        discard_cookie(path)
