#!/usr/bin/env python3
"""Coding Practice: a local study + judge server. Run: python3 server.py"""
from __future__ import annotations

import argparse
import json
import os
import mimetypes
import random
import re
import threading
import traceback
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from app import judge as judge_mod
from app.auth import Accounts, AuthError
from app.content import CONTENT, Catalog
from app.db import DB, now
from app.progress import QUIZ_PASS, QUIZ_SIZE, UNLOCK_SCORE, Progress

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"

catalog = Catalog()
MAX_BODY = 2 << 20            # request bodies above 2 MB are refused
SESSION_COOKIE = "cp_session"

# Each request runs with the signed-in user's own database. `db` and `progress` below are proxies to
# the current request's objects, so the handlers read like single-user code.
_ctx = threading.local()
_local_db = None              # single-user mode: data/progress.db
accounts: Accounts | None = None   # set in shared (multi-user) mode
INVITE_CODE = os.environ.get("CP_INVITE_CODE", "")
_progress_for: dict[int, Progress] = {}


class _Current:
    def __init__(self, attr):
        self._attr = attr

    def __getattr__(self, name):
        return getattr(getattr(_ctx, self._attr), name)


db = _Current("db")
progress = _Current("progress")


def _bind_user(user_db: DB) -> None:
    _ctx.db = user_db
    _ctx.progress = _progress_for.setdefault(id(user_db), Progress(user_db))


class ApiError(Exception):
    def __init__(self, status: int, msg: str):
        super().__init__(msg)
        self.status = status


def need(cond, status=404, msg="Not found"):
    if not cond:
        raise ApiError(status, msg)


def lang_or_404(lid: str):
    langs = catalog.get()
    need(lid in langs, msg=f"Unknown language {lid}")
    return langs[lid]


def lang_brief(lang, summary=None):
    summary = summary or progress.language_summary(lang)
    c = lang.config
    return {"id": lang.id, "name": lang.name, "color": c.get("color", "#888"),
            "icon": c.get("icon", lang.id[:2].upper()), "pct": round(summary["pct"], 1),
            "complete": summary["complete"], "total": summary["total"],
            "with_content": summary["with_content"], "milestones": summary["milestones"],
            "problems": len(lang.problems),
            "mcqs": sum(len(t.mcqs) for t in lang.topics)}


def problem_brief(lang, pid, st):
    p = lang.problems[pid]
    ps = st["problems"].get(pid) or {}
    return {"id": pid, "title": p.title, "difficulty": p.difficulty,
            "tags": [t.strip() for t in p.meta.get("tags", "").split(",") if t.strip()],
            "state": progress.problem_state(st, pid), "best": ps.get("best_score", 0),
            "multi_file": len(p.starters) > 1}


def milestone_unlocked(lang, n) -> bool:
    s = progress.language_summary(lang)
    return any(m["n"] == n and m["unlocked"] for m in s["milestones"])


# ------------------------------------------------------------------ handlers

def get_languages(_q):
    out = []
    for lang in catalog.get().values():
        s = progress.language_summary(lang)
        b = lang_brief(lang, s)
        b["plan"] = progress.plan(lang, s)
        out.append(b)
    return out


def get_dashboard(q):
    langs = get_languages(q)
    hm = progress.heatmap(q.get("lang"))
    totals = db.q("SELECT kind, COUNT(*) n FROM events GROUP BY kind")
    recent = db.q("SELECT * FROM events WHERE kind IN ('lesson_read','quiz_passed',"
                  "'problem_completed','quiz_taken','submission') ORDER BY id DESC LIMIT 15")
    return {"languages": langs, "heatmap": hm, "totals": {r["kind"]: r["n"] for r in totals},
            "recent": [dict(r) for r in recent]}


