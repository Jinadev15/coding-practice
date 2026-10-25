---
id: py-fleet-sql-repository
title: A SQL Repository for Fleet Missions
difficulty: Hard
order: 1
tags: sqlite3, SQL, constraints, JOIN, GROUP BY, window functions, transactions, injection
time_limit: 15
---
## Statement
Write the persistence layer for mission logs with **sqlite3** and real SQL. Every function takes an open `sqlite3.Connection`. The judge compares exact results, loads 60,000 missions, and attacks your queries with injection strings.

| Function | Contract |
|---|---|
| `init_schema(con)` | Enable foreign keys. Create `robots(id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL, model TEXT NOT NULL)` and `missions(id INTEGER PRIMARY KEY, robot_id INTEGER NOT NULL REFERENCES robots(id), started TEXT NOT NULL, distance REAL NOT NULL CHECK (distance >= 0), ok INTEGER NOT NULL CHECK (ok IN (0, 1)))`, plus an index on `missions(robot_id, started)`. |
| `add_robot(con, name, model) -> int` | The new id. A duplicate name raises `ValueError("duplicate robot")`. |
| `record_mission(con, robot_name, started, distance, ok) -> int` | The mission id. An unknown robot raises `ValueError("unknown robot")`. A constraint violation (such as a negative distance) raises `ValueError("invalid mission")`. `ok` is a bool. |
| `fleet_report(con) -> list[tuple]` | `(name, missions, total_distance, success_rate)` for **every** robot. `total_distance` is rounded to 2 places (0.0 if none). `success_rate` is the fraction of ok missions rounded to 3 places, or `None` with no missions. Sort by total distance descending, then name. |
| `longest_missions(con) -> list[tuple]` | Per robot with missions: `(name, started, distance)` of its longest mission. On ties, the earliest `started` wins. Sorted by name. Use a **window function**. |
| `best_streak(con, robot_name) -> int` | The longest run of consecutive `ok` missions in `started` order (0 for none or an unknown robot). |
| `transfer_missions(con, from_name, to_name) -> int` | Moves **all** missions to the other robot **atomically**, returning the count. If either robot is unknown, raise `ValueError("unknown robot")` and change nothing. |
| `search_robots(con, text) -> list[str]` | Names **containing** `text` literally (case-sensitive), sorted. `%` and `_` in `text` are literal characters, not wildcards. |

Every query must be **parameterised**.

## Starter
```python
import sqlite3


def init_schema(con):
    con.execute("CREATE TABLE robots(id INTEGER PRIMARY KEY, name TEXT, model TEXT)")
    con.execute("CREATE TABLE missions(id INTEGER PRIMARY KEY, robot_id INTEGER, started TEXT, distance REAL, ok INTEGER)")


def add_robot(con, name, model):
    return con.execute(f"INSERT INTO robots(name, model) VALUES ('{name}', '{model}')").lastrowid


def record_mission(con, robot_name, started, distance, ok):
    rid = con.execute(f"SELECT id FROM robots WHERE name = '{robot_name}'").fetchone()[0]
    return con.execute("INSERT INTO missions(robot_id, started, distance, ok) VALUES (?, ?, ?, ?)",
                       (rid, started, distance, int(ok))).lastrowid


def fleet_report(con):
    return con.execute("""SELECT r.name, COUNT(*), SUM(m.distance), AVG(m.ok)
                          FROM robots r JOIN missions m ON m.robot_id = r.id GROUP BY r.id""").fetchall()


def longest_missions(con):
    return []


def best_streak(con, robot_name):
    return 0


def transfer_missions(con, from_name, to_name):
    return 0


def search_robots(con, text):
    return [r[0] for r in con.execute(f"SELECT name FROM robots WHERE name LIKE '%{text}%'")]
```

