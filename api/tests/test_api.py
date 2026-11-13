from datetime import timedelta

import asyncio

from app.config import get_settings
from app.jobs.store import iso, utcnow


YOUTUBE = {
    "id": "abc",
    "title": "Sample video",
    "uploader": "Ada",
    "duration": 12,
    "thumbnail": "https://i.ytimg.com/vi/abc/hqdefault.jpg",
    "extractor_key": "Youtube",
    "formats": [
        {"format_id": "18", "ext": "mp4", "height": 360, "vcodec": "avc1", "acodec": "mp4a", "filesize": 1000},
        {"format_id": "137", "ext": "mp4", "height": 1080, "vcodec": "avc1", "acodec": "none", "filesize": 5000},
        {"format_id": "140", "ext": "m4a", "height": None, "vcodec": "none", "acodec": "mp4a", "filesize": 400},
    ],
}

CAROUSEL = {
    "title": "A post",
    "uploader": "Sam",
    "extractor_key": "Instagram",
    "entries": [
        {"title": "Clip", "ext": "mp4", "duration": 4, "vcodec": "avc1", "acodec": "mp4a", "thumbnail": "https://example.com/a.jpg"},
        {"title": "Photo", "ext": "jpg", "vcodec": "none", "thumbnail": "https://example.com/b.jpg"},
    ],
}


def test_analyze_lists_youtube_qualities_and_audio(client, monkeypatch):
    async def fake_dump(_url: str) -> dict:
        return YOUTUBE

    monkeypatch.setattr("app.services.analyze.dump_info", fake_dump)
    response = client.post("/api/analyze", json={"url": " https://www.youtube.com/watch?v=jNQXAC9IVRw "})
    assert response.status_code == 200
    body = response.json()
    assert body["platform"] == "youtube"
    assert body["media_type"] == "video"
    assert body["uploader"] == "Ada"
    labels = [item["label"] for item in body["items"][0]["formats"]]
    assert "360p" in labels
    assert "1080p" in labels
    assert "Audio only" in labels

    cached = client.post("/api/analyze", json={"url": "https://www.youtube.com/watch?v=jNQXAC9IVRw"})
    assert cached.json()["cached"] is True


def test_rejects_playlist_and_foreign_host(client):
    playlist = client.post("/api/analyze", json={"url": "https://www.youtube.com/playlist?list=PL123456"})
    assert playlist.status_code == 400
    assert playlist.json()["code"] == "unsupported"
    foreign = client.post("/api/analyze", json={"url": "https://example.com/video"})
    assert foreign.status_code == 400
    assert foreign.json()["code"] == "unsupported"


def test_carousel_can_download_one_or_all(client, monkeypatch):
    async def fake_dump(_url: str) -> dict:
        return CAROUSEL

    monkeypatch.setattr("app.services.analyze.dump_info", fake_dump)
    response = client.post("/api/analyze", json={"url": "https://www.instagram.com/p/ABC123/"})
    body = response.json()
    assert body["can_download_all"] is True
    assert len(body["items"]) == 2
    assert body["items"][1]["formats"][0]["kind"] == "image"


def test_over_limit_is_flagged_and_rejected(client, monkeypatch):
    async def fake_dump(_url: str) -> dict:
        return {**YOUTUBE, "duration": 999}

    monkeypatch.setattr("app.services.analyze.dump_info", fake_dump)
    analyzed = client.post("/api/analyze", json={"url": "https://youtu.be/jNQXAC9IVRw"}).json()
    option = analyzed["items"][0]["formats"][0]
    assert option["over_limit"] is True
    created = client.post("/api/jobs", json={"url": "https://youtu.be/jNQXAC9IVRw", "format_id": option["id"]})
    assert created.status_code == 400
    assert created.json()["code"] == "limit_exceeded"


def test_job_lifecycle_with_cached_reuse(client, monkeypatch):
    async def fake_dump(_url: str) -> dict:
        return YOUTUBE

    async def fake_run(job: dict, store) -> None:
        path = get_settings().temp_dir / "cache" / job["id"]
        path.mkdir(parents=True, exist_ok=True)
        target = path / "sample.mp4"
        target.write_bytes(b"12345")
        store.update(
            job["id"],
            status="ready",
            progress=100,
            file_path=str(target),
            file_name="Sample video.mp4",
            file_size=5,
            expires_at=iso(utcnow() + timedelta(hours=1)),
        )

    monkeypatch.setattr("app.services.analyze.dump_info", fake_dump)
    monkeypatch.setattr("app.jobs.queue.run_download", fake_run)

    async def immediate(self, job_id: str) -> None:
        await self._worker(job_id)

    monkeypatch.setattr("app.jobs.queue.JobManager.submit", immediate)

    analyzed = client.post("/api/analyze", json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}).json()
    audio = next(item for item in analyzed["items"][0]["formats"] if item["id"] == "audio")
    created = client.post(
        "/api/jobs",
        json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "format_id": audio["id"]},
    )
    assert created.status_code == 200
    body = created.json()
    assert body["status"] == "ready"
    assert body["download_url"]

    downloaded = client.get(body["download_url"])
    assert downloaded.status_code == 200
    assert downloaded.content == b"12345"
    assert "Sample" in downloaded.headers["content-disposition"]

    again = client.post(
        "/api/jobs",
        json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "format_id": audio["id"]},
    )
    assert again.json()["status"] == "ready"
    assert again.json()["id"] != body["id"]

    missing = client.get(f"/api/jobs/{body['id']}/download?expires=1&token=nope")
    assert missing.status_code == 400


def test_cancel_queued_job(client, monkeypatch):
    async def fake_dump(_url: str) -> dict:
        return YOUTUBE

    async def hang(_job: dict, _store) -> None:
        await asyncio.Event().wait()

    monkeypatch.setattr("app.services.analyze.dump_info", fake_dump)
    monkeypatch.setattr("app.jobs.queue.run_download", hang)

    analyzed = client.post("/api/analyze", json={"url": "https://www.youtube.com/watch?v=abcdefghijk"}).json()
    option = next(item for item in analyzed["items"][0]["formats"] if item["kind"] == "audio")
    created = client.post(
        "/api/jobs",
        json={"url": "https://www.youtube.com/watch?v=abcdefghijk", "format_id": option["id"]},
    )
    job_id = created.json()["id"]
    cancelled = client.delete(f"/api/jobs/{job_id}")
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"


def test_admin_stats_requires_token(client):
    denied = client.get("/api/admin/stats")
    assert denied.status_code == 401
    allowed = client.get("/api/admin/stats", headers={"Authorization": "Bearer test-admin-token"})
    assert allowed.status_code == 200
    assert "resources" in allowed.json()
    assert "limits" in allowed.json()


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert "ytdlp" in response.json()