def get_lang(lid):
    lang = lang_or_404(lid)
    s = progress.language_summary(lang)
    modules: list[dict] = []
    for t in lang.topics:
        if not modules or modules[-1]["name"] != t.module:
            modules.append({"name": t.module, "topics": []})
        st = s["statuses"][t.id]
        modules[-1]["topics"].append({"id": t.id, "title": t.title, "level": t.level,
                                      "summary": t.summary, "lesson": bool(t.lesson_path),
                                      "mcqs": len(t.mcqs), "problems": len(t.problems), **st})
    for m in modules:
        m["complete"] = sum(t["complete"] for t in m["topics"])
    return {**lang_brief(lang, s), "modules": modules, "errors": lang.errors,
            "plan": progress.plan(lang, s)}


def get_topic(lid, tid):
    lang = lang_or_404(lid)
    t = lang.topic_map.get(tid)
    need(t, msg="Unknown topic")
    st = progress.state(lid)
    idx = lang.topics.index(t)
    nav = lambda i: ({"id": lang.topics[i].id, "title": lang.topics[i].title}  # noqa: E731
                     if 0 <= i < len(lang.topics) else None)
    attempts = db.q("SELECT ts, correct, total FROM quiz_attempts WHERE lang=? AND topic=? "
                    "ORDER BY id DESC LIMIT 10", (lid, tid))
    return {"lang": lid, "lang_name": lang.name, "id": t.id, "title": t.title, "module": t.module,
            "level": t.level, "summary": t.summary,
            "lesson": t.lesson_path.read_text(encoding="utf-8") if t.lesson_path else None,
            "status": progress.topic_status(t, st), "mcqs": len(t.mcqs),
            "quiz_size": min(QUIZ_SIZE, len(t.mcqs)), "quiz_pass": QUIZ_PASS,
            "attempts": [dict(a) for a in attempts],
            "problems": [problem_brief(lang, p, st) for p in t.problems],
            "prev": nav(idx - 1), "next": nav(idx + 1)}


def post_lesson_read(lid, tid, body):
    lang = lang_or_404(lid)
    need(tid in lang.topic_map)
    with db.lock:
        _set_read(lid, tid, body)
    return {"ok": True}


def _set_read(lid, tid, body):
    if body.get("read", True):
        if not db.q("SELECT 1 FROM lessons WHERE lang=? AND topic=?", (lid, tid)):
            db.x("INSERT INTO lessons VALUES (?,?,?)", (lid, tid, now()))
            db.event(lid, "lesson_read", tid)
    else:
        db.x("DELETE FROM lessons WHERE lang=? AND topic=?", (lid, tid))


def get_quiz(lid, tid):
    lang = lang_or_404(lid)
    t = lang.topic_map.get(tid)
    need(t and t.mcqs, msg="No quiz for this topic yet")
    stats = {r["qid"]: r for r in db.q("SELECT * FROM mcq_stats WHERE lang=?", (lid,))}

    # Unseen and previously-missed questions first, then the rest, shuffled within groups.
    def weight(q):
        s = stats.get(q["id"])
        if not s or not s["seen"]:
            return 0
        return 1 if s["correct"] < s["seen"] else 2
    pool = sorted(t.mcqs, key=lambda q: (weight(q), random.random()))[:QUIZ_SIZE]
    random.shuffle(pool)
    out = []
    for q in pool:
        order = list(range(len(q["options"])))
        random.shuffle(order)
        out.append({"id": q["id"], "type": q["type"], "difficulty": q["difficulty"],
                    "question": q["question"], "code": q["code"], "multi": len(q["answer"]) > 1,
                    "options": [{"i": i, "text": q["options"][i]} for i in order]})
    return {"questions": out, "pass": QUIZ_PASS}


def grade_mcqs(lid, questions, answers):
    graded, correct = [], 0
    for q in questions:
        chosen = sorted(int(i) for i in answers.get(q["id"], []))
        ok = chosen == sorted(q["answer"])
        correct += ok
        db.x("INSERT INTO mcq_stats (lang, qid, seen, correct, last) VALUES (?,?,1,?,?) "
             "ON CONFLICT(lang, qid) DO UPDATE SET seen=seen+1, correct=correct+excluded.correct,"
             " last=excluded.last", (lid, q["id"], int(ok), now()))
        db.event(lid, "mcq_answer", q["id"], int(ok))
        graded.append({"id": q["id"], "chosen": chosen, "answer": q["answer"], "correct": ok,
                       "explanation": q["explanation"]})
    return graded, correct


