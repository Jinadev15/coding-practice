---
id: py-fastapi-pagination-filtering
title: Pagination, Filtering and Sorting Done Right
difficulty: Medium
order: 4
tags: FastAPI, Query, Literal, list query params, class dependencies, generic response models, offset pagination, keyset pagination, Link header
time_limit: 10
---
## Statement
List endpoints are where APIs get slow and inconsistent. Build one that validates every query parameter, paginates two ways, and reports totals and next links.

```python
def create_app(robots: list[dict]) -> FastAPI: ...
# robot: {"id": int, "name": str, "status": "idle"|"busy"|"charging", "battery": float, "tags": [str]}
```

Responses use a **generic** model `Page[RobotOut]`, where `Page(BaseModel, Generic[T])` has `items: list[T]`, `total: int`, `limit: int`, `offset: int`, `next_offset: int | None`. `RobotOut` has all five robot fields.

**`GET /robots`**, with every parameter validated by FastAPI (invalid → 422):

| Param | Type / rule | Meaning |
|---|---|---|
| `status` | `idle`, `busy` or `charging` (use `Literal`) | exact match |
| `min_battery` | float in [0, 1], default 0 | `battery >= min_battery` |
| `q` | string of 2–20 chars | case-insensitive substring of `name` |
| `tag` | repeatable (`?tag=a&tag=b`) | the robot must have **all** given tags |
| `sort` | `id`, `-id`, `name`, `-name`, `battery`, `-battery`; default `id` | `-` means descending; ties always broken by `id` **ascending** |
| `limit` | int 1–50, default 10 | page size |
| `offset` | int ≥ 0, default 0 | items to skip |

Put `limit` and `offset` in a reusable **class dependency** `Pagination` (`Depends()`), not in the endpoint signature.

`total` counts all matches (before paging). `next_offset = offset + limit` if that's `< total`, else `null`. Also set the headers `X-Total-Count: <total>` and, when there is a next page, `Link: <URL>; rel="next"`, where URL is `str(request.url.include_query_params(offset=next_offset))`.

**`GET /robots/keyset?after=&limit=`** — keyset (cursor) pagination in id order: `after` (int ≥ 0, default 0) returns robots with `id > after`, at most `limit` (1–50, default 10). Response `{"items": [...], "next_after": <last id> or null}`. `next_after` is `null` when no robot has a bigger id than the last one returned.

## Starter
```python
from typing import Literal

from fastapi import FastAPI


def create_app(robots):
    app = FastAPI()

    @app.get("/robots")
    def list_robots(status: str | None = None, limit: int = 10, offset: int = 0):
        items = [r for r in robots if status is None or r["status"] == status]
        return {"items": items[offset:offset + limit], "total": len(items), "limit": limit,
                "offset": offset, "next_offset": None}

    return app
```

