"""Accounts for sharing the app with friends (server.py --multi-user).

Accounts and login sessions live in data/accounts.db. Each user's progress is a separate SQLite
file, data/users/<username>.db, with the same schema as the single-user data/progress.db, so one
person's activity can never touch another's and concurrent use needs no cross-user locking.
"""
from __future__ import annotations

import hashlib
import hmac
import re
import secrets
import sqlite3
import threading
import time
from pathlib import Path

from .db import DB, DB_PATH, now

DATA = DB_PATH.parent
USERS_DIR = DATA / "users"
SESSION_DAYS = 30
USERNAME_RE = re.compile(r"[a-z0-9_]{3,24}")
OWNER_DB_SETTING = "owner"          # the account that keeps using data/progress.db

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY, pw_hash TEXT NOT NULL, created TEXT NOT NULL,
    is_admin INTEGER DEFAULT 0, uses_main_db INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS sessions (
    token_hash TEXT PRIMARY KEY, username TEXT NOT NULL, created REAL NOT NULL, expires REAL NOT NULL
);
"""


class AuthError(Exception):
    pass


def _hash_pw(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    dk = hashlib.scrypt(password.encode(), salt=salt, n=2 ** 14, r=8, p=1, dklen=32)
    return f"scrypt${salt.hex()}${dk.hex()}"


def _check_pw(password: str, stored: str) -> bool:
    try:
        _, salt, _dk = stored.split("$")
    except ValueError:
        return False
    return hmac.compare_digest(_hash_pw(password, bytes.fromhex(salt)), stored)


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class Accounts:
    def __init__(self, path: Path = DATA / "accounts.db"):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.executescript(SCHEMA)
        self.lock = threading.Lock()
        self._dbs: dict[str, DB] = {}
        self._fails: dict[str, list[float]] = {}

    # ---------------------------------------------------------------- users
    def create_user(self, username: str, password: str, is_admin=False, uses_main_db=False) -> None:
        username = username.strip().lower()
        if not USERNAME_RE.fullmatch(username):
            raise AuthError("Username must be 3-24 characters: lowercase letters, digits or _.")
        if len(password) < 8:
            raise AuthError("Password must be at least 8 characters.")
        with self.lock:
            if self.conn.execute("SELECT 1 FROM users WHERE username=?", (username,)).fetchone():
                raise AuthError("That username is taken.")
            self.conn.execute("INSERT INTO users VALUES (?,?,?,?,?)",
                              (username, _hash_pw(password), now(), int(is_admin), int(uses_main_db)))
            self.conn.commit()

    def set_password(self, username: str, password: str) -> None:
        if len(password) < 8:
            raise AuthError("Password must be at least 8 characters.")
        with self.lock:
            cur = self.conn.execute("UPDATE users SET pw_hash=? WHERE username=?", (_hash_pw(password), username))
            self.conn.execute("DELETE FROM sessions WHERE username=?", (username,))
            self.conn.commit()
        if not cur.rowcount:
            raise AuthError("No such user.")

    def users(self) -> list[dict]:
        with self.lock:
            return [dict(r) for r in self.conn.execute(
                "SELECT username, created, is_admin, uses_main_db FROM users ORDER BY created")]

    def delete_user(self, username: str) -> None:
        with self.lock:
            self.conn.execute("DELETE FROM users WHERE username=?", (username,))
            self.conn.execute("DELETE FROM sessions WHERE username=?", (username,))
            self.conn.commit()

    # ---------------------------------------------------------------- login
    def _throttled(self, key: str) -> bool:
        cutoff = time.time() - 900
        recent = [t for t in self._fails.get(key, []) if t > cutoff]
        self._fails[key] = recent
        return len(recent) >= 8

    def login(self, username: str, password: str, client: str) -> str:
        username = (username or "").strip().lower()
        keys = (f"u:{username}", f"ip:{client}")
        with self.lock:
            if any(self._throttled(k) for k in keys):
                raise AuthError("Too many failed attempts. Wait 15 minutes and try again.")
            row = self.conn.execute("SELECT pw_hash FROM users WHERE username=?", (username,)).fetchone()
        # hash even for unknown users so response time doesn't reveal which usernames exist
        ok = _check_pw(password or "", row["pw_hash"] if row else _hash_pw("x"))
        if not (row and ok):
            with self.lock:
                for k in keys:
                    self._fails.setdefault(k, []).append(time.time())
            raise AuthError("Wrong username or password.")
        token = secrets.token_urlsafe(32)
        t = time.time()
        with self.lock:
            self.conn.execute("DELETE FROM sessions WHERE expires<?", (t,))
            self.conn.execute("INSERT INTO sessions VALUES (?,?,?,?)",
                              (_token_hash(token), username, t, t + SESSION_DAYS * 86400))
            self.conn.commit()
            self._fails.pop(f"u:{username}", None)
        return token

    def logout(self, token: str) -> None:
        with self.lock:
            self.conn.execute("DELETE FROM sessions WHERE token_hash=?", (_token_hash(token),))
            self.conn.commit()

    def session_user(self, token: str | None) -> dict | None:
        if not token:
            return None
        with self.lock:
            row = self.conn.execute(
                "SELECT u.username, u.is_admin, u.uses_main_db FROM sessions s JOIN users u USING (username) "
                "WHERE s.token_hash=? AND s.expires>?", (_token_hash(token), time.time())).fetchone()
        return dict(row) if row else None

    # ---------------------------------------------------------------- per-user storage
    def db_for(self, user: dict) -> DB:
        name = user["username"]
        with self.lock:
            if name not in self._dbs:
                path = DB_PATH if user.get("uses_main_db") else USERS_DIR / f"{name}.db"
                self._dbs[name] = DB(path)
            return self._dbs[name]
