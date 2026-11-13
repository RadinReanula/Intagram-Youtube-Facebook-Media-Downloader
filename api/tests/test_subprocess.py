import asyncio
import sys

import pytest

from app.platforms.ytdlp import run_command


def test_command_runs_on_windows_selector_loop():
    if sys.platform != "win32":
        pytest.skip("the reload loop gap is specific to Windows")

    async def go():
        code, stdout, _stderr = await run_command([sys.executable, "-c", "print('ok')"], timeout=20)
        assert code == 0
        assert b"ok" in stdout

    loop = asyncio.SelectorEventLoop()
    try:
        loop.run_until_complete(go())
    finally:
        loop.close()


def test_crash_response_keeps_cors_headers(client):
    from app.main import app

    @app.get("/api/boom")
    async def boom():
        raise RuntimeError("boom")

    response = client.get("/api/boom", headers={"Origin": "http://localhost:3000"})
    assert response.status_code == 500
    assert response.json()["code"] == "blocked"
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