def post_quiz(lid, tid, body):
    lang = lang_or_404(lid)
    t = lang.topic_map.get(tid)
    need(t and t.mcqs)
    bank = {q["id"]: q for q in t.mcqs}
    ids = [i for i in body.get("ids", []) if i in bank]
    need(ids, 400, "No questions submitted")
    graded, correct = grade_mcqs(lid, [bank[i] for i in ids], body.get("answers", {}))
    was_passed = progress.topic_status(t, progress.state(lid))["quiz_passed"]
    db.x("INSERT INTO quiz_attempts (lang, topic, ts, correct, total, details) VALUES "
         "(?,?,?,?,?,?)", (lid, tid, now(), correct, len(ids), json.dumps(graded)))
    db.event(lid, "quiz_taken", tid, correct / len(ids))
    passed = correct / len(ids) >= QUIZ_PASS
    if passed and not was_passed:
        db.event(lid, "quiz_passed", tid, correct / len(ids))
    return {"graded": graded, "correct": correct, "total": len(ids), "passed": passed}


def get_review(lid, q):
    """A mixed revision quiz from topics you have already studied, weakest questions first."""
    lang = lang_or_404(lid)
    st = progress.state(lid)
    studied = [t for t in lang.topics if t.mcqs and (t.id in st["lessons"] or t.id in st["quiz"])]
    need(studied, msg="Study a topic first; revision draws from topics you have started.")
    stats = {r["qid"]: r for r in db.q("SELECT * FROM mcq_stats WHERE lang=?", (lid,))}
    pool = [q for t in studied for q in t.mcqs]

    def acc(q):
        s = stats.get(q["id"])
        return (s["correct"] / s["seen"]) if s and s["seen"] else 0.5
    pool.sort(key=lambda x: (acc(x) + random.random() * 0.6))
    n = int(q.get("n", 15))
    pick = pool[:n]
    random.shuffle(pick)
    out = []
    for item in pick:
        order = list(range(len(item["options"])))
        random.shuffle(order)
        out.append({"id": item["id"], "type": item["type"], "difficulty": item["difficulty"],
                    "topic": lang.topic_map[item["topic"]].title, "question": item["question"],
                    "code": item["code"], "multi": len(item["answer"]) > 1,
                    "options": [{"i": i, "text": item["options"][i]} for i in order]})
    return {"questions": out}


def post_review(lid, body):
    lang = lang_or_404(lid)
    bank = {q["id"]: q for t in lang.topics for q in t.mcqs}
    ids = [i for i in body.get("ids", []) if i in bank]
    need(ids, 400, "No questions submitted")
    graded, correct = grade_mcqs(lid, [bank[i] for i in ids], body.get("answers", {}))
    return {"graded": graded, "correct": correct, "total": len(ids)}


def get_problem(lid, pid):
    lang = lang_or_404(lid)
    p = lang.problems.get(pid)
    need(p, msg="Unknown problem")
    if p.milestone:
        need(milestone_unlocked(lang, p.milestone), 403,
             f"Milestone {p.milestone} is locked. Complete more topics to unlock it.")
    st = progress.state(lid)
    ps = st["problems"].get(pid) or {}
    draft = db.q("SELECT files FROM drafts WHERE lang=? AND problem=?", (lid, pid))
    subs = db.q("SELECT id, ts, score, passed, total FROM submissions WHERE lang=? AND problem=? "
                "ORDER BY id DESC LIMIT 20", (lid, pid))
    unlocked = bool(ps.get("unlocked_at"))
    topic = lang.topic_map.get(p.topic)
    siblings = (topic.problems if topic else lang.milestones.get(p.milestone or 0, []))
    i = siblings.index(pid) if pid in siblings else -1
    return {
        "lang": lid, "lang_name": lang.name, "editor_mode": lang.config.get("editor_mode", "text"),
        "id": pid, "title": p.title, "difficulty": p.difficulty, "meta": p.meta,
        "topic": p.topic, "topic_title": topic.title if topic else f"Milestone {p.milestone}",
        "milestone": p.milestone, "statement": p.statement, "starters": p.starters,
        "hints": p.hints, "draft": json.loads(draft[0]["files"]) if draft else None,
        "samples": [{"input": t.input, "output": t.output} for t in p.tests if t.sample],
        "tests_total": len(p.tests), "state": progress.problem_state(st, pid),
        "best": ps.get("best_score", 0), "attempts": ps.get("attempts", 0),
        "unlock_score": UNLOCK_SCORE, "submissions": [dict(s) for s in subs],
        "solution": {"md": p.solution_md, "files": p.solution_files} if unlocked else None,
        "prev": siblings[i - 1] if i > 0 else None,
        "next": siblings[i + 1] if 0 <= i < len(siblings) - 1 else None,
    }


