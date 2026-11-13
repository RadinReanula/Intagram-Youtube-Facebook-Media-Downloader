from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class FormatOption(BaseModel):
    id: str
    label: str
    ext: str
    kind: Literal["video", "audio", "image"]
    filesize: int | None = None
    over_limit: bool = False
    warning: str | None = None


class MediaItem(BaseModel):
    index: int
    title: str | None = None
    thumbnail: str | None = None
    duration: float | None = None
    media_type: str
    formats: list[FormatOption]


class AnalyzeResult(BaseModel):
    platform: str
    media_type: str
    title: str | None = None
    thumbnail: str | None = None
    duration: float | None = None
    uploader: str | None = None
    items: list[MediaItem]
    can_download_all: bool = False
    cached: bool = False


class JobView(BaseModel):
    id: str
    status: str
    progress: float = 0
    position: int | None = None
    error_code: str | None = None
    error_message: str | None = None
    file_name: str | None = None
    file_size: int | None = None
    download_url: str | None = None


class JobCreate(BaseModel):
    url: str
    format_id: str = Field(min_length=1, max_length=180)
    item_index: int | None = None
    turnstile_token: str | None = None


class AnalyzeRequest(BaseModel):
    url: str = Field(min_length=1, max_length=2000)
    turnstile_token: str | None = None
