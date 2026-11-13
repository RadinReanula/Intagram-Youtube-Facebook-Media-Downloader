from __future__ import annotations

import sqlite3
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def iso(value: datetime) -> str:
    return value.isoformat()


class JobStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row

    def init(self) -> None:
        with self._lock:
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA busy_timeout=3000")
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    url TEXT NOT NULL,
                    url_hash TEXT NOT NULL,
                    platform TEXT,
                    media_type TEXT,
                    format_id TEXT NOT NULL,
                    item_index INTEGER,
                    status TEXT NOT NULL,
                    progress REAL NOT NULL DEFAULT 0,
                    error_code TEXT,
                    error_message TEXT,
                    file_path TEXT,
                    file_name TEXT,
                    file_size INTEGER,
                    title TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    expires_at TEXT,
                    downloaded_at TEXT
                )
                """
            )
            columns = {row[1] for row in self._conn.execute("PRAGMA table_info(jobs)")}
            if "session_hash" not in columns:
                self._conn.execute("ALTER TABLE jobs ADD COLUMN session_hash TEXT NOT NULL DEFAULT ''")
            self._conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status, created_at)")
            self._conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_lookup ON jobs(url_hash, format_id, status)")
            self._conn.commit()

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    def create(
        self,
        *,
        url: str,
        url_hash: str,
        platform: str,
        media_type: str,
        format_id: str,
        item_index: int | None,
        status: str,
        title: str | None,
        session_hash: str = "",
        file_path: str | None = None,
        file_name: str | None = None,
        file_size: int | None = None,
        ttl_seconds: int | None = None,
    ) -> dict[str, Any]:
        now = utcnow()
        job_id = uuid4().hex
        expires = iso(now + timedelta(seconds=ttl_seconds)) if ttl_seconds else None
        with self._lock:
            self._conn.execute(
                """
                INSERT INTO jobs (
                    id, url, url_hash, platform, media_type, format_id, item_index, status,
                    progress, file_path, file_name, file_size, title, created_at, updated_at, expires_at, session_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job_id,
                    url,
                    url_hash,
                    platform,
                    media_type,
                    format_id,
                    item_index,
                    status,
                    100 if status == "ready" else 0,
                    file_path,
                    file_name,
                    file_size,
                    title,
                    iso(now),
                    iso(now),
                    expires,
                    session_hash,
                ),
            )
            self._conn.commit()
        job = self.get(job_id)
        assert job is not None
        return job

    def get(self, job_id: str) -> dict[str, Any] | None:
        with self._lock:
            row = self._conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return dict(row) if row else None

    def update(self, job_id: str, **fields: Any) -> None:
        allowed = {
            "status",
            "progress",
            "error_code",
            "error_message",
            "file_path",
            "file_name",
            "file_size",
            "title",
            "expires_at",
            "downloaded_at",
            "platform",
            "media_type",
        }
        unknown = set(fields) - allowed
        if unknown:
            raise ValueError(f"unknown job fields: {', '.join(sorted(unknown))}")
        fields["updated_at"] = iso(utcnow())
        columns = ", ".join(f"{key} = ?" for key in fields)
        values = list(fields.values()) + [job_id]
        with self._lock:
            self._conn.execute(f"UPDATE jobs SET {columns} WHERE id = ?", values)
            self._conn.commit()

    def queued_count(self) -> int:
        with self._lock:
            row = self._conn.execute("SELECT COUNT(*) AS n FROM jobs WHERE status = 'queued'").fetchone()
        return int(row["n"])

    def position(self, job_id: str) -> int | None:
        job = self.get(job_id)
        if not job or job["status"] != "queued":
            return None
        with self._lock:
            row = self._conn.execute(
                "SELECT COUNT(*) AS n FROM jobs WHERE status = 'queued' AND created_at <= ?",
                (job["created_at"],),
            ).fetchone()
        return int(row["n"])

    def queued_ids(self) -> list[str]:
        with self._lock:
            rows = self._conn.execute("SELECT id FROM jobs WHERE status = 'queued' ORDER BY created_at").fetchall()
        return [row["id"] for row in rows]

    def fail_interrupted(self) -> None:
        now = iso(utcnow())
        with self._lock:
            self._conn.execute(
                """
                UPDATE jobs
                SET status = 'failed', error_code = 'blocked',
                    error_message = 'The server restarted before this download finished.',
                    updated_at = ?
                WHERE status = 'processing'
                """,
                (now,),
            )
            self._conn.commit()

    def find_ready(self, url_hash: str, format_id: str, item_index: int | None, session_hash: str = "") -> dict[str, Any] | None:
        now = iso(utcnow())
        with self._lock:
            row = self._conn.execute(
                """
                SELECT * FROM jobs
                WHERE url_hash = ? AND format_id = ? AND IFNULL(item_index, -1) = ?
                  AND IFNULL(session_hash, '') = ?
                  AND status = 'ready' AND file_path IS NOT NULL
                  AND (expires_at IS NULL OR expires_at > ?)
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (url_hash, format_id, -1 if item_index is None else item_index, session_hash, now),
            ).fetchone()
        return dict(row) if row else None

    def counts(self) -> dict[str, int]:
        with self._lock:
            rows = self._conn.execute("SELECT status, COUNT(*) AS n FROM jobs GROUP BY status").fetchall()
        return {row["status"]: int(row["n"]) for row in rows}

    def recent_errors(self, limit: int = 20) -> list[dict[str, Any]]:
        with self._lock:
            rows = self._conn.execute(
                """
                SELECT id, platform, error_code, error_message, created_at
                FROM jobs
                WHERE status = 'failed'
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def expired(self, now: datetime) -> list[dict[str, Any]]:
        stamp = iso(now)
        with self._lock:
            rows = self._conn.execute(
                """
                SELECT * FROM jobs
                WHERE file_path IS NOT NULL AND (
                    (expires_at IS NOT NULL AND expires_at < ?)
                    OR status IN ('failed', 'cancelled')
                )
                """,
                (stamp,),
            ).fetchall()
        return [dict(row) for row in rows]

    def ready_using(self, file_path: str, now: datetime) -> int:
        with self._lock:
            row = self._conn.execute(
                """
                SELECT COUNT(*) AS n FROM jobs
                WHERE file_path = ? AND status = 'ready' AND (expires_at IS NULL OR expires_at > ?)
                """,
                (file_path, iso(now)),
            ).fetchone()
        return int(row["n"])

    def clear_file(self, job_id: str) -> None:
        self.update(job_id, file_path=None)

    def reset(self) -> None:
        with self._lock:
            self._conn.execute("DELETE FROM jobs")
            self._conn.commit()
