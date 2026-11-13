from __future__ import annotations

import time
from typing import TypeVar

T = TypeVar("T")


class TtlCache:
    def __init__(self) -> None:
        self._items: dict[str, tuple[float, object]] = {}

    def get(self, key: str) -> object | None:
        item = self._items.get(key)
        if item is None:
            return None
        expires, value = item
        if expires < time.monotonic():
            self._items.pop(key, None)
            return None
        return value

    def set(self, key: str, value: object, ttl_seconds: float) -> None:
        self._items[key] = (time.monotonic() + ttl_seconds, value)

    def clear(self) -> None:
        self._items.clear()