## Driver
```python
import random
import sys
import warnings
warnings.simplefilter("ignore")
from fastapi.testclient import TestClient

rng = random.Random(7)
NAMES = ["atlas", "bolt", "cog", "dash", "echo", "flux", "gear", "hex", "ion", "jolt", "kilo", "luma"]
ROBOTS = []
for i in range(1, 61):
    ROBOTS.append({"id": i, "name": f"{rng.choice(NAMES)}-{rng.randint(1, 9)}", "status": rng.choice(["idle", "busy", "charging"]),
                   "battery": round(rng.choice([0.1, 0.25, 0.5, 0.5, 0.75, 0.9, 1.0]), 2),
                   "tags": sorted(rng.sample(["arm", "lidar", "cam", "gps", "wheels"], rng.randint(0, 3)))})
rng.shuffle(ROBOTS)          # stored order is NOT id order

def show(c, path):
    r = c.get(path)
    if r.status_code != 200:
        print(f"{path} -> {r.status_code}")
        return
    j = r.json()
    if "next_after" in j:
        print(f"{path} -> ids={[x['id'] for x in j['items']]} next_after={j['next_after']}")
        return
    print(f"{path} -> ids={[x['id'] for x in j['items']]} total={j['total']} limit={j['limit']} offset={j['offset']} "
          f"next={j['next_offset']} X-Total-Count={r.headers.get('x-total-count')} Link={r.headers.get('link')}")

GROUPS = {
    "basic": ["/robots", "/robots?limit=5&offset=55", "/robots?limit=5&offset=60", "/robots?offset=100", "/robots?status=busy&limit=3"],
    "filters": ["/robots?min_battery=0.9&limit=50", "/robots?q=ECHO&limit=50", "/robots?tag=arm&tag=cam&limit=50",
                "/robots?tag=gps&status=idle&min_battery=0.5&limit=50", "/robots?q=zzz", "/robots?tag=arm&tag=arm&limit=3"],
    "sorting": ["/robots?sort=-id&limit=4", "/robots?sort=name&limit=6", "/robots?sort=-name&limit=6",
                "/robots?sort=battery&limit=6", "/robots?sort=-battery&limit=6&offset=3", "/robots?sort=-battery&status=charging&limit=50"],
    "invalid": ["/robots?status=sleeping", "/robots?min_battery=1.5", "/robots?min_battery=-0.1", "/robots?q=a",
                "/robots?q=" + "x" * 21, "/robots?sort=power", "/robots?limit=0", "/robots?limit=51", "/robots?offset=-1",
                "/robots?limit=abc", "/robots/keyset?after=-1", "/robots/keyset?limit=60"],
    "keyset": ["/robots/keyset?limit=7", "/robots/keyset?after=7&limit=7", "/robots/keyset?after=55&limit=10",
               "/robots/keyset?after=54&limit=6", "/robots/keyset?after=60", "/robots/keyset?after=1000"],
}
for g in sys.stdin.read().split():
    print("#", g)
    app = create_app(ROBOTS)
    c = TestClient(app)
    for p in GROUPS[g]:
        show(c, p)
    if g == "basic":
        spec = app.openapi()
        params = sorted(p["name"] for p in spec["paths"]["/robots"]["get"]["parameters"])
        print("params", params)
        print("schemas", sorted(k for k in spec["components"]["schemas"] if k.startswith("Page") or k == "RobotOut"))
```

