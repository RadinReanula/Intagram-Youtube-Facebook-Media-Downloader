from __future__ import annotations

import shutil
from pathlib import Path

import psutil

from app.config import Settings
from app.errors import busy


def directory_size(path: Path) -> int:
    if not path.exists():
        return 0
    total = 0
    for item in path.rglob("*"):
        if item.is_file():
            try:
                total += item.stat().st_size
            except OSError:
                continue
    return total


def ensure_capacity(settings: Settings) -> None:
    memory = psutil.virtual_memory().percent
    if memory >= settings.memory_threshold_percent:
        raise busy("The server is busy because memory is high. Try again later.")
    target = settings.temp_dir if settings.temp_dir.exists() else settings.temp_dir.parent
    if target.exists():
        usage = shutil.disk_usage(target)
        if usage.total and (usage.used / usage.total) * 100 >= settings.disk_threshold_percent:
            raise busy("The server is busy because disk space is low. Try again later.")
    if directory_size(settings.temp_dir) >= settings.disk_limit_bytes:
        raise busy("The server is busy because temporary storage is full. Try again later.")


def snapshot(settings: Settings) -> dict[str, float | int]:
    memory = psutil.virtual_memory()
    target = settings.temp_dir if settings.temp_dir.exists() else Path(".")
    usage = shutil.disk_usage(target if target.exists() else Path("."))
    return {
        "memory_percent": round(memory.percent, 1),
        "memory_available_mb": int(memory.available / (1024 * 1024)),
        "disk_percent": round((usage.used / usage.total) * 100, 1) if usage.total else 0,
        "disk_free_mb": int(usage.free / (1024 * 1024)),
        "temp_bytes": directory_size(settings.temp_dir),
    }
