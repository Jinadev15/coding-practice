# Databases: sqlite3, SQL and SQLAlchemy

Robots log missions, fleets track maintenance, ML pipelines store experiment results. All of that is structured data that must be **queried, updated concurrently and kept consistent**. Relational databases and SQL remain the backbone. Python ships `sqlite3` in the standard library (SQLite is the most deployed database in the world, running in every phone, browser and many robots), and SQLAlchemy is the standard toolkit for PostgreSQL and MySQL. This lesson covers the relational model, SQL from basics to window functions, safe parameterised queries, transactions, indexes and query plans, and SQLAlchemy Core and ORM.

## 1. The relational model

Data lives in **tables** (relations) of rows with typed columns. Each table has a **primary key**, and relationships are expressed with **foreign keys**. Normalisation removes duplication: a robot's name is stored once in `robots`, and missions refer to it by `robot_id`.

```sql
CREATE TABLE robots (
    id      INTEGER PRIMARY KEY,               -- SQLite: alias of the rowid, auto-assigned
    name    TEXT NOT NULL UNIQUE,
    model   TEXT NOT NULL,
    battery REAL NOT NULL DEFAULT 1.0 CHECK (battery BETWEEN 0 AND 1)
);
CREATE TABLE missions (
    id        INTEGER PRIMARY KEY,
    robot_id  INTEGER NOT NULL REFERENCES robots(id) ON DELETE CASCADE,
    started   TEXT NOT NULL,                   -- ISO-8601 timestamps sort correctly as text
    distance  REAL NOT NULL,
    ok        INTEGER NOT NULL                 -- 0/1 boolean
);
CREATE INDEX idx_missions_robot ON missions(robot_id, started);
```

Constraints (`NOT NULL`, `UNIQUE`, `CHECK`, `REFERENCES`) make the **database** enforce invariants, so even buggy code can't insert a battery level of 1.7.

## 2. sqlite3 in Python

```python
import sqlite3

con = sqlite3.connect("fleet.db")              # ":memory:" for an in-memory database
con.execute("PRAGMA foreign_keys = ON")        # SQLite enforces FKs only when enabled, per connection
con.row_factory = sqlite3.Row                  # rows accessible by column name

with con:                                      # a transaction: COMMIT on success, ROLLBACK on exception
    cur = con.execute("INSERT INTO robots(name, model) VALUES (?, ?)", ("rover-1", "R2"))
    rid = cur.lastrowid
    con.executemany("INSERT INTO missions(robot_id, started, distance, ok) VALUES (?, ?, ?, ?)",
                    [(rid, "2026-01-05T10:00", 120.5, 1), (rid, "2026-01-06T09:30", 80.0, 0)])

for row in con.execute("SELECT name, battery FROM robots WHERE battery < ?", (0.5,)):
    print(row["name"], row["battery"])
```

> [!DANGER]
> **Never build SQL with string formatting**, as in `f"... WHERE name = '{name}'"`. A name like `x' OR '1'='1` changes the query: that's **SQL injection**, one of the most exploited vulnerabilities. Always use placeholders (`?` or `:name`). The driver sends values separately from the SQL text. Identifiers (table and column names) can't be parameterised, so whitelist them.

## 3. Querying: from SELECT to window functions

```sql
-- filtering, sorting, limiting
SELECT name, battery FROM robots WHERE model = 'R2' AND battery < 0.3 ORDER BY battery LIMIT 5;

-- aggregation with GROUP BY / HAVING
SELECT robot_id, COUNT(*) AS n, ROUND(SUM(distance), 1) AS km, AVG(ok) AS success_rate
FROM missions GROUP BY robot_id HAVING COUNT(*) >= 2;

-- JOINs: INNER keeps matches only; LEFT keeps every robot, even with zero missions
SELECT r.name, COUNT(m.id) AS missions
FROM robots r LEFT JOIN missions m ON m.robot_id = r.id
GROUP BY r.id ORDER BY missions DESC, r.name;

-- subquery: robots that never failed
SELECT name FROM robots WHERE id NOT IN (SELECT robot_id FROM missions WHERE ok = 0);

-- CTE + window function: each robot's longest mission and running total
WITH ranked AS (
    SELECT robot_id, started, distance,
           ROW_NUMBER() OVER (PARTITION BY robot_id ORDER BY distance DESC) AS rk,
           SUM(distance) OVER (PARTITION BY robot_id ORDER BY started) AS running_km
    FROM missions
)
SELECT * FROM ranked WHERE rk = 1;
```

- `WHERE` filters rows **before** grouping, and `HAVING` filters groups **after** it.
- **Window functions** (`OVER (PARTITION BY … ORDER BY …)`) compute per-row values over related rows without collapsing them: rankings, running totals, moving averages, `LAG`/`LEAD` for deltas between consecutive readings.