## Tests
=== sample
basic
---
# basic
/robots -> ids=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10] total=60 limit=10 offset=0 next=10 X-Total-Count=60 Link=<http://testserver/robots?offset=10>; rel="next"
/robots?limit=5&offset=55 -> ids=[56, 57, 58, 59, 60] total=60 limit=5 offset=55 next=None X-Total-Count=60 Link=None
/robots?limit=5&offset=60 -> ids=[] total=60 limit=5 offset=60 next=None X-Total-Count=60 Link=None
/robots?offset=100 -> ids=[] total=60 limit=10 offset=100 next=None X-Total-Count=60 Link=None
/robots?status=busy&limit=3 -> ids=[1, 4, 6] total=21 limit=3 offset=0 next=3 X-Total-Count=21 Link=<http://testserver/robots?status=busy&limit=3&offset=3>; rel="next"
params ['limit', 'min_battery', 'offset', 'q', 'sort', 'status', 'tag']
schemas ['Page_RobotOut_', 'RobotOut']
=== hidden
filters
---
# filters
/robots?min_battery=0.9&limit=50 -> ids=[1, 7, 15, 16, 19, 30, 32, 36, 38, 39, 40, 44, 46, 50, 53, 56, 57, 60] total=18 limit=50 offset=0 next=None X-Total-Count=18 Link=None
/robots?q=ECHO&limit=50 -> ids=[17, 33] total=2 limit=50 offset=0 next=None X-Total-Count=2 Link=None
/robots?tag=arm&tag=cam&limit=50 -> ids=[45] total=1 limit=50 offset=0 next=None X-Total-Count=1 Link=None
/robots?tag=gps&status=idle&min_battery=0.5&limit=50 -> ids=[11, 16, 32] total=3 limit=50 offset=0 next=None X-Total-Count=3 Link=None
/robots?q=zzz -> ids=[] total=0 limit=10 offset=0 next=None X-Total-Count=0 Link=None
/robots?tag=arm&tag=arm&limit=3 -> ids=[3, 5, 7] total=14 limit=3 offset=0 next=3 X-Total-Count=14 Link=<http://testserver/robots?tag=arm&tag=arm&limit=3&offset=3>; rel="next"
=== hidden
sorting
---
# sorting
/robots?sort=-id&limit=4 -> ids=[60, 59, 58, 57] total=60 limit=4 offset=0 next=4 X-Total-Count=60 Link=<http://testserver/robots?sort=-id&limit=4&offset=4>; rel="next"
/robots?sort=name&limit=6 -> ids=[41, 51, 29, 23, 43, 7] total=60 limit=6 offset=0 next=6 X-Total-Count=60 Link=<http://testserver/robots?sort=name&limit=6&offset=6>; rel="next"
/robots?sort=-name&limit=6 -> ids=[53, 37, 11, 34, 47, 27] total=60 limit=6 offset=0 next=6 X-Total-Count=60 Link=<http://testserver/robots?sort=-name&limit=6&offset=6>; rel="next"
/robots?sort=battery&limit=6 -> ids=[3, 4, 8, 14, 20, 28] total=60 limit=6 offset=0 next=6 X-Total-Count=60 Link=<http://testserver/robots?sort=battery&limit=6&offset=6>; rel="next"
/robots?sort=-battery&limit=6&offset=3 -> ids=[30, 32, 36, 38, 39, 50] total=60 limit=6 offset=3 next=9 X-Total-Count=60 Link=<http://testserver/robots?sort=-battery&limit=6&offset=9>; rel="next"
/robots?sort=-battery&status=charging&limit=50 -> ids=[7, 15, 36, 38, 39, 60, 5, 35, 59, 17, 22, 25, 31, 37, 42, 52, 9, 29, 48, 14, 34, 54, 58] total=23 limit=50 offset=0 next=None X-Total-Count=23 Link=None
=== hidden
invalid
---
# invalid
/robots?status=sleeping -> 422
/robots?min_battery=1.5 -> 422
/robots?min_battery=-0.1 -> 422
/robots?q=a -> 422
/robots?q=xxxxxxxxxxxxxxxxxxxxx -> 422
/robots?sort=power -> 422
/robots?limit=0 -> 422
/robots?limit=51 -> 422
/robots?offset=-1 -> 422
/robots?limit=abc -> 422
/robots/keyset?after=-1 -> 422
/robots/keyset?limit=60 -> 422
=== hidden
keyset
---
# keyset
/robots/keyset?limit=7 -> ids=[1, 2, 3, 4, 5, 6, 7] next_after=7
/robots/keyset?after=7&limit=7 -> ids=[8, 9, 10, 11, 12, 13, 14] next_after=14
/robots/keyset?after=55&limit=10 -> ids=[56, 57, 58, 59, 60] next_after=None
/robots/keyset?after=54&limit=6 -> ids=[55, 56, 57, 58, 59, 60] next_after=None
/robots/keyset?after=60 -> ids=[] next_after=None
/robots/keyset?after=1000 -> ids=[] next_after=None

## Hints
- Declare `status: Literal["idle", "busy", "charging"] | None = None`, `tag: Annotated[list[str], Query()] = []`, and bounds with `Annotated[float, Query(ge=0, le=1)]`.
- `class Pagination: def __init__(self, limit: Annotated[int, Query(ge=1, le=50)] = 10, offset: ...)`, used as `page: Annotated[Pagination, Depends()]`.
- For the id tie-break, sort by id first, then do a stable sort by the requested field. Take `request: Request, response: Response` parameters to read the URL and set headers.

