from __future__ import annotations

import asyncio
import json
import os
import shutil
import signal
import subprocess
import time
from pathlib import Path

from app.config import get_settings
from app.errors import blocked, limit_exceeded, not_found, private_content, unsupported

_PROCESSES: dict[str, subprocess.Popen] = {}


def map_ytdlp_error(text: str):
    lower = text.lower()
    if "max-filesize" in lower or "file is larger" in lower:
        return limit_exceeded("This file is larger than the allowed size.")
    if any(word in lower for word in ("private", "login", "sign in", "log in", "cookies", "registered users", "empty media response")):
        return private_content()
    if any(word in lower for word in ("unavailable", "not found", "404", "removed", "deleted", "does not exist", "no video")):
        return not_found()
    if any(word in lower for word in ("rate-limit", "rate limit", "too many requests", "429", "blocked", "forbidden")):
        return blocked()
    if "unsupported url" in lower or "unsupported" in lower:
        return unsupported("This link is not supported.")
    if "live event" in lower or "is live" in lower:
        return unsupported("Live streams are not supported.")
    return blocked("The media could not be fetched. Try again later.")


def tool_prefix() -> list[str]:
    if os.name != "posix":
        return []
    prefix: list[str] = []
    if shutil.which("nice"):
        prefix += ["nice", "-n", "10"]
    if shutil.which("ionice"):
        prefix += ["ionice", "-c", "3"]
    return prefix


def ytdlp_base(extra: list[str] | None = None) -> list[str]:
    settings = get_settings()
    command = [*tool_prefix(), settings.ytdlp_path, "--ignore-config", "--no-warnings"]
    ffmpeg = settings.ffmpeg_path
    if Path(ffmpeg).is_absolute():
        command += ["--ffmpeg-location", ffmpeg]
    if extra:
        command += extra
    return command


def kill_process(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=5)
            return
        except (ProcessLookupError, OSError):
            return
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(process.pid)],
            capture_output=True,
            check=False,
        )
        return
    process.kill()


async def terminate(job_id: str) -> None:
    process = _PROCESSES.get(job_id)
    if process is not None:
        await asyncio.to_thread(kill_process, process)


def _execute(command: list[str], timeout: float, job_id: str | None, on_line_sync) -> tuple[int, bytes, bytes]:
    popen_kwargs: dict = {"stdout": subprocess.PIPE, "stderr": subprocess.PIPE}
    if os.name == "posix":
        popen_kwargs["start_new_session"] = True
    process = subprocess.Popen(command, **popen_kwargs)
    if job_id:
        _PROCESSES[job_id] = process
    stdout_parts: list[bytes] = []
    deadline = time.monotonic() + timeout
    try:
        assert process.stdout is not None
        while True:
            if time.monotonic() > deadline:
                kill_process(process)
                raise TimeoutError
            line = process.stdout.readline()
            if not line:
                break
            stdout_parts.append(line)
            if on_line_sync is not None:
                on_line_sync(line.decode(errors="replace"))
        remaining = max(1.0, deadline - time.monotonic())
        try:
            stderr = process.stderr.read() if process.stderr is not None else b""
            code = process.wait(timeout=remaining)
        except subprocess.TimeoutExpired:
            kill_process(process)
            raise TimeoutError from None
        return code, b"".join(stdout_parts), stderr or b""
    finally:
        if job_id:
            _PROCESSES.pop(job_id, None)
        if process.poll() is None:
            kill_process(process)


async def run_command(command: list[str], timeout: float, job_id: str | None = None, on_line=None) -> tuple[int, bytes, bytes]:
    loop = asyncio.get_running_loop()

    def on_line_sync(text: str) -> None:
        if on_line is None:
            return
        future = asyncio.run_coroutine_threadsafe(on_line(text), loop)
        future.result(timeout=5)

    try:
        return await asyncio.to_thread(_execute, command, timeout, job_id, on_line_sync if on_line else None)
    except TimeoutError:
        raise limit_exceeded("This download took too long and was stopped.") from None
    except FileNotFoundError as exc:
        raise blocked("The extraction tool is not available on the server.") from exc


async def dump_info(url: str, extra: list[str] | None = None) -> dict:
    command = [
        *ytdlp_base(extra),
        "--no-playlist",
        "--dump-single-json",
        "--skip-download",
        "--socket-timeout",
        "15",
        "--no-progress",
        "--retries",
        "1",
        url,
    ]
    code, stdout, stderr = await run_command(command, timeout=40)
    text = stderr.decode(errors="replace")
    if code != 0 or not stdout.strip():
        raise map_ytdlp_error(text or stdout.decode(errors="replace") or "empty response")
    try:
        return json.loads(stdout.decode(errors="replace"))
    except json.JSONDecodeError:
        raise map_ytdlp_error(text or "invalid response") from None
