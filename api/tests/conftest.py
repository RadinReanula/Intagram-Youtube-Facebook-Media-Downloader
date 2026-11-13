import os
import tempfile
from pathlib import Path

_root = Path(tempfile.mkdtemp(prefix="media-downloader-tests-"))
os.environ["TEMP_DIR"] = str(_root / "tmp")
os.environ["DATABASE_PATH"] = str(_root / "jobs.sqlite")
os.environ["DOWNLOAD_SIGNING_SECRET"] = "test-secret"
os.environ["ADMIN_TOKEN"] = "test-admin-token"
os.environ["TURNSTILE_SECRET"] = ""
os.environ["CORS_ORIGINS"] = "http://localhost:3000"
os.environ["RATE_LIMIT"] = "1000/minute"
os.environ["MAX_DURATION_SECONDS"] = "30"
os.environ["MAX_FILE_SIZE_BYTES"] = "1000000"
os.environ["MAX_QUEUE_LENGTH"] = "2"
os.environ["MEMORY_THRESHOLD_PERCENT"] = "101"
os.environ["DISK_THRESHOLD_PERCENT"] = "101"
os.environ["DISK_LIMIT_BYTES"] = str(50 * 1024 * 1024 * 1024)
os.environ["FILE_TTL_SECONDS"] = "900"

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.analyze import get_metadata_cache


@pytest.fixture
def client():
    get_metadata_cache().clear()
    with TestClient(app) as test_client:
        app.state.store.reset()
        yield test_client
        app.state.store.reset()
