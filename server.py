#!/usr/bin/env python3
"""Coding Practice: a local study + judge server. Run: python3 server.py"""
from __future__ import annotations

import argparse
import json
import mimetypes
import random
import re
import traceback
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from app import judge as judge_mod
from app.content import Catalog
from app.db import DB, now
from app.progress import QUIZ_PASS, QUIZ_SIZE, UNLOCK_SCORE, Progress

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"

catalog = Catalog()
db = DB()
progress = Progress(db)


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
    if body.get("read", True):
        if not db.q("SELECT 1 FROM lessons WHERE lang=? AND topic=?", (lid, tid)):
            db.x("INSERT INTO lessons VALUES (?,?,?)", (lid, tid, now()))
            db.event(lid, "lesson_read", tid)
    else:
        db.x("DELETE FROM lessons WHERE lang=? AND topic=?", (lid, tid))
    return {"ok": True}


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
    allowed = set(p.starters)
    for name in files:
        need(name in allowed or re.fullmatch(r"[\w.\-]+", name), 400, f"Bad file name {name}")
    return {k: str(v) for k, v in files.items()}


def post_run(lid, pid, body):
    lang = lang_or_404(lid)
    p = lang.problems.get(pid)
    need(p)
    files = clean_files(lang, p, body)
    custom = body.get("custom_input")
    return judge_mod.judge(lang, p, files, samples_only=True,
                           custom_input=custom if custom is not None else None)


def post_submit(lid, pid, body):
    lang = lang_or_404(lid)
    p = lang.problems.get(pid)
    need(p)
    if p.milestone:
        need(milestone_unlocked(lang, p.milestone), 403, "Milestone locked")
    files = clean_files(lang, p, body)
    res = judge_mod.judge(lang, p, files)
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
    return {"lang": lid, "lang_name": lang.name, **m, "pct": s["pct"], "problems_list": probs}


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


class Handler(BaseHTTPRequestHandler):
    server_version = "CodingPractice/1.0"

    def log_message(self, fmt, *args):
        if args and isinstance(args[0], str) and "/api/" in args[0]:
            super().log_message(fmt, *args)

    def _send(self, status, data: bytes, ctype: str):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _json(self, status, obj):
        self._send(status, json.dumps(obj, default=str).encode(), "application/json")

    def _handle(self, method):
        url = urlparse(self.path)
        if url.path.startswith("/api/"):
            q = {k: v[0] for k, v in parse_qs(url.query).items()}
            body = {}
            if method in ("POST", "PUT"):
                n = int(self.headers.get("Content-Length") or 0)
                if n:
                    body = json.loads(self.rfile.read(n))
            for meth, pat, fn in ROUTES:
                m = re.fullmatch(pat, url.path)
                if m and meth == method:
                    try:
                        return self._json(200, fn(m.groups(), q, body))
                    except ApiError as e:
                        return self._json(e.status, {"error": str(e)})
                    except Exception as e:  # noqa: BLE001
                        traceback.print_exc()
                        return self._json(500, {"error": f"{type(e).__name__}: {e}"})
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--no-browser", action="store_true")
    a = ap.parse_args()
    langs = catalog.get()
    for lang in langs.values():
        for err in lang.errors:
            print(f"[content warning] {lang.id}: {err}")
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), Handler)
    url = f"http://127.0.0.1:{a.port}"
    print(f"Coding Practice running at {url}  ({', '.join(langs)})")
    if not a.no_browser:
        webbrowser.open(url)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
