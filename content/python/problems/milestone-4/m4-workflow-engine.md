---
id: m4-workflow-engine
title: A Resumable Async Workflow Engine
difficulty: Expert
order: 3
tags: asyncio, DAG scheduling, retries, timeouts, semaphores, SQLite persistence, OOP design
time_limit: 15
---
## Statement
Capstone: a miniature Airflow or Prefect. Workflows are DAGs of **async tasks** with dependencies, retries and timeouts, run with bounded concurrency, and **persisted to SQLite**, so a crashed run resumes without redoing finished work.

**`Workflow`**
- `add(name, func, deps=(), retries=0, timeout=None)`. `func` is an `async def f(ctx) -> result`, where `ctx` is a dict `{dep_name: dep_result}` of its direct dependencies. Results must be JSON-serialisable. A duplicate name raises `ValueError`.
- `validate()` raises `ValueError("unknown dependency <d> of <task>")`, or `ValueError("cycle detected")`.

**`Engine(db_path, concurrency=2)`**
- **`await run(workflow, run_id) -> dict[str, str]`** returns each task's status: `"done"`, `"failed"` or `"skipped"`.
  - It validates first.
  - A task starts once **all** its dependencies are done, and at most `concurrency` tasks run at once.
  - A task **fails** if it raises an `Exception` or exceeds its `timeout` (`asyncio.wait_for`). It's retried immediately, up to `retries` extra attempts.
  - When a task finally fails, **every task depending on it, transitively, is skipped** and never runs. Independent branches keep going.
  - **Persistence**: after each task finishes (done or failed), record `(run_id, name, status, attempts, result_json)` in SQLite. Skipped tasks are recorded at the end of the run.
  - **Resume**: when `run` is called with a `run_id` that already has records, tasks recorded as `"done"` are **not executed again**. Their stored results feed their dependents. Failed and skipped tasks run again.
  - A `BaseException` that isn't an `Exception` (here, the judge's `Crash`) must propagate out of `run`, leaving the records written so far.
- `results(run_id) -> dict[name, result]` (done tasks only) and `attempts(run_id) -> dict[name, int]` (cumulative across resumed runs).

## Starter
```python
import asyncio


class Workflow:
    def __init__(self):
        self.tasks = {}

    def add(self, name, func, deps=(), retries=0, timeout=None):
        self.tasks[name] = (func, list(deps))


class Engine:
    def __init__(self, db_path, concurrency=2):
        self.results_ = {}

    async def run(self, workflow, run_id):
        status = {}
        for name, (func, deps) in workflow.tasks.items():          # declaration order, sequential, no persistence
            self.results_[name] = await func({d: self.results_.get(d) for d in deps})
            status[name] = "done"
        return status

    def results(self, run_id):
        return self.results_
```

