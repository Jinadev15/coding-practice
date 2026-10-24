"""Progress rules: topic completion, milestones, the activity heatmap and the daily planner."""
from __future__ import annotations

import math
from datetime import date, timedelta

from .content import MILESTONES, Language, Topic
from .db import DB

QUIZ_PASS = 0.70          # fraction of a topic quiz you must get right
QUIZ_SIZE = 10            # questions per topic quiz attempt
UNLOCK_SCORE = 0.75       # fraction of tests to unlock a problem's solution
TASK_KINDS = ("lesson_read", "quiz_passed", "problem_completed")
HEAT_KINDS = ("lesson_read", "mcq_answer", "submission")


class Progress:
    def __init__(self, db: DB):
        self.db = db

    # ------------------------------------------------------------ raw state
    def state(self, lang: str) -> dict:
        lessons = {r["topic"] for r in self.db.q("SELECT topic FROM lessons WHERE lang=?", (lang,))}
        quiz = {}
        for r in self.db.q("SELECT topic, MAX(CAST(correct AS REAL)/total) best, COUNT(*) n "
                           "FROM quiz_attempts WHERE lang=? AND total>0 GROUP BY topic", (lang,)):
            quiz[r["topic"]] = {"best": r["best"], "attempts": r["n"]}
        probs = {r["problem"]: dict(r) for r in
                 self.db.q("SELECT * FROM problem_status WHERE lang=?", (lang,))}
        return {"lessons": lessons, "quiz": quiz, "problems": probs}

    @staticmethod
    def problem_state(st: dict, pid: str) -> str:
        p = st["problems"].get(pid)
        if not p or not p["attempts"]:
            return "new"
        if p["completed_at"]:
            return "completed"
        if p["unlocked_at"]:
            return "unlocked"
        return "attempted"

    def topic_status(self, t: Topic, st: dict) -> dict:
        read = t.id in st["lessons"]
        q = st["quiz"].get(t.id)
        quiz_passed = bool(q and q["best"] >= QUIZ_PASS)
        done_probs = sum(self.problem_state(st, p) == "completed" for p in t.problems)
        has_content = bool(t.lesson_path or t.mcqs or t.problems)
        tasks_total = (1 if t.lesson_path else 0) + (1 if t.mcqs else 0) + len(t.problems)
        tasks_done = (1 if t.lesson_path and read else 0) + (1 if t.mcqs and quiz_passed else 0) \
            + done_probs
        if t.mcqs or t.problems:
            complete = (quiz_passed or not t.mcqs) and done_probs == len(t.problems)
        else:
            complete = bool(t.lesson_path and read)
        return {
            "read": read, "quiz_best": q["best"] if q else None, "quiz_passed": quiz_passed,
            "problems_done": done_probs, "problems_total": len(t.problems),
            "has_content": has_content, "complete": complete,
            "tasks_done": tasks_done, "tasks_total": tasks_total,
            "started": read or bool(q) or any(p in st["problems"] for p in t.problems),
        }

    def language_summary(self, lang: Language) -> dict:
        st = self.state(lang.id)
        statuses = {t.id: self.topic_status(t, st) for t in lang.topics}
        total = len(lang.topics)
        complete = sum(s["complete"] for s in statuses.values())
        pct = 100 * complete / total if total else 0
        milestones = []
        for n, need in MILESTONES.items():
            pids = lang.milestones.get(n, [])
            done = sum(self.problem_state(st, p) == "completed" for p in pids)
            milestones.append({"n": n, "requires_pct": need, "unlocked": pct >= need,
                               "problems": len(pids), "done": done})
        return {"statuses": statuses, "complete": complete, "total": total, "pct": pct,
                "with_content": sum(s["has_content"] for s in statuses.values()),
                "milestones": milestones, "state": st}

    # ------------------------------------------------------------ heatmap
    def heatmap(self, lang: str | None = None, days: int = 371) -> dict:
        start = (date.today() - timedelta(days=days - 1)).isoformat()
        sql = ("SELECT day, kind, COUNT(*) n FROM events WHERE day>=? AND kind IN "
               f"({','.join('?' * len(HEAT_KINDS))})")
        args: list = [start, *HEAT_KINDS]
        if lang:
            sql += " AND lang=?"
            args.append(lang)
        cells: dict[str, dict] = {}
        for r in self.db.q(sql + " GROUP BY day, kind", args):
            c = cells.setdefault(r["day"], {"total": 0})
            c[r["kind"]] = r["n"]
            c["total"] += r["n"]
        # streaks
        streak, d = 0, date.today()
        if d.isoformat() not in cells:
            d -= timedelta(days=1)
        while d.isoformat() in cells:
            streak += 1
            d -= timedelta(days=1)
        best, run = 0, 0
        for i in range(days):
            k = (date.today() - timedelta(days=days - 1 - i)).isoformat()
            run = run + 1 if k in cells else 0
            best = max(best, run)
        return {"start": start, "days": days, "cells": cells, "streak": streak,
                "best_streak": best, "active_days": len(cells)}

    # ------------------------------------------------------------ planner
    def tasks_by_day(self, lang: str, since: str) -> dict[str, int]:
        rows = self.db.q(
            f"SELECT day, COUNT(*) n FROM events WHERE lang=? AND day>=? AND kind IN "
            f"({','.join('?' * len(TASK_KINDS))}) GROUP BY day", (lang, since, *TASK_KINDS))
        return {r["day"]: r["n"] for r in rows}

    def plan(self, lang: Language, summary: dict | None = None) -> dict:
        summary = summary or self.language_summary(lang)
        st, statuses = summary["state"], summary["statuses"]
        today = date.today()
        first = self.db.q("SELECT MIN(day) d FROM events WHERE lang=? AND kind IN "
                          f"({','.join('?' * len(TASK_KINDS))})", (lang.id, *TASK_KINDS))[0]["d"]
        window = 14
        by_day = self.tasks_by_day(lang.id, (today - timedelta(days=window)).isoformat())
        done_today = by_day.get(today.isoformat(), 0)
        floor = int(self.db.get_setting(f"daily_min:{lang.id}", 4))
        avg = None
        if first and first < today.isoformat():
            start = max(date.fromisoformat(first), today - timedelta(days=window))
            span = (today - start).days            # full days before today
            past = sum(n for d, n in by_day.items() if d != today.isoformat())
            avg = past / span if span else None

        remaining_tasks = []
        for t in lang.topics:
            s = statuses[t.id]
            if t.lesson_path and not s["read"]:
                remaining_tasks.append({"kind": "lesson", "topic": t.id, "title": t.title})
            if t.mcqs and not s["quiz_passed"]:
                remaining_tasks.append({"kind": "quiz", "topic": t.id, "title": t.title})
            for pid in t.problems:
                if self.problem_state(st, pid) != "completed":
                    remaining_tasks.append({"kind": "problem", "topic": t.id, "problem": pid,
                                            "title": lang.problems[pid].title})
        for m in summary["milestones"]:
            if m["unlocked"]:
                for pid in lang.milestones.get(m["n"], []):
                    if self.problem_state(st, pid) != "completed":
                        remaining_tasks.append({"kind": "problem", "topic": f"milestone-{m['n']}",
                                                "problem": pid, "title": lang.problems[pid].title})
        remaining = len(remaining_tasks)

        pace_target = max(floor, math.ceil(avg * 1.1)) if avg else floor
        deadline = self.db.get_setting(f"deadline:{lang.id}")
        required = None
        if deadline:
            days_left = max(1, (date.fromisoformat(deadline) - today).days + 1)
            # tasks finished today still count toward today's quota
            required = math.ceil((remaining + done_today) / days_left)
        target = max(pace_target, required or 0)
        target = min(target, remaining + done_today)
        todo = max(0, target - done_today)
        eta = None
        if avg and avg > 0 and remaining:
            eta = (today + timedelta(days=math.ceil(remaining / avg))).isoformat()
        week = [{"day": (today - timedelta(days=i)).isoformat(),
                 "n": by_day.get((today - timedelta(days=i)).isoformat(), 0)}
                for i in range(6, -1, -1)]
        return {"lang": lang.id, "name": lang.name, "done_today": done_today, "target": target,
                "avg": round(avg, 2) if avg is not None else None, "floor": floor,
                "deadline": deadline, "required": required, "remaining": remaining,
                "eta": eta, "next": remaining_tasks[:todo or 0][:12], "week": week,
                "pct": round(summary["pct"], 1)}