def clean_files(lang, p, body) -> dict[str, str]:
    files = body.get("files") or {}
    need(isinstance(files, dict) and files, 400, "No code submitted")
    need(len(files) <= 24, 400, "Too many files")
    allowed = set(p.starters)
    for name in files:
        need(name in allowed or (re.fullmatch(r"[\w.\-]+", name) and not name.startswith(".")),
             400, f"Bad file name {name}")
    return {k: str(v) for k, v in files.items()}


def post_run(lid, pid, body):
    lang = lang_or_404(lid)
    p = lang.problems.get(pid)
    need(p)
    if p.milestone:
        need(milestone_unlocked(lang, p.milestone), 403, "Milestone locked")
    files = clean_files(lang, p, body)
    custom = body.get("custom_input")
    return judge_mod.judge(lang, p, files, samples_only=True,
                           custom_input=str(custom) if custom is not None else None)


def post_submit(lid, pid, body):
    lang = lang_or_404(lid)
    p = lang.problems.get(pid)
    need(p)
    if p.milestone:
        need(milestone_unlocked(lang, p.milestone), 403, "Milestone locked")
    files = clean_files(lang, p, body)
    res = judge_mod.judge(lang, p, files)
    with db.lock:          # two tabs submitting at once must not lose an attempt or a completion
        return _record_submission(lang, p, files, res)


def _record_submission(lang, p, files, res):
    lid, pid = lang.id, p.id
    score = res["score"]
    db.x("INSERT INTO submissions (lang, problem, ts, score, passed, total, files, result) "
         "VALUES (?,?,?,?,?,?,?,?)", (lid, pid, now(), score, res["passed"], res["total"],
                                      json.dumps(files), json.dumps(res)[:200_000]))
    db.event(lid, "submission", pid, score)
    prev = db.q("SELECT * FROM problem_status WHERE lang=? AND problem=?", (lid, pid))
    prev = dict(prev[0]) if prev else {"best_score": 0, "attempts": 0, "unlocked_at": None,
                                       "completed_at": None}
    unlocked = prev["unlocked_at"] or (now() if score >= UNLOCK_SCORE else None)
    completed = prev["completed_at"] or (now() if score >= 1.0 else None)
    db.x("INSERT INTO problem_status VALUES (?,?,?,?,?,?) ON CONFLICT(lang, problem) DO UPDATE "
         "SET best_score=excluded.best_score, attempts=excluded.attempts, "
         "unlocked_at=excluded.unlocked_at, completed_at=excluded.completed_at",
         (lid, pid, max(prev["best_score"], score), prev["attempts"] + 1, unlocked, completed))
    if completed and not prev["completed_at"]:
        db.event(lid, "problem_completed", pid, 1)
    res["state"] = "completed" if completed else ("unlocked" if unlocked else "attempted")
    res["newly_unlocked"] = bool(unlocked and not prev["unlocked_at"])
    res["newly_completed"] = bool(completed and not prev["completed_at"])
    if unlocked:
        res["solution"] = {"md": p.solution_md, "files": p.solution_files}
    return res