## Driver
```python
import asyncio
import os
import sys
import tempfile

class Crash(BaseException):
    pass

calls = {}
active = {"now": 0, "max": 0}

def task(name, value=None, fail_times=0, sleep=0.01, crash=False):
    async def f(ctx):
        calls[name] = calls.get(name, 0) + 1
        active["now"] += 1; active["max"] = max(active["max"], active["now"])
        try:
            await asyncio.sleep(sleep)
            if crash and calls[name] == 1:
                raise Crash()
            if calls[name] <= fail_times:
                raise RuntimeError(f"{name} flaky")
            return value if value is not None else {"from": sorted(ctx), "sum": sum(v["sum"] if isinstance(v, dict) else v for v in ctx.values()) + 1}
        finally:
            active["now"] -= 1
    return f

def show(d):
    return " ".join(f"{k}={d[k]}" for k in sorted(d))

db = os.path.join(tempfile.mkdtemp(), "wf.sqlite")
for cmd in sys.stdin.read().split():
    calls.clear(); active.update(now=0, max=0)
    if cmd == "dag":
        wf = Workflow()
        wf.add("extract", task("extract", value=1))
        wf.add("clean", task("clean"), deps=["extract"])
        wf.add("features", task("features"), deps=["extract"])
        wf.add("train", task("train"), deps=["clean", "features"])
        wf.add("report", task("report"), deps=["train"])
        try:
            wf.add("clean", task("x"))
        except ValueError:
            print("duplicate rejected")
        eng = Engine(db, concurrency=2)
        st = asyncio.run(eng.run(wf, "run-1"))
        print(show(st))
        print("report result", eng.results("run-1")["report"], "max concurrency", active["max"], "calls", show(calls))
        bad = Workflow(); bad.add("a", task("a"), deps=["ghost"])
        try:
            asyncio.run(eng.run(bad, "bad"))
        except ValueError as e:
            print("error:", e)
        cyc = Workflow(); cyc.add("a", task("a"), deps=["c"]); cyc.add("b", task("b"), deps=["a"]); cyc.add("c", task("c"), deps=["b"])
        try:
            cyc.validate()
        except ValueError as e:
            print("error:", e)
    elif cmd == "failures":
        wf = Workflow()
        wf.add("fetch", task("fetch", value=5, fail_times=2), retries=2)
        wf.add("parse", task("parse"), deps=["fetch"])
        wf.add("upload", task("upload", fail_times=10), deps=["parse"], retries=1)
        wf.add("notify", task("notify"), deps=["upload"])
        wf.add("archive", task("archive"), deps=["notify"])
        wf.add("slow", task("slow", sleep=5.0), timeout=0.05, retries=1)
        wf.add("after_slow", task("after_slow"), deps=["slow"])
        wf.add("independent", task("independent", value=7))
        eng = Engine(db, concurrency=3)
        st = asyncio.run(eng.run(wf, "run-2"))
        print(show(st))
        print("attempts", show(eng.attempts("run-2")), "calls", show(calls))
    elif cmd == "resume":
        wf = Workflow()
        wf.add("a", task("a", value=10))
        wf.add("b", task("b"), deps=["a"])
        wf.add("c", task("c", crash=True), deps=["a"])
        wf.add("d", task("d"), deps=["b", "c"])
        eng = Engine(db, concurrency=1)
        try:
            asyncio.run(eng.run(wf, "run-3"))
        except Crash:
            saved = Engine(db).results("run-3")
            print("crashed; a saved:", "a" in saved, "c saved:", "c" in saved, "d saved:", "d" in saved)
        eng2 = Engine(db, concurrency=1)
        st = asyncio.run(eng2.run(wf, "run-3"))
        print(show(st), "| calls", show(calls))
        print("results", show(eng2.results("run-3")))
        st = asyncio.run(Engine(db).run(wf, "run-3"))
        print("third run calls unchanged:", show(calls), show(st))
    elif cmd == "wide":
        wf = Workflow()
        for i in range(40):
            wf.add(f"leaf{i:02d}", task(f"leaf{i:02d}", value=i))
        wf.add("join", task("join"), deps=[f"leaf{i:02d}" for i in range(40)])
        eng = Engine(db, concurrency=4)
        st = asyncio.run(eng.run(wf, "run-4"))
        print("done", sum(v == "done" for v in st.values()), "max concurrency", active["max"], "join", eng.results("run-4")["join"]["sum"])
```

## Tests
=== sample
dag
---
duplicate rejected
clean=done extract=done features=done report=done train=done
report result {'from': ['train'], 'sum': 6} max concurrency 2 calls clean=1 extract=1 features=1 report=1 train=1
error: unknown dependency ghost of a
error: cycle detected
=== hidden
failures
---
after_slow=skipped archive=skipped fetch=done independent=done notify=skipped parse=done slow=failed upload=failed
attempts after_slow=0 archive=0 fetch=3 independent=1 notify=0 parse=1 slow=2 upload=2 calls fetch=3 independent=1 parse=1 slow=2 upload=2
=== hidden
resume
---
crashed; a saved: True c saved: False d saved: False
a=done b=done c=done d=done | calls a=1 b=1 c=2 d=1
results a=10 b={'from': ['a'], 'sum': 11} c={'from': ['a'], 'sum': 11} d={'from': ['b', 'c'], 'sum': 23}
third run calls unchanged: a=1 b=1 c=2 d=1 a=done b=done c=done d=done
=== hidden
wide
---
done 41 max concurrency 4 join 781

## Hints
- Persist with the standard-library `sqlite3`: `CREATE TABLE IF NOT EXISTS tasks(run_id TEXT, name TEXT, status TEXT, attempts INTEGER, result TEXT, PRIMARY KEY(run_id, name))`, plus `INSERT ... ON CONFLICT DO UPDATE`. Commit after every write, so a crash keeps them.
- Scheduling loop: keep `pending`, `running` (a dict of name → `asyncio.Task`) and `status`. Start every pending task whose deps are all done (within the semaphore limit), then `await asyncio.wait(running.values(), return_when=FIRST_COMPLETED)`. Re-raise a `BaseException` from a finished task.
- When a task fails, mark its transitive dependents as skipped. A reverse adjacency map plus BFS does it.
- On resume, load the rows first: `"done"` tasks start out done, with their stored (JSON-decoded) results, and stored attempts accumulate.