> [!WARNING]
> `NULL` means "unknown". `NULL = NULL` is not true, so use `IS NULL`. `COUNT(col)` skips NULLs, while `COUNT(*)` doesn't. And `NOT IN (subquery)` returns nothing if the subquery contains a NULL. Prefer `NOT EXISTS`.

**Upsert:**

```sql
INSERT INTO robots(name, model, battery) VALUES (?, ?, ?)
ON CONFLICT(name) DO UPDATE SET battery = excluded.battery;
```

## 4. Transactions and ACID

| Property | Meaning |
|---|---|
| **Atomicity** | all statements of a transaction apply, or none do |
| **Consistency** | constraints hold before and after |
| **Isolation** | concurrent transactions don't see each other's partial work |
| **Durability** | committed data survives a crash or power loss |

```python
def transfer_mission(con, mission_id: int, new_robot: int) -> None:
    with con:                                           # one atomic unit
        if con.execute("SELECT 1 FROM robots WHERE id = ?", (new_robot,)).fetchone() is None:
            raise ValueError("no such robot")           # raises, so ROLLBACK
        con.execute("UPDATE missions SET robot_id = ? WHERE id = ?", (new_robot, mission_id))
```

SQLite allows many readers but **one writer at a time**. Enable `PRAGMA journal_mode=WAL` so readers don't block the writer, and set `timeout=` on connect. PostgreSQL provides fine-grained row locking and isolation levels (READ COMMITTED, REPEATABLE READ, SERIALIZABLE).

## 5. Indexes and query plans

Without an index, `WHERE robot_id = ?` scans every row: O(n). A **B-tree index** makes it O(log n), and a composite index `(robot_id, started)` also serves `ORDER BY started` within a robot.

```python
for row in con.execute("EXPLAIN QUERY PLAN SELECT * FROM missions WHERE robot_id = ? ORDER BY started", (1,)):
    print(row[-1])
```

```output
SEARCH missions USING INDEX idx_missions_robot (robot_id=?)
```

Indexes speed up reads but slow down writes and use space. Index the columns used in frequent `WHERE`, `JOIN` and `ORDER BY` clauses, and verify with `EXPLAIN`.

## 6. SQLAlchemy: Core and ORM

```python
from sqlalchemy import create_engine, ForeignKey, String, select, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session

class Base(DeclarativeBase): pass

class Robot(Base):
    __tablename__ = "robots"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    missions: Mapped[list["Mission"]] = relationship(back_populates="robot", cascade="all, delete-orphan")

class Mission(Base):
    __tablename__ = "missions"
    id: Mapped[int] = mapped_column(primary_key=True)
    robot_id: Mapped[int] = mapped_column(ForeignKey("robots.id"))
    distance: Mapped[float]
    robot: Mapped[Robot] = relationship(back_populates="missions")

engine = create_engine("sqlite:///:memory:")           # postgresql+psycopg://user@host/db in production
Base.metadata.create_all(engine)
with Session(engine) as s, s.begin():                   # unit of work, committed at the end of the block
    s.add(Robot(name="rover", missions=[Mission(distance=5.0), Mission(distance=7.5)]))
with Session(engine) as s:
    stmt = select(Robot.name, func.sum(Mission.distance)).join(Robot.missions).group_by(Robot.id)
    print(s.execute(stmt).all())                        # [('rover', 12.5)]
```

- **Core** is a Python expression language that compiles to SQL for any dialect. The **ORM** maps classes to tables with an identity map and a unit of work.
- Use **Alembic** for schema migrations.
- The ORM is productive, but know the SQL it emits (`echo=True`) to avoid N+1 queries.

## 7. Choosing storage

| Use | Choice |
|---|---|
| Embedded on the robot, single process, a config or log database | SQLite (WAL mode) |
| Multi-user services, concurrency, rich types | PostgreSQL (+ PostGIS for maps, TimescaleDB for telemetry) |
| Analytics over large files | DuckDB or Parquet with pandas/polars |
| Cache, queues, pub/sub | Redis |
| Raw high-rate sensor streams | rosbag2 (MCAP/SQLite) or time-series databases |

> [!EXAM]
> **What is SQL injection and how do parameterised queries prevent it?**
> SQL injection happens when untrusted input is concatenated into SQL text, so crafted input such as `' OR '1'='1` changes the structure of the query and can read, modify or delete arbitrary data. Parameterised queries send the SQL text with placeholders (`?`, `:name`) separately from the values. The database parses and plans the statement first, then binds the values purely as data, so they can never be interpreted as SQL. Identifiers can't be parameters and must be validated against a whitelist.
