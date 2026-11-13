from __future__ import annotations

import os
import re
import shutil
import zipfile
from datetime import timedelta
from pathlib import Path

from app.auth.cookies import job_cookie_path
from app.config import get_settings
from app.errors import ApiError, blocked
from app.jobs.store import JobStore, iso, utcnow
from app.platforms import get_platform
from app.platforms.ytdlp import run_command, ytdlp_base
from app.services.names import safe_filename

_PROGRESS = re.compile(r"\[download\]\s+(\d+(?:\.\d+)?)%")
_FRAGMENT = re.compile(r"\.f\d+\.")
_MEDIA_EXTS = {".mp4", ".webm", ".mkv", ".m4a", ".mp3", ".jpg", ".jpeg", ".png", ".webp", ".gif", ".opus", ".ogg"}
_VIDEO_EXTS = {".mp4", ".webm", ".mkv"}
_AUDIO_EXTS = {".m4a", ".mp3", ".opus", ".ogg", ".webm"}


def select_outputs(files: list[Path], format_id: str) -> tuple[list[Path], bool]:
    """Pick the finished media files. A zip is only for a multi-item download."""
    media = [path for path in files if path.suffix.lower() in _MEDIA_EXTS and not path.name.endswith(".part")]
    if not media:
        return [], False
    if format_id == "all":
        return media, len(media) > 1
    finished = [path for path in media if not _FRAGMENT.search(path.name)]
    if len(finished) == 1:
        return finished, False
    if len(finished) > 1:
        preferred = [path for path in finished if path.suffix.lower() in {".mp4", ".mp3"}]
        pool = preferred or finished
        return [max(pool, key=lambda path: path.stat().st_size)], False
    return [], False


def _largest(files: list[Path], suffixes: set[str]) -> Path | None:
    matches = [path for path in files if path.suffix.lower() in suffixes]
    if not matches:
        return None
    return max(matches, key=lambda path: path.stat().st_size)


async def run_download(job: dict, store: JobStore) -> None:
    settings = get_settings()
    work = settings.temp_dir / "work" / job["id"]
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True, exist_ok=True)
    template = str(work / "%(title).80s.%(ext)s")
    command = [
        *ytdlp_base(),
        "--newline",
        "--retries",
        "2",
        "--socket-timeout",
        "20",
        "--max-filesize",
        str(settings.max_file_size_bytes),
        "-o",
        template,
        *get_platform(job["platform"]).format_args(job["format_id"]),
    ]
    if job["format_id"] == "all":
        command.append("--yes-playlist")
    elif job["item_index"] is not None:
        command += ["--playlist-items", str(int(job["item_index"]) + 1)]
    else:
        command.append("--no-playlist")
    cookie = job_cookie_path(job["id"])
    if cookie.is_file():
        command += ["--cookies", str(cookie)]
    command.append(job["url"])

    last_percent = -1

    async def on_line(line: str) -> None:
        nonlocal last_percent
        match = _PROGRESS.search(line)
        if not match:
            return
        percent = int(float(match.group(1)))
        if percent == last_percent:
            return
        last_percent = percent
        store.update(job["id"], progress=percent)

    try:
        code, _stdout, stderr = await run_command(command, timeout=settings.job_timeout_seconds, job_id=job["id"], on_line=on_line)
    except ApiError:
        shutil.rmtree(work, ignore_errors=True)
        raise
    except FileNotFoundError as exc:
        shutil.rmtree(work, ignore_errors=True)
        raise blocked("The extraction tool is not available on the server.") from exc

    if code != 0:
        shutil.rmtree(work, ignore_errors=True)
        from app.platforms.ytdlp import map_ytdlp_error

        raise map_ytdlp_error(stderr.decode(errors="replace"))

    files = [path for path in work.rglob("*") if path.is_file() and not path.name.endswith(".part")]
    if not files:
        shutil.rmtree(work, ignore_errors=True)
        raise blocked("The download finished without a file.")

    chosen, bundle = select_outputs(files, job["format_id"])
    try:
        if not chosen and job["format_id"] != "all":
            chosen = await _merge_streams(work, files, settings)
            bundle = False
    except ApiError:
        shutil.rmtree(work, ignore_errors=True)
        raise
    if not chosen:
        shutil.rmtree(work, ignore_errors=True)
        raise blocked("The download finished without a file.")

    title = job.get("title") or "download"
    if bundle:
        produced = work / "bundle.zip"
        with zipfile.ZipFile(produced, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in chosen:
                archive.write(path, arcname=path.name)
        file_name = safe_filename(title, "zip")
    else:
        produced = chosen[0]
        ext = produced.suffix.lstrip(".") or "bin"
        file_name = safe_filename(title, ext)

    cache_dir = settings.temp_dir / "cache" / job["id"]
    cache_dir.mkdir(parents=True, exist_ok=True)
    destination = cache_dir / file_name
    _link_or_copy(produced, destination)
    shutil.rmtree(work, ignore_errors=True)
    expires = iso(utcnow() + timedelta(seconds=settings.file_ttl_seconds))
    store.update(
        job["id"],
        status="ready",
        progress=100,
        file_path=str(destination),
        file_name=file_name,
        file_size=destination.stat().st_size,
        expires_at=expires,
        error_code=None,
        error_message=None,
    )


def _link_or_copy(source: Path, destination: Path) -> None:
    try:
        os.link(source, destination)
    except OSError:
        shutil.copy2(source, destination)


async def _merge_streams(work: Path, files: list[Path], settings) -> list[Path]:
    video = _largest(files, _VIDEO_EXTS)
    audio = _largest([path for path in files if path != video], _AUDIO_EXTS)
    if video is None or audio is None:
        return [video] if video is not None else []
    ffmpeg = settings.ffmpeg_path
    if not (Path(ffmpeg).is_file() or shutil.which(ffmpeg)):
        raise blocked("The server can't combine the video and audio yet. Try again later.")
    output = work / "combined.mp4"
    code, _stdout, _stderr = await run_command(
        [ffmpeg, "-y", "-i", str(video), "-i", str(audio), "-c", "copy", "-shortest", str(output)],
        timeout=settings.job_timeout_seconds,
    )
    if code != 0 or not output.is_file():
        raise blocked("The server can't combine the video and audio yet. Try again later.")
    return [output]
