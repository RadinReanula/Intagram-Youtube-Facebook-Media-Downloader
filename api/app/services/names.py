from __future__ import annotations

import re

_UNSAFE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def safe_filename(title: str | None, ext: str) -> str:
    cleaned = _UNSAFE.sub("", title or "")
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .")
    cleaned = cleaned[:80] or "download"
    suffix = ext.lower().lstrip(".") or "bin"
    return f"{cleaned}.{suffix}"
