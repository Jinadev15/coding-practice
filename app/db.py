"""SQLite storage for your progress. One file: data/progress.db."""
from __future__ import annotations

import json
import sqlite3
import threading
from datetime import date, datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "progress.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY, ts TEXT NOT NULL, day TEXT NOT NULL, lang TEXT NOT NULL,
    kind TEXT NOT NULL, ref TEXT NOT NULL, value REAL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS events_day ON events(day);
CREATE TABLE IF NOT EXISTS lessons (
    lang TEXT, topic TEXT, read_at TEXT, PRIMARY KEY (lang, topic)
);
CREATE TABLE IF NOT EXISTS quiz_attempts (
    id INTEGER PRIMARY KEY, lang TEXT, topic TEXT, ts TEXT, correct INTEGER, total INTEGER,
    details TEXT
);
CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY, lang TEXT, problem TEXT, ts TEXT, score REAL, passed INTEGER,
    total INTEGER, files TEXT, result TEXT
);
CREATE TABLE IF NOT EXISTS problem_status (
    lang TEXT, problem TEXT, best_score REAL DEFAULT 0, attempts INTEGER DEFAULT 0,
    unlocked_at TEXT, completed_at TEXT, PRIMARY KEY (lang, problem)
);
CREATE TABLE IF NOT EXISTS drafts (
    lang TEXT, problem TEXT, files TEXT, updated TEXT, PRIMARY KEY (lang, problem)
);
CREATE TABLE IF NOT EXISTS mcq_stats (
    lang TEXT, qid TEXT, seen INTEGER DEFAULT 0, correct INTEGER DEFAULT 0, last TEXT,
    PRIMARY KEY (lang, qid)
);
CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT);
"""

_lock = threading.Lock()


def now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def today() -> str:
    return date.today().isoformat()


class DB:
    def __init__(self, path: Path = DB_PATH):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def q(self, sql: str, args=()) -> list[sqlite3.Row]:
        with _lock:
            return self.conn.execute(sql, args).fetchall()

    def x(self, sql: str, args=()) -> int:
        with _lock:
            cur = self.conn.execute(sql, args)
            self.conn.commit()
            return cur.lastrowid

    def event(self, lang: str, kind: str, ref: str, value: float = 0) -> None:
        self.x("INSERT INTO events (ts, day, lang, kind, ref, value) VALUES (?,?,?,?,?,?)",
               (now(), today(), lang, kind, ref, value))

    # settings ----------------------------------------------------------
    def get_setting(self, key: str, default=None):
        rows = self.q("SELECT value FROM settings WHERE key=?", (key,))
        return json.loads(rows[0]["value"]) if rows else default

    def set_setting(self, key: str, value) -> None:
        self.x("INSERT INTO settings (key, value) VALUES (?, ?) "
               "ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, json.dumps(value)))