def put_draft(lid, pid, body):
    lang = lang_or_404(lid)
    p = lang.problems.get(pid)
    need(p)
    files = clean_files(lang, p, body)
    db.x("INSERT INTO drafts VALUES (?,?,?,?) ON CONFLICT(lang, problem) DO UPDATE SET "
         "files=excluded.files, updated=excluded.updated", (lid, pid, json.dumps(files), now()))
    return {"ok": True}


def get_submission(lid, sid):
    rows = db.q("SELECT * FROM submissions WHERE lang=? AND id=?", (lid, int(sid)))
    need(rows)
    r = dict(rows[0])
    return {**r, "files": json.loads(r["files"]), "result": json.loads(r["result"])}


def get_milestone(lid, n):
    lang = lang_or_404(lid)
    n = int(n)
    s = progress.language_summary(lang)
    m = next((m for m in s["milestones"] if m["n"] == n), None)
    need(m)
    probs = [problem_brief(lang, p, s["state"]) for p in lang.milestones.get(n, [])] \
        if m["unlocked"] else []
    guide = CONTENT / lid / "milestones" / f"milestone-{n}.md"
    return {"lang": lid, "lang_name": lang.name, **m, "pct": s["pct"], "problems_list": probs,
            "guide": guide.read_text(encoding="utf-8") if guide.exists() else ""}


def get_problems(lid, q):
    lang = lang_or_404(lid)
    st = progress.state(lid)
    out = []
    for t in lang.topics:
        for pid in t.problems:
            b = problem_brief(lang, pid, st)
            b.update(topic=t.id, topic_title=t.title, module=t.module)
            out.append(b)
    return out


def get_settings(_q):
    langs = catalog.get()
    return {lid: {"deadline": db.get_setting(f"deadline:{lid}"),
                  "daily_min": db.get_setting(f"daily_min:{lid}", 4)} for lid in langs}


def post_settings(body):
    for lid, vals in body.items():
        lang_or_404(lid)
        if "deadline" in vals:
            v = vals["deadline"] or None
            need(v is None or re.fullmatch(r"\d{4}-\d{2}-\d{2}", v), 400, "Bad date")
            db.set_setting(f"deadline:{lid}", v)
        if "daily_min" in vals:
            db.set_setting(f"daily_min:{lid}", max(1, min(200, int(vals["daily_min"]))))
    return get_settings({})


ROUTES = [
    ("GET", r"/api/dashboard", lambda m, q, b: get_dashboard(q)),
    ("GET", r"/api/languages", lambda m, q, b: get_languages(q)),
    ("GET", r"/api/settings", lambda m, q, b: get_settings(q)),
    ("POST", r"/api/settings", lambda m, q, b: post_settings(b)),
    ("GET", r"/api/lang/([\w-]+)", lambda m, q, b: get_lang(*m)),
    ("GET", r"/api/lang/([\w-]+)/problems", lambda m, q, b: get_problems(m[0], q)),
    ("GET", r"/api/topic/([\w-]+)/([\w-]+)", lambda m, q, b: get_topic(*m)),
    ("POST", r"/api/lesson/([\w-]+)/([\w-]+)", lambda m, q, b: post_lesson_read(*m, b)),
    ("GET", r"/api/quiz/([\w-]+)/([\w-]+)", lambda m, q, b: get_quiz(*m)),
    ("POST", r"/api/quiz/([\w-]+)/([\w-]+)", lambda m, q, b: post_quiz(*m, b)),
    ("GET", r"/api/review/([\w-]+)", lambda m, q, b: get_review(m[0], q)),
    ("POST", r"/api/review/([\w-]+)", lambda m, q, b: post_review(m[0], b)),
    ("GET", r"/api/problem/([\w-]+)/([\w.-]+)", lambda m, q, b: get_problem(*m)),
    ("POST", r"/api/run/([\w-]+)/([\w.-]+)", lambda m, q, b: post_run(*m, b)),
    ("POST", r"/api/submit/([\w-]+)/([\w.-]+)", lambda m, q, b: post_submit(*m, b)),
    ("PUT", r"/api/draft/([\w-]+)/([\w.-]+)", lambda m, q, b: put_draft(*m, b)),
    ("GET", r"/api/submission/([\w-]+)/(\d+)", lambda m, q, b: get_submission(*m)),
    ("GET", r"/api/milestone/([\w-]+)/(\d)", lambda m, q, b: get_milestone(*m)),
]


