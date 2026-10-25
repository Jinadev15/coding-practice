---
id: py-report-service
title: A SOLID Report Service
difficulty: Medium
order: 1
tags: SOLID, open/closed, dependency inversion, Protocol, registry, csv, json
time_limit: 5
---
## Statement
Refactor-proof reporting: a `ReportService` that depends only on **abstractions** (a data source and a clock), with output formats that plug in through a **registry** (open/closed). The judge registers a brand-new HTML formatter and injects a fake data source and a frozen clock.

**Registry**
- `@register_formatter` registers a formatter **class** under its class attribute `name`, and returns the class. A duplicate name raises `ValueError`.
- `get_formatter(name)` returns a **new instance**, or raises `ValueError("unknown format <name>")`.

A formatter implements `format(title: str, columns: list[str], rows: list[dict]) -> str`, where a missing key renders as an empty value.

| `name` | Output |
|---|---|
| `"csv"` | A first line `# <title>`, then a header and rows written with `csv.writer` (`lineterminator="\n"`, minimal quoting). |
| `"json"` | `json.dumps({"title": title, "rows": [{col: row.get(col) for col in columns} ...]})` |
| `"markdown"` | `### <title>`, a blank line, `\| a \| b \|`, `\|---\|---\|`, then one row per line `\| v1 \| v2 \|`, with `\|` inside values escaped as `\\\|`. |

**`ReportService(source, clock)`**
- `source.rows(query)` returns a list of dicts. `clock()` returns a `datetime`.
- `generate(query, fmt, columns=None, title=None) -> str` looks up the formatter **before** querying (so a bad format never hits the data source).
  - `columns` defaults to the union of the row keys in first-seen order, and `title` defaults to `Report: <query>`.
  - It returns the formatted text plus a final line `-- generated <clock().isoformat()> (<n> rows)`.

## Starter
```python
import json
from datetime import datetime


class ReportService:                     # hard-wired: a database, the wall clock and if/elif formats
    def __init__(self, source=None, clock=None):
        self.source = source

    def generate(self, query, fmt, columns=None, title=None):
        rows = self.source.rows(query)
        if fmt == "json":
            out = json.dumps(rows)
        elif fmt == "csv":
            out = "\n".join(",".join(str(v) for v in r.values()) for r in rows)
        else:
            out = str(rows)
        return out + f"\n-- generated {datetime.now().isoformat()}"
```

## Driver
```python
import sys
from datetime import datetime

class FakeSource:
    def __init__(self): self.queries = []
    def rows(self, query):
        self.queries.append(query)
        if query == "robots":
            return [{"id": "r1", "battery": 0.82, "status": "idle"},
                    {"id": "r2", "battery": 0.15, "status": "charging", "note": "dock, bay 3"},
                    {"id": "r|3", "battery": 0.5}]
        if query == "empty":
            return []
        return [{"n": i, "sq": i * i} for i in range(int(query))]

clock = lambda: datetime(2026, 10, 25, 9, 30, 0)

for cmd in sys.stdin.read().split():
    if cmd == "formats":
        src = FakeSource()
        svc = ReportService(src, clock)
        for fmt in ["csv", "json", "markdown"]:
            print(svc.generate("robots", fmt))
            print("====")
        print(svc.generate("robots", "csv", columns=["status", "id"], title="Fleet"))
        try:
            svc.generate("robots", "pdf")
        except ValueError as e:
            print("error:", e, "| queries so far:", len(src.queries))
        print(svc.generate("empty", "markdown"))
    elif cmd == "extend":
        @register_formatter
        class HtmlFormatter:
            name = "html"
            def format(self, title, columns, rows):
                head = "".join(f"<th>{c}</th>" for c in columns)
                body = "".join("<tr>" + "".join(f"<td>{r.get(c, '')}</td>" for c in columns) + "</tr>" for r in rows)
                return f"<h1>{title}</h1><table><tr>{head}</tr>{body}</table>"
        svc = ReportService(FakeSource(), clock)
        print(svc.generate("3", "html"))
        print(type(get_formatter("html")).__name__, get_formatter("csv") is not get_formatter("csv"))
        try:
            register_formatter(HtmlFormatter)
        except ValueError:
            print("duplicate format rejected")
    elif cmd == "big":
        svc = ReportService(FakeSource(), clock)
        out = svc.generate("20000", "csv")
        lines = out.splitlines()
        print(len(lines), lines[0], lines[1], lines[-2], lines[-1])
        md = svc.generate("500", "markdown")
        print(len(md.splitlines()), md.splitlines()[3])
```

## Tests
=== sample
formats
---
# Report: robots
id,battery,status,note
r1,0.82,idle,
r2,0.15,charging,"dock, bay 3"
r|3,0.5,,
-- generated 2026-10-25T09:30:00 (3 rows)
====
{"title": "Report: robots", "rows": [{"id": "r1", "battery": 0.82, "status": "idle", "note": null}, {"id": "r2", "battery": 0.15, "status": "charging", "note": "dock, bay 3"}, {"id": "r|3", "battery": 0.5, "status": null, "note": null}]}
-- generated 2026-10-25T09:30:00 (3 rows)
====
### Report: robots

