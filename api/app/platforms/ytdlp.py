from __future__ import annotations

import asyncio
import contextlib
import json
import os
import shutil
import signal
from pathlib import Path

from app.config import get_settings
from app.errors import blocked, limit_exceeded, not_found, private_content, unsupported

_PROCESSES: dict[str, asyncio.subprocess.Process] = {}


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


def session_kwargs() -> dict:
    if os.name == "posix":
        return {"start_new_session": True}
    return {}


def ytdlp_base() -> list[str]:
    settings = get_settings()
    command = [*tool_prefix(), settings.ytdlp_path, "--ignore-config", "--no-warnings"]
    ffmpeg = settings.ffmpeg_path
    if Path(ffmpeg).is_absolute():
        command += ["--ffmpeg-location", ffmpeg]
    return command


async def _kill(process: asyncio.subprocess.Process) -> None:
    if process.returncode is not None:
        return
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGKILL)
            return
        except ProcessLookupError:
            return
    if os.name == "nt":
        subprocess_kill = await asyncio.create_subprocess_exec(
            "taskkill",
            "/F",
            "/T",
            "/PID",
            str(process.pid),
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await subprocess_kill.wait()
        return
    process.kill()


async def terminate(job_id: str) -> None:
    process = _PROCESSES.get(job_id)
    if process is not None:
        await _kill(process)


async def run_command(command: list[str], timeout: float, job_id: str | None = None, on_line=None) -> tuple[int, bytes, bytes]:
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        **session_kwargs(),
    )
    if job_id:
        _PROCESSES[job_id] = process
    if process.stdout is not None:
        process.stdout._limit = 16 * 1024 * 1024
    if process.stderr is not None:
        process.stderr._limit = 16 * 1024 * 1024

    async def read_stdout() -> bytes:
        chunks: list[bytes] = []
        assert process.stdout is not None
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            chunks.append(line)
            if on_line is not None:
                await on_line(line.decode(errors="replace"))
        return b"".join(chunks)

    try:
        stdout_task = asyncio.create_task(read_stdout())
        stderr_task = asyncio.create_task(process.stderr.read() if process.stderr else _empty())
        stdout, stderr = await asyncio.wait_for(asyncio.gather(stdout_task, stderr_task), timeout=timeout)
        code = await process.wait()
    except TimeoutError:
        await _kill(process)
        if process.returncode is None:
            with contextlib.suppress(Exception):
                await process.wait()
        raise limit_exceeded("This download took too long and was stopped.") from None
    finally:
        if job_id:
            _PROCESSES.pop(job_id, None)
    return code, stdout, stderr or b""


async def _empty() -> bytes:
    return b""


async def dump_info(url: str) -> dict:
    command = [
        *ytdlp_base(),
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
    try:
        code, stdout, stderr = await run_command(command, timeout=40)
    except FileNotFoundError as exc:
        raise blocked("The extraction tool is not available on the server.") from exc
    text = stderr.decode(errors="replace")
    if code != 0 or not stdout.strip():
        raise map_ytdlp_error(text or stdout.decode(errors="replace") or "empty response")
    try:
        return json.loads(stdout.decode(errors="replace"))
    except json.JSONDecodeError:
        raise map_ytdlp_error(text or "invalid response") from None