## Solution
**Let the framework validate.** `Literal[...]` restricts `status` and `sort` to known values, `Query(ge=, le=, min_length=)` bounds numbers and strings, and `list[str]` with `Query()` accepts repeated `?tag=` parameters. Every violation is a precise 422, and all of it appears in the OpenAPI docs.

**Class dependencies.** `Pagination` declares `limit`/`offset` once, and `Depends()` makes FastAPI build it from the query string. Every list endpoint can reuse it.

**Deterministic ordering.** Paging only works if the order is total. Sorting by `battery` alone leaves ties in arbitrary order, so the same robot could show up on two pages, or on none. Python's sort is **stable**: sort by id first, then by the requested key, and ties stay in id order (for descending too, because `reverse=True` keeps stability).

**Two pagination styles.**
- *Offset* is simple and supports "jump to page 7", but the database still walks past `offset` rows (O(offset)), and inserts shift items between pages.
- *Keyset* (`WHERE id > :after ORDER BY id LIMIT :n`) uses an index seek, costs the same on page 1 and page 1000, and doesn't skip or repeat items under inserts. It can't jump to arbitrary pages.

`total`, `X-Total-Count` and the `Link` header let clients build pagers without guessing.

Complexity here: O(n log n) per request (in-memory filtering and sorting). With a database: O(log n + page) for keyset, O(offset + page) for offset.

```python
from typing import Annotated, Generic, Literal, TypeVar

from fastapi import Depends, FastAPI, Query, Request, Response
from pydantic import BaseModel

T = TypeVar("T")


class RobotOut(BaseModel):
    id: int
    name: str
    status: str
    battery: float
    tags: list[str]


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    limit: int
    offset: int
    next_offset: int | None


class KeysetPage(BaseModel):
    items: list[RobotOut]
    next_after: int | None


class Pagination:
    def __init__(self, limit: Annotated[int, Query(ge=1, le=50)] = 10,
                 offset: Annotated[int, Query(ge=0)] = 0):
        self.limit, self.offset = limit, offset


SortKey = Literal["id", "-id", "name", "-name", "battery", "-battery"]


def create_app(robots):
    app = FastAPI()
    by_id = sorted(robots, key=lambda r: r["id"])

    @app.get("/robots", response_model=Page[RobotOut])
    def list_robots(
        request: Request,
        response: Response,
        page: Annotated[Pagination, Depends()],
        status: Literal["idle", "busy", "charging"] | None = None,
        min_battery: Annotated[float, Query(ge=0, le=1)] = 0,
        q: Annotated[str | None, Query(min_length=2, max_length=20)] = None,
        tag: Annotated[list[str], Query()] = [],
        sort: SortKey = "id",
    ):
        items = [r for r in by_id
                 if (status is None or r["status"] == status)
                 and r["battery"] >= min_battery
                 and (q is None or q.lower() in r["name"].lower())
                 and all(t in r["tags"] for t in tag)]
        field = sort.lstrip("-")
        if field != "id":
            items.sort(key=lambda r: r["id"])                               # tie-break: id ascending
            items.sort(key=lambda r: r[field], reverse=sort.startswith("-"))  # stable sort keeps it
        elif sort == "-id":
            items.reverse()
        total = len(items)
        nxt = page.offset + page.limit if page.offset + page.limit < total else None
        response.headers["X-Total-Count"] = str(total)
        if nxt is not None:
            response.headers["Link"] = f'<{request.url.include_query_params(offset=nxt)}>; rel="next"'
        return {"items": items[page.offset:page.offset + page.limit], "total": total,
                "limit": page.limit, "offset": page.offset, "next_offset": nxt}

    @app.get("/robots/keyset", response_model=KeysetPage)
    def keyset(after: Annotated[int, Query(ge=0)] = 0, limit: Annotated[int, Query(ge=1, le=50)] = 10):
        chunk = [r for r in by_id if r["id"] > after][:limit]
        more = bool(chunk) and any(r["id"] > chunk[-1]["id"] for r in by_id)
        return {"items": chunk, "next_after": chunk[-1]["id"] if more else None}

    return app
```