# ------------------------------------------------------------------ accounts

def get_me(_q, user):
    if not accounts:
        return {"multi_user": False, "user": None}
    return {"multi_user": True, "user": user and user["username"], "signup": bool(INVITE_CODE)}


AUTH_FREE = {"/api/auth/me", "/api/auth/login", "/api/auth/signup", "/api/auth/logout"}


class Handler(BaseHTTPRequestHandler):
    server_version = "CodingPractice/1.0"

    def log_message(self, fmt, *args):
        if args and isinstance(args[0], str) and "/api/" in args[0]:
            super().log_message(fmt, *args)

    def _send(self, status, data: bytes, ctype: str, headers: dict | None = None):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "same-origin")
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def _json(self, status, obj, headers=None):
        self._send(status, json.dumps(obj, default=str).encode(), "application/json", headers)

    # -------------------------------------------------------------- sessions
    def _client(self) -> str:
        # behind a tunnel or reverse proxy the real client is in the forwarding header
        return (self.headers.get("CF-Connecting-IP") or self.headers.get("X-Forwarded-For", "").split(",")[0].strip()
                or self.client_address[0])

    def _token(self) -> str | None:
        for part in (self.headers.get("Cookie") or "").split(";"):
            k, _, v = part.strip().partition("=")
            if k == SESSION_COOKIE:
                return v
        return None

    def _cookie(self, token: str, max_age: int) -> dict:
        secure = "; Secure" if self.headers.get("X-Forwarded-Proto") == "https" else ""
        return {"Set-Cookie": f"{SESSION_COOKIE}={token}; Path=/; HttpOnly; SameSite=Strict; "
                              f"Max-Age={max_age}{secure}"}

    def _auth(self, path, method, body):
        """Handles /api/auth/*; returns (status, payload, headers)."""
        user = accounts.session_user(self._token()) if accounts else None
        if path == "/api/auth/me":
            return 200, get_me({}, user), None
        if method != "POST" or not accounts:
            return 404, {"error": "No such endpoint"}, None
        try:
            if path == "/api/auth/signup":
                if not INVITE_CODE or not secrets_equal(str(body.get("invite", "")), INVITE_CODE):
                    raise AuthError("Invalid invite code.")
                accounts.create_user(str(body.get("username", "")), str(body.get("password", "")))
            if path in ("/api/auth/signup", "/api/auth/login"):
                token = accounts.login(str(body.get("username", "")), str(body.get("password", "")), self._client())
                return 200, {"ok": True}, self._cookie(token, 30 * 86400)
            if path == "/api/auth/logout":
                if self._token():
                    accounts.logout(self._token())
                return 200, {"ok": True}, self._cookie("", 0)
        except AuthError as e:
            return 400, {"error": str(e)}, None
        return 404, {"error": "No such endpoint"}, None

    def _handle(self, method):
        url = urlparse(self.path)
        if url.path.startswith("/api/"):
            # Single-user mode has no sign-in, so only answer requests addressed to this machine by name.
            # This blocks DNS-rebinding pages (Host: evil.example) from driving the judge.
            if not accounts and (self.headers.get("Host") or "").rsplit(":", 1)[0] not in ("127.0.0.1", "localhost", "[::1]"):
                return self._json(403, {"error": "Use http://127.0.0.1 to reach this server"})
            q = {k: v[0] for k, v in parse_qs(url.query).items()}
            body = {}
            if method in ("POST", "PUT"):
                # Cross-site forms can't send JSON or a foreign Origin without CORS, which we never allow.
                # (A tunnel may rewrite Host to the loopback address; SameSite=Strict cookies still apply there.)
                origin, host = self.headers.get("Origin"), self.headers.get("Host") or ""
                proxied = host.split(":")[0] in ("127.0.0.1", "localhost", "[::1]")
                if origin and not proxied and urlparse(origin).netloc not in (host, self.headers.get("X-Forwarded-Host")):
                    return self._json(403, {"error": "Cross-origin request refused"})
                if "application/json" not in (self.headers.get("Content-Type") or ""):
                    return self._json(415, {"error": "Send JSON"})
                try:
                    n = int(self.headers.get("Content-Length") or 0)
                except ValueError:
                    n = -1
                if n < 0 or n > MAX_BODY:
                    self.close_connection = True
                    return self._json(413, {"error": "Request too large"})
                if n:
                    try:
                        body = json.loads(self.rfile.read(n))
                    except ValueError:
                        return self._json(400, {"error": "Invalid JSON"})
                    if not isinstance(body, dict):
                        return self._json(400, {"error": "Invalid JSON"})
            if url.path.startswith("/api/auth/"):
                status, payload, headers = self._auth(url.path, method, body)
                return self._json(status, payload, headers)
            if accounts:
                user = accounts.session_user(self._token())
                if not user:
                    return self._json(401, {"error": "Please sign in."})
                _bind_user(accounts.db_for(user))
            else:
                _bind_user(_local_db)
            for meth, pat, fn in ROUTES:
                m = re.fullmatch(pat, url.path)
                if m and meth == method:
                    try:
                        return self._json(200, fn(m.groups(), q, body))
                    except ApiError as e:
                        return self._json(e.status, {"error": str(e)})
                    except Exception:  # noqa: BLE001
                        traceback.print_exc()
                        return self._json(500, {"error": "Internal error. The details were logged on the server."})
            return self._json(404, {"error": "No such endpoint"})
        if method != "GET":
            return self._json(405, {"error": "Method not allowed"})
        path = (STATIC / url.path.lstrip("/")).resolve()
        if url.path in ("", "/") or not path.is_file() or STATIC.resolve() not in path.parents:
            path = STATIC / "index.html"
        ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self._send(200, path.read_bytes(), ctype)

    def do_GET(self):
        self._handle("GET")

    def do_POST(self):
        self._handle("POST")

    def do_PUT(self):
        self._handle("PUT")

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()