## Driver
```python
import random
import sys

def attempt(label, fn):
    try:
        print(f"{label}: {fn()!r}")
    except ValueError as e:
        print(f"{label}: ValueError {e}")
    except sqlite3.Error as e:
        print(f"{label}: sqlite3 {type(e).__name__}")

def fresh():
    con = sqlite3.connect(":memory:")
    init_schema(con)
    return con

for cmd in sys.stdin.read().split():
    con = fresh()
    if cmd == "basic":
        for n, m in [("rover", "R2"), ("arm", "UR5"), ("drone", "Q4"), ("idle_bot", "R2")]:
            add_robot(con, n, m)
        attempt("dup", lambda: add_robot(con, "rover", "X"))
        data = [("rover", "2026-01-01T10:00", 120.5, True), ("rover", "2026-01-02T10:00", 80.25, False),
                ("rover", "2026-01-03T10:00", 120.5, True), ("arm", "2026-01-01T09:00", 0.5, True),
                ("drone", "2026-01-05T08:00", 300.0, True), ("drone", "2026-01-04T08:00", 300.0, False)]
        for d in data:
            record_mission(con, *d)
        attempt("unknown", lambda: record_mission(con, "ghost", "2026-01-01", 1.0, True))
        attempt("negative", lambda: record_mission(con, "arm", "2026-01-01", -1.0, True))
        attempt("report", lambda: fleet_report(con))
        attempt("longest", lambda: longest_missions(con))
        attempt("fk on", lambda: con.execute("PRAGMA foreign_keys").fetchone()[0])
        attempt("raw fk", lambda: con.execute("INSERT INTO missions(robot_id, started, distance, ok) VALUES (99, 'x', 1, 1)"))
        attempt("raw ok=2", lambda: con.execute("INSERT INTO missions(robot_id, started, distance, ok) VALUES (1, 'x', 1, 2)"))
        attempt("index", lambda: any("robot_id" in (r[4] or "") for r in con.execute("SELECT * FROM sqlite_master WHERE type='index'")))
    elif cmd == "streaks":
        add_robot(con, "r", "M"); add_robot(con, "empty", "M")
        pattern = [1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1]
        order = list(range(len(pattern))); random.Random(3).shuffle(order)
        for i in order:
            record_mission(con, "r", f"2026-02-{i + 1:02d}", 1.0, bool(pattern[i]))
        attempt("streak r", lambda: best_streak(con, "r"))
        attempt("streak empty", lambda: best_streak(con, "empty"))
        attempt("streak ghost", lambda: best_streak(con, "ghost"))
    elif cmd == "transfer":
        add_robot(con, "a", "M"); add_robot(con, "b", "M")
        for i in range(5):
            record_mission(con, "a", f"2026-03-0{i + 1}", i * 2.5, i % 2 == 0)
        attempt("to ghost", lambda: transfer_missions(con, "a", "ghost"))
        attempt("report", lambda: fleet_report(con))
        attempt("move", lambda: transfer_missions(con, "a", "b"))
        attempt("report", lambda: fleet_report(con))
        attempt("in tx?", lambda: con.in_transaction)
    elif cmd == "injection":
        for n in ["alpha", "beta_1", "beta21", "100%_sure", "o'brien", "x"]:
            add_robot(con, n, "M")
        attempt("quote name", lambda: record_mission(con, "o'brien", "2026", 1.0, True))
        attempt("search eta", lambda: search_robots(con, "eta"))
        attempt("search _", lambda: search_robots(con, "_"))
        attempt("search %", lambda: search_robots(con, "%"))
        attempt("search quote", lambda: search_robots(con, "'"))
        attempt("search inject", lambda: search_robots(con, "' OR '1'='1"))
        attempt("evil robot", lambda: add_robot(con, "z'); DROP TABLE robots; --", "M"))
        attempt("robots left", lambda: con.execute("SELECT COUNT(*) FROM robots").fetchone()[0])
        attempt("evil lookup", lambda: record_mission(con, "x' OR '1'='1", "2026", 1.0, True))
        attempt("ALPHA", lambda: search_robots(con, "ALPHA"))
    elif cmd == "load":
        rnd = random.Random(2026)
        names = [f"bot{i:03d}" for i in range(400)]
        for n in names:
            add_robot(con, n, rnd.choice(["R1", "R2", "Q4"]))
        for i in range(60000):
            record_mission(con, rnd.choice(names[:390]), f"2026-{rnd.randint(1, 12):02d}-{rnd.randint(1, 28):02d}T{rnd.randint(0, 23):02d}:{rnd.randint(0, 59):02d}:{i % 60:02d}",
                           round(rnd.uniform(0, 500), 2), rnd.random() < 0.8)
        rep = fleet_report(con)
        print(len(rep), rep[:3], rep[-3:])
        lm = longest_missions(con)
        print(len(lm), lm[:3])
        print([best_streak(con, n) for n in names[:12]])
```