## Solution
```python
import asyncio
import json
import sqlite3
from collections import deque


class Workflow:
    def __init__(self):
        self.tasks: dict[str, dict] = {}

    def add(self, name, func, deps=(), retries=0, timeout=None):
        if name in self.tasks:
            raise ValueError(f"duplicate task {name}")
        self.tasks[name] = {"func": func, "deps": list(deps), "retries": retries, "timeout": timeout}

    def validate(self):
        for name, t in self.tasks.items():
            for d in t["deps"]:
                if d not in self.tasks:
                    raise ValueError(f"unknown dependency {d} of {name}")
        indeg = {n: len(t["deps"]) for n, t in self.tasks.items()}       # Kahn's algorithm
        q = deque(n for n, k in indeg.items() if k == 0)
        seen = 0
        children = self.children()
        while q:
            n = q.popleft()
            seen += 1
            for c in children[n]:
                indeg[c] -= 1
                if indeg[c] == 0:
                    q.append(c)
        if seen != len(self.tasks):
            raise ValueError("cycle detected")

    def children(self):
        ch = {n: [] for n in self.tasks}
        for n, t in self.tasks.items():
            for d in t["deps"]:
                ch[d].append(n)
        return ch


class Engine:
    def __init__(self, db_path, concurrency=2):
        self.db = sqlite3.connect(db_path)
        self.db.execute("CREATE TABLE IF NOT EXISTS tasks(run_id TEXT, name TEXT, status TEXT, attempts INTEGER,"
                        " result TEXT, PRIMARY KEY(run_id, name))")
        self.db.commit()
        self.concurrency = concurrency

    def _save(self, run_id, name, status, attempts, result=None):
        self.db.execute("INSERT INTO tasks VALUES (?, ?, ?, ?, ?) ON CONFLICT(run_id, name) DO UPDATE SET "
                        "status=excluded.status, attempts=excluded.attempts, result=excluded.result",
                        (run_id, name, status, attempts, json.dumps(result)))
        self.db.commit()                                              # durable before moving on

    def _load(self, run_id):
        return {n: (s, a, json.loads(r)) for n, s, a, r in
                self.db.execute("SELECT name, status, attempts, result FROM tasks WHERE run_id = ?", (run_id,))}

    def results(self, run_id):
        return {n: r for n, (s, a, r) in self._load(run_id).items() if s == "done"}

    def attempts(self, run_id):
        return {n: a for n, (s, a, r) in self._load(run_id).items()}

    async def _attempt(self, spec, ctx):
        coro = spec["func"](ctx)
        return await (asyncio.wait_for(coro, spec["timeout"]) if spec["timeout"] else coro)

    async def _execute(self, name, spec, ctx, sem, prior_attempts):
        async with sem:
            attempts = prior_attempts
            for _ in range(spec["retries"] + 1):
                attempts += 1
                try:
                    return "done", attempts, await self._attempt(spec, ctx)
                except Exception:                                    # includes TimeoutError; BaseException escapes
                    continue
            return "failed", attempts, None

    async def run(self, workflow, run_id):
        workflow.validate()
        stored = self._load(run_id)
        tasks, children = workflow.tasks, workflow.children()
        status, results, attempts = {}, {}, {n: stored[n][1] if n in stored else 0 for n in tasks}
        for n in tasks:
            if n in stored and stored[n][0] == "done":               # resume: never redo finished work
                status[n], results[n] = "done", stored[n][2]
        sem = asyncio.Semaphore(self.concurrency)
        running: dict[str, asyncio.Task] = {}

        def skip_descendants(root):
            q = deque(children[root])
            while q:
                c = q.popleft()
                if c not in status:
                    status[c] = "skipped"
                    q.extend(children[c])

        try:
            while True:
                for n in tasks:
                    if n not in status and n not in running and all(status.get(d) == "done" for d in tasks[n]["deps"]):
                        ctx = {d: results[d] for d in tasks[n]["deps"]}
                        running[n] = asyncio.ensure_future(self._execute(n, tasks[n], ctx, sem, attempts[n]))
                if not running:
                    break
                done, _ = await asyncio.wait(running.values(), return_when=asyncio.FIRST_COMPLETED)
                for n in [n for n, t in running.items() if t in done]:
                    st, att, res = running.pop(n).result()           # re-raises BaseException (crash)
                    status[n], attempts[n] = st, att
                    self._save(run_id, n, st, att, res)
                    if st == "done":
                        results[n] = res
                    else:
                        skip_descendants(n)
        finally:
            for t in running.values():
                t.cancel()
        for n in tasks:
            if status.get(n) == "skipped":
                self._save(run_id, n, "skipped", attempts[n])
        return status
```

- **A DAG scheduler on asyncio**: tasks start as soon as their dependencies finish, independent branches overlap, and a semaphore caps concurrency (the judge measures the peak). `asyncio.wait(FIRST_COMPLETED)` reacts to each completion immediately.
- **Failure semantics are explicit**: retries absorb transient errors (`fetch` succeeds on its third attempt), timeouts turn hangs into failures (`slow`), and a permanent failure skips exactly its downstream subgraph while unrelated work (`independent`) completes.
- **Durability**: every finished task is committed to SQLite before the scheduler continues. A crash mid-run (the judge raises a `BaseException` that bypasses ordinary error handling) loses no completed work.
- **Idempotent resume**: rerunning a `run_id` reuses the stored results of `"done"` tasks, so expensive steps (training, uploads) never run twice, and attempt counts accumulate across runs for auditing.
- **Separation of concerns**: the `Workflow` is a pure description (validated by Kahn's algorithm), and the `Engine` handles execution and persistence. A distributed executor could replace the engine without touching workflow definitions.