def secrets_equal(a: str, b: str) -> bool:
    import hmac
    return hmac.compare_digest(a.encode(), b.encode())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--no-browser", action="store_true")
    ap.add_argument("--host", default="127.0.0.1",
                    help="address to listen on (keep 127.0.0.1 behind a tunnel; 0.0.0.0 exposes it to the LAN)")
    ap.add_argument("--multi-user", action="store_true",
                    help="require sign-in; each account gets its own progress database")
    a = ap.parse_args()
    global accounts, _local_db
    if a.multi_user:
        if not judge_mod.sandbox_enabled():
            raise SystemExit("--multi-user needs the bubblewrap sandbox (bwrap) so friends' code can't touch "
                             "this machine. Install bubblewrap, or check that unprivileged user namespaces work.")
        accounts = Accounts()
        if not accounts.users():
            print("No accounts yet. Create one with:  python3 tools/users.py add <name> --admin --mine")
    else:
        _local_db = DB()
        if a.host not in ("127.0.0.1", "localhost", "::1"):
            raise SystemExit("Refusing to listen on a public address without --multi-user (sign-in + sandbox).")
    langs = catalog.get()
    for lang in langs.values():
        for err in lang.errors:
            print(f"[content warning] {lang.id}: {err}")
    srv = ThreadingHTTPServer((a.host, a.port), Handler)
    srv.daemon_threads = True
    url = f"http://127.0.0.1:{a.port}"
    mode = "shared, sign-in required" if accounts else "single user"
    print(f"Coding Practice running at {url}  ({', '.join(langs)}; {mode}; "
          f"sandbox {'on' if judge_mod.sandbox_enabled() else 'off'})")
    if not a.no_browser:
        webbrowser.open(url)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