## Tests
=== sample
basic
---
dup: ValueError duplicate robot
unknown: ValueError unknown robot
negative: ValueError invalid mission
report: [('drone', 2, 600.0, 0.5), ('rover', 3, 321.25, 0.667), ('arm', 1, 0.5, 1.0), ('idle_bot', 0, 0.0, None)]
longest: [('arm', '2026-01-01T09:00', 0.5), ('drone', '2026-01-04T08:00', 300.0), ('rover', '2026-01-01T10:00', 120.5)]
fk on: 1
raw fk: sqlite3 IntegrityError
raw ok=2: sqlite3 IntegrityError
index: True
=== hidden
streaks
---
streak r: 4
streak empty: 0
streak ghost: 0
=== hidden
transfer
---
to ghost: ValueError unknown robot
report: [('a', 5, 25.0, 0.6), ('b', 0, 0.0, None)]
move: 5
report: [('b', 5, 25.0, 0.6), ('a', 0, 0.0, None)]
in tx?: False
=== hidden
injection
---
quote name: 1
search eta: ['beta21', 'beta_1']
search _: ['100%_sure', 'beta_1']
search %: ['100%_sure']
search quote: ["o'brien"]
search inject: []
evil robot: 7
robots left: 7
evil lookup: ValueError unknown robot
ALPHA: []
=== hidden
load
---
400 [('bot278', 183, 47624.03, 0.781), ('bot015', 192, 47511.92, 0.786), ('bot246', 181, 47484.34, 0.851)] [('bot397', 0, 0.0, None), ('bot398', 0, 0.0, None), ('bot399', 0, 0.0, None)]
390 [('bot000', '2026-08-16T21:59:30', 496.04), ('bot001', '2026-02-14T21:31:19', 496.59), ('bot002', '2026-05-18T08:23:37', 499.36)]
[20, 24, 12, 11, 18, 20, 13, 15, 10, 27, 17, 17]

## Hints
- `PRAGMA foreign_keys = ON` is per connection. Run it inside `init_schema`.
- Translate `sqlite3.IntegrityError` into the required `ValueError`s. Do the existence checks for robots yourself, so the messages are exact.
- `fleet_report`: `LEFT JOIN`, then `COUNT(m.id)`, `COALESCE(ROUND(SUM(m.distance), 2), 0.0)`, and `ROUND(AVG(m.ok), 3)` (which is NULL when there are no missions).
- `longest_missions`: `ROW_NUMBER() OVER (PARTITION BY robot_id ORDER BY distance DESC, started ASC)`, keeping rank 1.
- `search_robots`: `LIKE ? ESCAPE '\'` with `%`, `\` and `_` escaped in the text. Or use `instr(name, ?) > 0`. Note that `LIKE` is case-insensitive for ASCII in SQLite.
- `with con:` makes `transfer_missions` atomic. Check both robots before updating.

## Solution
```python
import sqlite3


def init_schema(con):
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript("""
        CREATE TABLE IF NOT EXISTS robots (
            id    INTEGER PRIMARY KEY,
            name  TEXT UNIQUE NOT NULL,
            model TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS missions (
            id       INTEGER PRIMARY KEY,
            robot_id INTEGER NOT NULL REFERENCES robots(id),
            started  TEXT NOT NULL,
            distance REAL NOT NULL CHECK (distance >= 0),
            ok       INTEGER NOT NULL CHECK (ok IN (0, 1))
        );
        CREATE INDEX IF NOT EXISTS idx_missions_robot_started ON missions(robot_id, started);
    """)


