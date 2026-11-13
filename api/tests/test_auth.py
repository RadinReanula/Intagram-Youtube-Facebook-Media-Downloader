import logging
import time
from pathlib import Path

from app.auth.cookies import temporary_cookie
from app.auth.instagram import reset_pending
from app.auth.sessions import sessions
from app.config import get_settings
from app.main import app


def _enable(monkeypatch):
    monkeypatch.setattr(get_settings(), "enable_instagram_login", True)
    sessions.reset()
    reset_pending()


def _headers(agent: str = "pytest-agent") -> dict[str, str]:
    return {"Origin": "http://localhost:3000", "User-Agent": agent}


async def _ok(username, password, code, challenge_id, user_agent):
    assert password
    return {"status": "ok", "username": username, "settings": {"cookies": {"sessionid": "session-value"}}}


def test_login_cookie_and_log_hygiene(client, monkeypatch, caplog):
    _enable(monkeypatch)
    monkeypatch.setattr("app.routes.auth.sign_in", _ok)
    caplog.set_level(logging.DEBUG)
    response = client.post(
        "/api/auth/instagram/login",
        json={"username": "ada", "password": "secret-pass"},
        headers=_headers(),
    )
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "username": "ada"}
    assert "secret-pass" not in response.text
    assert "session-value" not in response.text
    assert "secret-pass" not in caplog.text
    assert "md_session" in response.headers["set-cookie"]
    state = client.get("/api/auth/session", headers=_headers())
    assert state.json()["signed_in"] is True
    assert state.json()["username"] == "ada"


def test_origin_is_required(client, monkeypatch):
    _enable(monkeypatch)
    monkeypatch.setattr("app.routes.auth.sign_in", _ok)
    rejected = client.post(
        "/api/auth/instagram/login",
        json={"username": "ada", "password": "secret-pass"},
        headers={"Origin": "https://evil.example", "User-Agent": "pytest-agent"},
    )
    assert rejected.status_code == 403
    missing = client.post(
        "/api/auth/instagram/login",
        json={"username": "ada", "password": "secret-pass"},
        headers={"User-Agent": "pytest-agent"},
    )
    assert missing.status_code == 403


def test_login_rate_limit(client, monkeypatch):
    _enable(monkeypatch)
    monkeypatch.setattr("app.routes.auth.sign_in", _ok)
    last = None
    for _ in range(6):
        last = client.post(
            "/api/auth/instagram/login",
            json={"username": "ada", "password": "secret-pass"},
            headers=_headers(),
        )
    assert last is not None
    assert last.status_code == 429


def test_user_agent_and_idle_expiry(client, monkeypatch):
    _enable(monkeypatch)
    monkeypatch.setattr("app.routes.auth.sign_in", _ok)
    client.post(
        "/api/auth/instagram/login",
        json={"username": "ada", "password": "secret-pass"},
        headers=_headers("agent-a"),
    )
    other = client.get("/api/auth/session", headers=_headers("agent-b"))
    assert other.json()["signed_in"] is False
    token = client.cookies.get("md_session")
    assert token
    record = sessions._sessions[sessions.token_hash(token)]
    record.seen = time.time() - 10_000
    expired = client.get("/api/auth/session", headers=_headers("agent-a"))
    assert expired.json()["signed_in"] is False


def test_sessions_do_not_share_jobs_or_cache(client, monkeypatch):
    _enable(monkeypatch)
    calls = {"n": 0}

    async def fake_dump(url, extra=None):
        calls["n"] += 1
        return {
            "title": "Story",
            "uploader": "ada",
            "extractor_key": "Instagram",
            "ext": "mp4",
            "duration": 4,
            "vcodec": "avc1",
            "acodec": "mp4a",
        }

    monkeypatch.setattr("app.services.analyze.dump_info", fake_dump)
    monkeypatch.setattr("app.routes.auth.sign_in", _ok)
    story = "https://www.instagram.com/stories/ada/1/"
    blocked = client.post("/api/analyze", json={"url": story})
    assert blocked.status_code == 401
    assert blocked.json()["code"] == "login_required"

    client.post(
        "/api/auth/instagram/login",
        json={"username": "ada", "password": "secret-pass"},
        headers=_headers("agent-a"),
    )
    token_a = client.cookies.get("md_session")
    opened = client.post("/api/analyze", json={"url": story}, headers=_headers("agent-a"))
    assert opened.status_code == 200
    token_b = sessions.open_session(username="sam", settings_dict={"cookies": {"sessionid": "other"}}, user_agent="agent-b")
    client.cookies.set("md_session", token_b)
    again = client.post("/api/analyze", json={"url": story}, headers=_headers("agent-b"))
    assert again.status_code == 200
    assert calls["n"] == 2

    job = app.state.store.create(
        url=story,
        url_hash="story",
        platform="instagram",
        media_type="story",
        format_id="best",
        item_index=0,
        status="queued",
        title="Story",
        session_hash=sessions.token_hash(token_a),
    )
    hidden = client.get(f"/api/jobs/{job['id']}", headers=_headers("agent-b"))
    assert hidden.status_code == 404
    client.cookies.set("md_session", token_a)
    visible = client.get(f"/api/jobs/{job['id']}", headers=_headers("agent-a"))
    assert visible.status_code == 200


def test_cookie_file_is_removed_after_use(tmp_path, monkeypatch):
    monkeypatch.setattr(get_settings(), "temp_dir", tmp_path)
    with temporary_cookie({"cookies": {"sessionid": "abc"}}) as extra:
        path = Path(extra[1])
        assert path.is_file()
        assert "sessionid" in path.read_text(encoding="utf-8")
    assert not path.exists()
