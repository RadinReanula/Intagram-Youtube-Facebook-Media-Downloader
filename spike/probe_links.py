"""Metadata-only extraction probe. Does not download media files.

Run from the repo root:
    .venv/bin/python spike/probe_links.py
    .venv/Scripts/python.exe spike/probe_links.py
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

SAMPLES = [
    ("youtube", "video", "https://www.youtube.com/watch?v=jNQXAC9IVRw"),
    ("youtube", "short", "https://www.youtube.com/shorts/aqz-KE-bpKQ"),
    ("instagram", "reel", "https://www.instagram.com/reel/C8Q3p0sR0aA/"),
    ("instagram", "post", "https://www.instagram.com/p/C8Q3p0sR0aA/"),
    ("instagram", "story", "https://www.instagram.com/stories/instagram/"),
    ("facebook", "video", "https://www.facebook.com/facebook/videos/10153231379946729/"),
    ("facebook", "reel", "https://www.facebook.com/reel/10153231379946729/"),
]

TIMEOUT_SECONDS = 45


def ytdlp() -> str:
    exe = shutil.which("yt-dlp")
    if exe:
        return exe
    candidate = Path(sys.executable).with_name("yt-dlp.exe" if sys.platform == "win32" else "yt-dlp")
    if candidate.exists():
        return str(candidate)
    raise SystemExit("yt-dlp is not installed in this environment")


def probe(url: str) -> dict:
    started = time.perf_counter()
    command = [
        ytdlp(),
        "--dump-single-json",
        "--skip-download",
        "--no-playlist",
        "--no-warnings",
        "--socket-timeout",
        "20",
        "--retries",
        "1",
        url,
    ]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "elapsed_s": round(time.perf_counter() - started, 2), "error": "timeout"}

    elapsed = round(time.perf_counter() - started, 2)
    if completed.returncode != 0:
        err = (completed.stderr or completed.stdout or "").strip().splitlines()
        return {"ok": False, "elapsed_s": elapsed, "error": err[-1] if err else f"exit {completed.returncode}"}

    try:
        data = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {"ok": False, "elapsed_s": elapsed, "error": "invalid json"}

    formats = data.get("formats") or []
    return {
        "ok": True,
        "elapsed_s": elapsed,
        "title": data.get("title"),
        "uploader": data.get("uploader") or data.get("channel"),
        "duration": data.get("duration"),
        "is_live": bool(data.get("is_live")),
        "extractor": data.get("extractor"),
        "format_count": len(formats),
        "has_video": any(f.get("vcodec") not in (None, "none") for f in formats),
        "has_audio": any(f.get("acodec") not in (None, "none") for f in formats),
        "thumbnail": bool(data.get("thumbnail")),
    }


def main() -> None:
    results = []
    for platform, media_type, url in SAMPLES:
        print(f"probing {platform}/{media_type} ...", flush=True)
        row = {"platform": platform, "media_type": media_type, "url": url, **probe(url)}
        results.append(row)
        print(json.dumps(row, ensure_ascii=False), flush=True)

    out = Path(__file__).with_name("probe_results.json")
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
