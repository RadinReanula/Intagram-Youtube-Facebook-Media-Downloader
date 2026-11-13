from __future__ import annotations

import os
import shutil
from pathlib import Path

from fastapi import APIRouter

from app.config import get_settings

router = APIRouter()


def _tool_ready(command: str) -> bool:
    path = Path(command)
    if path.is_absolute():
        return path.exists()
    return shutil.which(command) is not None


@router.get("/api/health")
async def health() -> dict[str, object]:
    settings = get_settings()
    temp_ok = settings.temp_dir.exists() and os.access(settings.temp_dir, os.W_OK)
    ytdlp_ok = _tool_ready(settings.ytdlp_path)
    ffmpeg_ok = _tool_ready(settings.ffmpeg_path)
    return {
        "status": "ok" if temp_ok and ytdlp_ok else "degraded",
        "ytdlp": ytdlp_ok,
        "ffmpeg": ffmpeg_ok,
        "temp_writable": temp_ok,
    }