| id | battery | status | note |
|---|---|---|---|
| r1 | 0.82 | idle |  |
| r2 | 0.15 | charging | dock, bay 3 |
| r\|3 | 0.5 |  |  |
-- generated 2026-10-25T09:30:00 (3 rows)
====
# Fleet
status,id
idle,r1
charging,r2
,r|3
-- generated 2026-10-25T09:30:00 (3 rows)
error: unknown format pdf | queries so far: 4
### Report: empty

|  |
|
-- generated 2026-10-25T09:30:00 (0 rows)
=== hidden
extend
---
<h1>Report: 3</h1><table><tr><th>n</th><th>sq</th></tr><tr><td>0</td><td>0</td></tr><tr><td>1</td><td>1</td></tr><tr><td>2</td><td>4</td></tr></table>
-- generated 2026-10-25T09:30:00 (3 rows)
HtmlFormatter True
duplicate format rejected
=== hidden
big
---
20003 # Report: 20000 n,sq 19999,399960001 -- generated 2026-10-25T09:30:00 (20000 rows)
505 |---|---|

## Hints
- `_REGISTRY: dict[str, type] = {}`. The decorator checks `cls.name not in _REGISTRY`, stores the class and returns it, so it works as `@register_formatter`.
- The service stores `self._source` and `self._clock` and never imports a database or calls `datetime.now()`. That's what makes it testable.
- Default columns: `list(dict.fromkeys(k for r in rows for k in r))` keeps the first-seen order.
- CSV: write into an `io.StringIO`. `csv.writer(buf, lineterminator="\n")` quotes values containing commas automatically.

## Solution
```python
import csv
import io
import json
from typing import Callable, Protocol
from datetime import datetime

_REGISTRY: dict[str, type] = {}


def register_formatter(cls):
    if cls.name in _REGISTRY:
        raise ValueError(f"duplicate format {cls.name}")
    _REGISTRY[cls.name] = cls
    return cls


def get_formatter(name: str):
    try:
        return _REGISTRY[name]()
    except KeyError:
        raise ValueError(f"unknown format {name}") from None


class DataSource(Protocol):
    def rows(self, query: str) -> list[dict]: ...


class Formatter(Protocol):
    name: str
    def format(self, title: str, columns: list[str], rows: list[dict]) -> str: ...


@register_formatter
class CsvFormatter:
    name = "csv"

    def format(self, title, columns, rows):
        buf = io.StringIO()
        buf.write(f"# {title}\n")
        w = csv.writer(buf, lineterminator="\n")
        w.writerow(columns)
        for r in rows:
            w.writerow(["" if r.get(c) is None else r.get(c) for c in columns])
        return buf.getvalue().rstrip("\n")


@register_formatter
class JsonFormatter:
    name = "json"

    def format(self, title, columns, rows):
        return json.dumps({"title": title, "rows": [{c: r.get(c) for c in columns} for r in rows]})


@register_formatter
class MarkdownFormatter:
    name = "markdown"

    @staticmethod
    def _cell(v) -> str:
        return "" if v is None else str(v).replace("|", "\\|")

    def format(self, title, columns, rows):
        lines = [f"### {title}", "", "| " + " | ".join(columns) + " |", "|" + "---|" * len(columns)]
        lines += ["| " + " | ".join(self._cell(r.get(c)) for c in columns) + " |" for r in rows]
        return "\n".join(lines)


class ReportService:
    def __init__(self, source: DataSource, clock: Callable[[], datetime]):
        self._source = source                         # injected abstractions (DIP)
        self._clock = clock

    def generate(self, query: str, fmt: str, columns: list[str] | None = None, title: str | None = None) -> str:
        formatter = get_formatter(fmt)                # fail fast before touching the data source
        rows = self._source.rows(query)
        cols = columns if columns is not None else list(dict.fromkeys(k for r in rows for k in r))
        body = formatter.format(title or f"Report: {query}", cols, rows)
        return f"{body}\n-- generated {self._clock().isoformat()} ({len(rows)} rows)"
```

- **Open/closed**: formats live in a registry. The judge's `HtmlFormatter` is added with one decorator, and `ReportService` never changes. The starter's `if/elif` chain needs editing (and re-testing) for every format.
- **Dependency inversion**: the service depends on a `DataSource` protocol and a clock callable, so tests inject a fake source and a frozen clock. Production would inject an SQL repository and `datetime.now`.
- **Single responsibility**: fetching, formatting and stamping live in separate collaborators, each testable alone. Each formatter knows only its own syntax, such as CSV quoting (`"dock, bay 3"`) and Markdown pipe escaping.
- **Fail fast**: resolving the formatter first means an invalid request never costs a database query (the query log proves it).
