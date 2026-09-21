from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


class JobQueue:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kind TEXT NOT NULL,
                    status TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    result TEXT NOT NULL DEFAULT '{}',
                    error TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            con.commit()

    def add(self, kind: str, payload: dict) -> int:
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as con:
            cur = con.execute(
                "INSERT INTO jobs(kind,status,payload,result,created_at) VALUES(?,?,?,?,?)",
                (kind, "queued", json.dumps(payload, ensure_ascii=False), "{}", now),
            )
            con.commit()
            return int(cur.lastrowid)

    def list(self) -> list[dict]:
        with self._connect() as con:
            rows = con.execute(
                "SELECT id,kind,status,payload,result,error,created_at FROM jobs ORDER BY id DESC"
            ).fetchall()
        return [
            {
                "id": r[0],
                "kind": r[1],
                "status": r[2],
                "payload": json.loads(r[3]),
                "result": json.loads(r[4]),
                "error": r[5],
                "created_at": r[6],
            }
            for r in rows
        ]

    def update(self, job_id: int, status: str, result: dict | None = None, error: str | None = None):
        with self._connect() as con:
            con.execute(
                "UPDATE jobs SET status=?,result=?,error=? WHERE id=?",
                (status, json.dumps(result or {}, ensure_ascii=False), error, job_id),
            )
            con.commit()