def _robot_id(con, name):
    row = con.execute("SELECT id FROM robots WHERE name = ?", (name,)).fetchone()
    return None if row is None else row[0]


def add_robot(con, name, model):
    try:
        with con:
            return con.execute("INSERT INTO robots(name, model) VALUES (?, ?)", (name, model)).lastrowid
    except sqlite3.IntegrityError:
        raise ValueError("duplicate robot") from None


def record_mission(con, robot_name, started, distance, ok):
    rid = _robot_id(con, robot_name)
    if rid is None:
        raise ValueError("unknown robot")
    try:
        with con:
            return con.execute("INSERT INTO missions(robot_id, started, distance, ok) VALUES (?, ?, ?, ?)",
                               (rid, started, distance, 1 if ok else 0)).lastrowid
    except sqlite3.IntegrityError:
        raise ValueError("invalid mission") from None


def fleet_report(con):
    return con.execute("""
        SELECT r.name,
               COUNT(m.id)                                AS missions,
               COALESCE(ROUND(SUM(m.distance), 2), 0.0)   AS total,
               ROUND(AVG(m.ok), 3)                        AS success_rate
        FROM robots r LEFT JOIN missions m ON m.robot_id = r.id
        GROUP BY r.id
        ORDER BY total DESC, r.name
    """).fetchall()


def longest_missions(con):
    return con.execute("""
        WITH ranked AS (
            SELECT robot_id, started, distance,
                   ROW_NUMBER() OVER (PARTITION BY robot_id ORDER BY distance DESC, started ASC) AS rk
            FROM missions
        )
        SELECT r.name, k.started, k.distance
        FROM ranked k JOIN robots r ON r.id = k.robot_id
        WHERE k.rk = 1
        ORDER BY r.name
    """).fetchall()


def best_streak(con, robot_name):
    best = run = 0
    rows = con.execute("""SELECT m.ok FROM missions m JOIN robots r ON r.id = m.robot_id
                          WHERE r.name = ? ORDER BY m.started, m.id""", (robot_name,))
    for (ok,) in rows:
        run = run + 1 if ok else 0
        best = max(best, run)
    return best


def transfer_missions(con, from_name, to_name):
    with con:                                            # one atomic transaction
        src, dst = _robot_id(con, from_name), _robot_id(con, to_name)
        if src is None or dst is None:
            raise ValueError("unknown robot")
        return con.execute("UPDATE missions SET robot_id = ? WHERE robot_id = ?", (dst, src)).rowcount


def search_robots(con, text):
    return [name for (name,) in con.execute(
        "SELECT name FROM robots WHERE instr(name, ?) > 0 ORDER BY name", (text,))]
```

- **Constraints in the schema** (`UNIQUE`, `CHECK`, foreign keys) make the database reject bad data even from code that bypasses these functions. The judge inserts raw rows to prove it.
- **`LEFT JOIN` with `COUNT(m.id)`** keeps robots with no missions. `COUNT(*)` would count the NULL row as 1, and `AVG` over no rows is NULL, which becomes `None`.
- **The window function** ranks missions per robot without collapsing rows. `ORDER BY distance DESC, started ASC` encodes the tie-break in SQL.
- **Atomic transfer**: the existence checks and the `UPDATE` share one transaction, so a failure leaves the database untouched.
- **No string-built SQL**: every value is a `?` parameter, so names like `o'brien` or `x' OR '1'='1` are just data. `instr` does a literal, case-sensitive substring match with no wildcard semantics. With `LIKE` you'd have to escape `%` and `_`, and also handle its ASCII case-insensitivity.
- The composite index `(robot_id, started)` serves the per-robot ordered scan in `best_streak` and the partitioned window.
