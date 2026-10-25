#!/usr/bin/env python3
"""Assemble C++ problems from authoring specs and stress-test them.

    python3 tools/build_problem.py SPEC [SPEC...]       build + stress + write content/cpp/problems/<topic>/<id>.md

Spec format: sections introduced by '=== name' lines:
  meta (key: value lines incl. topic, id, title, difficulty, order, tags, time_limit, compare, libs)
  statement, starter, driver, solution, explanation, hints ('- ' bullets), brute (optional; same
  function names as the solution), samples, hidden (test inputs separated by lines of '---'),
  gen (optional Python 3 printing ONE random input; argv[1] is a seed, argv[2] is 'small' or 'big').
The reference must agree with the brute force on every stress input, run clean under ASan/UBSan,
and the starter must fail at least one test.
"""
from __future__ import annotations

import hashlib
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STRESS = 300          # small random inputs compared against the brute force
GEN_HIDDEN = 6        # random hidden tests embedded in the problem (3 small + 3 big)
CXX = ["g++", "-std=c++23", "-O2", "-pipe"]
SAN = ["g++", "-std=c++23", "-O1", "-g", "-fsanitize=address,undefined", "-fno-sanitize-recover=all", "-pipe"]


def parse(path: Path) -> dict[str, str]:
    secs, cur = {}, None
    for line in path.read_text().split("\n"):
        m = re.fullmatch(r"=== (\w+)\s*", line)
        if m:
            cur = m.group(1); secs[cur] = []
        elif cur:
            secs[cur].append(line)
    return {k: "\n".join(v).strip("\n") for k, v in secs.items()}


def tests(block: str) -> list[str]:
    return [t.strip("\n") + "\n" for t in re.split(r"(?m)^---\s*$", block) if t.strip()] if block else []


def compile_(src: str, out: Path, cmd: list[str], libs: list[str]) -> None:
    f = out.with_suffix(".cpp"); f.write_text(src)
    r = subprocess.run(cmd + [str(f), "-o", str(out)] + libs, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"compile failed for {out.name}:\n{r.stderr[:4000]}")


def _cap_memory():
    import resource
    resource.setrlimit(resource.RLIMIT_AS, (3 << 30, 3 << 30))


def run(exe: Path, inp: str, timeout=20) -> str:
    r = subprocess.run([str(exe)], input=inp, capture_output=True, text=True, timeout=timeout,
                       preexec_fn=None if exe.name == "san" else _cap_memory)
    if r.returncode:
        raise RuntimeError(f"{exe.name} exit {r.returncode}\nstdin:\n{inp[:500]}\nstderr:\n{r.stderr[:2000]}")
    return r.stdout


def gen(code: str, seed: int, size: str, d: Path) -> str:
    g = d / "gen.py"; g.write_text(code)
    return subprocess.run([sys.executable, str(g), str(seed), size], capture_output=True, text=True, check=True).stdout


def norm(s: str) -> list[str]:
    return [l.rstrip() for l in s.rstrip().splitlines()]


def build(spec: Path) -> None:
    s = parse(spec)
    meta = dict(l.split(":", 1) for l in s["meta"].splitlines() if ":" in l)
    meta = {k.strip(): v.strip() for k, v in meta.items()}
    pid, topic = meta["id"], meta["topic"]
    libs = []
    seed0 = int(hashlib.md5(pid.encode()).hexdigest()[:8], 16)
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        compile_(s["solution"] + "\n\n" + s["driver"] + "\n", d / "ref", CXX, libs)
        compile_(s["solution"] + "\n\n" + s["driver"] + "\n", d / "san", SAN, libs)
        compile_(s["starter"] + "\n\n" + s["driver"] + "\n", d / "starter", CXX, libs)
        brute = None
        if s.get("brute"):
            compile_(s["brute"] + "\n\n" + s["driver"] + "\n", d / "brute", CXX, libs); brute = d / "brute"
        samples, hidden = tests(s.get("samples", "")), tests(s.get("hidden", ""))
        # stress against brute force (and sanitizers) on small random inputs
        if s.get("gen"):
            for i in range(STRESS if brute else 60):
                inp = gen(s["gen"], seed0 + i, "small", d)
                got = run(d / "san", inp) if i % 10 == 0 else run(d / "ref", inp)
                if brute and norm(got) != norm(run(brute, inp)):
                    sys.exit(f"[{pid}] MISMATCH vs brute on stress input {i}:\n{inp}\nref:\n{got}\nbrute:\n{run(brute, inp)}")
            for i in range(GEN_HIDDEN):
                hidden.append(gen(s["gen"], seed0 + 10_000 + i, "small" if i < GEN_HIDDEN // 2 else "big", d))
        allt = samples + hidden
        outs = []
        tl = float(meta.get("time_limit", 1))
        for t in allt:
            t0 = time.perf_counter()
            outs.append(run(d / "ref", t))
            el = time.perf_counter() - t0
            if el > tl * 0.5:
                sys.exit(f"[{pid}] reference takes {el:.2f}s on a test (limit {tl}s): too close to the limit\n{t[:200]}")
            if len(t) < 20_000:
                run(d / "san", t)
            if brute and len(t) < 5_000 and "gen" not in t:
                try:
                    b = run(brute, t, timeout=5)
                except (subprocess.TimeoutExpired, RuntimeError):
                    b = None          # too big for the brute force: covered by the stress inputs
                if b is not None and norm(b) != norm(outs[-1]):
                    sys.exit(f"[{pid}] MISMATCH vs brute on listed test:\n{t}\nref:\n{outs[-1]}\nbrute:\n{b}")
        starter_fails = False
        for t, o in zip(allt, outs):
            try:
                t0 = time.perf_counter()
                got = run(d / "starter", t, timeout=max(5, 3 * tl))
                if norm(got) != norm(o) or time.perf_counter() - t0 > tl:
                    starter_fails = True; break
            except Exception:
                starter_fails = True; break
        if not starter_fails:
            sys.exit(f"[{pid}] the starter passes every test; make the tests stronger")
    for o in outs:
        if any(l.startswith("## ") for l in o.splitlines()) or "\n---\n" in "\n" + o:
            sys.exit(f"[{pid}] an output line conflicts with the problem file format")
    # assemble
    fm = ["---"] + [f"{k}: {meta[k]}" for k in ("id", "title", "difficulty", "order", "tags", "time_limit", "compare", "libs") if meta.get(k)] + ["---"]
    md = "\n".join(fm) + "\n## Statement\n" + s["statement"].strip() + "\n\n## Starter\n```cpp\n" + s["starter"].strip() + \
        "\n```\n\n## Driver\n```cpp\n" + s["driver"].strip() + "\n```\n\n## Tests\n"
    for i, (t, o) in enumerate(zip(allt, outs)):
        md += ("=== sample\n" if i < len(samples) else "=== hidden\n") + t
        if len(o) < 3000:
            md += "---\n" + o.rstrip("\n") + "\n"
    md += "\n## Hints\n" + s["hints"].strip() + "\n\n## Solution\n" + s["explanation"].strip() + "\n\n```cpp\n" + s["solution"].strip() + "\n```\n"
    dest = ROOT / "content" / "cpp" / "problems" / topic / f"{pid}.md"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(md)
    print(f"[{pid}] ok: {len(samples)} samples, {len(hidden)} hidden, stress {'vs brute' if brute else 'sanitizers only'} -> {dest.relative_to(ROOT)}")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        build(Path(p))
