#!/usr/bin/env python3
"""Check all content: CSV structure, MCQ answers, and that every reference solution
passes 100% of its own tests. Run after adding content:

    python3 tools/validate.py            # everything
    python3 tools/validate.py python     # one language
    python3 tools/validate.py python py-two-sum   # one problem
"""
from __future__ import annotations

import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.content import Catalog  # noqa: E402
from app.judge import judge  # noqa: E402


def check_problem(lang, p) -> list[str]:
    errs = []
    if not p.statement.strip():
        errs.append("missing ## Statement")
    if not p.tests:
        errs.append("no tests")
    if not any(t.sample for t in p.tests):
        errs.append("no sample test")
    if not p.solution_files:
        errs.append("no reference solution")
        return errs
    if not p.solution_md.strip():
        errs.append("no solution explanation")
    if set(p.solution_files) - set(p.starters) and len(p.starters) > 1:
        errs.append(f"solution files {set(p.solution_files) - set(p.starters)} not in starters")
    files = {**p.starters, **p.solution_files}
    try:
        r = judge(lang, p, files)
    except Exception as e:  # noqa: BLE001
        return errs + [f"judge error: {e}"]
    if not r["compiled"]:
        errs.append("reference solution does not compile:\n" + r["compile_output"])
    elif r["passed"] != r["total"]:
        bad = [x for x in r["results"] if not x["passed"]]
        detail = "; ".join(f"test {x['index']} {x['status']}" for x in bad[:5])
        first = next((x for x in bad if "got" in x), None)
        if first:
            detail += f"\n      input: {first['input'][:200]!r}\n      expected: {first['expected'][:200]!r}" \
                      f"\n      got: {first['got'][:200]!r}\n      stderr: {first['stderr'][:300]}"
        errs.append(f"reference passes {r['passed']}/{r['total']}: {detail}")
    # Starter code must not already pass (it would be a free completion).
    if not errs and len(p.tests) > 1:
        try:
            s = judge(lang, p, dict(p.starters))
            if s["compiled"] and s["passed"] == s["total"]:
                errs.append("starter code already passes all tests")
        except Exception:  # noqa: BLE001
            pass
    return errs


def main() -> int:
    only_lang = sys.argv[1] if len(sys.argv) > 1 else None
    only_prob = sys.argv[2] if len(sys.argv) > 2 else None
    langs = Catalog().get()
    failures = 0
    for lang in langs.values():
        if only_lang and lang.id != only_lang:
            continue
        print(f"== {lang.name}: {len(lang.topics)} topics, "
              f"{sum(1 for t in lang.topics if t.lesson_path)} lessons, "
              f"{sum(len(t.mcqs) for t in lang.topics)} MCQs, {len(lang.problems)} problems")
        for e in lang.errors:
            print(f"  [content] {e}")
            failures += 1
        ids = set()
        for t in lang.topics:
            if t.id in ids:
                print(f"  [curriculum] duplicate topic id {t.id}")
                failures += 1
            ids.add(t.id)
            for q in t.mcqs:
                problems = []
                if len(q["options"]) < 2:
                    problems.append("fewer than 2 options")
                if not q["answer"]:
                    problems.append("no valid answer letter")
                if any(a >= len(q["options"]) for a in q["answer"]):
                    problems.append("answer letter out of range")
                if not q["explanation"]:
                    problems.append("no explanation")
                if problems:
                    failures += 1
                    print(f"  [mcq {q['id']}] {', '.join(problems)}")
        seen = set()
        for t in lang.topics:
            for q in t.mcqs:
                if q["id"] in seen:
                    failures += 1
                    print(f"  [mcq] duplicate id {q['id']}")
                seen.add(q["id"])
        probs = [p for p in lang.problems.values() if not only_prob or p.id == only_prob]
        with ThreadPoolExecutor(max_workers=6) as ex:
            for p, errs in zip(probs, ex.map(lambda p: check_problem(lang, p), probs)):
                if errs:
                    failures += 1
                    print(f"  [problem {p.id}] ({p.path.relative_to(p.path.parents[2])})")
                    for e in errs:
                        print(f"      - {e}")
    print("OK" if not failures else f"{failures} issue(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
