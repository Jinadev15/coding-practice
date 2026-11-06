# FastAPI in Depth

FastAPI is the dominant modern Python framework for **JSON APIs**: ML model serving, mobile and SPA back ends, internal microservices, robot fleet managers. It builds on **Starlette** (an ASGI toolkit: routing, requests, middleware, WebSockets) and **Pydantic** (validation from type hints). An endpoint's signature is at once its parsing rules, its validation rules and its OpenAPI documentation. This lesson covers parameters and models, response models, status codes and error handling, dependency injection (including per-request database sessions), routers and app factories, pagination and filtering, async vs sync, and testing with `TestClient`.

## 1. Why FastAPI

- **Less code, fewer bugs.** You declare types once. Parsing, conversion, validation, error messages and docs all follow from them.
- **Correct by construction.** Invalid input never reaches your code: it gets a 422 with field-level details.
- **Docs for free.** `/docs` (Swagger UI) and `/openapi.json` are generated from the code, so client SDKs and contract tests can be generated too.
- **ASGI and async.** One process can serve thousands of slow I/O-bound connections. Plain `def` endpoints still work (they run in a thread pool).
- **Dependency injection** makes auth, database sessions and settings reusable and testable.

## 2. Where each parameter comes from

```python
from typing import Annotated, Literal

from fastapi import FastAPI, Header, Query
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

app = FastAPI(title="Fleet API", version="1.0")

class MissionIn(BaseModel):                       # a Pydantic model parameter = JSON body
    goal: tuple[float, float]
    priority: Literal["low", "normal", "high"] = "normal"
    speed: float = Field(default=0.5, gt=0, le=2.0)

@app.post("/robots/{robot_id}/missions")
def create_mission(
    robot_id: int,                                           # in the path template -> path param
    mission: MissionIn,                                      # model -> body
    dry_run: bool = False,                                   # simple type with default -> query
    tag: Annotated[list[str], Query()] = [],                 # repeated ?tag=a&tag=b
    x_request_id: Annotated[str | None, Header()] = None,    # header X-Request-Id
):
    return {"robot": robot_id, "goal": mission.goal, "dry_run": dry_run, "tags": tag, "rid": x_request_id}

c = TestClient(app)
r = c.post("/robots/7/missions?dry_run=true&tag=a&tag=b", json={"goal": [3, 4]}, headers={"X-Request-Id": "r1"})
print(r.json())
print(c.post("/robots/x/missions", json={"goal": [3, 4]}).status_code)     # 422: robot_id isn't an int
```

The rules: a name in the path template is a **path** parameter; a Pydantic model is the **body**; simple types are **query** parameters; `Header()`, `Cookie()`, `Form()`, `File()` are explicit. `Annotated[type, Query(ge=1, le=50)]` adds constraints. `bool` accepts `true/false/1/0/yes/no`.

### Dry run: how FastAPI handles one request

`POST /robots/7/missions?dry_run=true` with body `{"goal": [3, 4]}`:

| Step | What happens |
|---|---|
| 1 | Starlette routing matches the path template and method, extracting `robot_id="7"` |
| 2 | FastAPI resolves **dependencies** (sub-dependencies first; each one at most once per request) |
| 3 | it converts and validates path/query/header values: `robot_id → 7`, `dry_run → True` |
| 4 | it parses the JSON body and validates it as `MissionIn` (defaults fill `priority`, `speed`) |
| 5 | any failure in 2–4 → collected into one `RequestValidationError` → 422 with every error's `loc` |
| 6 | your function runs (in the event loop if `async def`, in a thread pool if `def`) |
| 7 | the return value is validated and **filtered** by `response_model`, then serialised to JSON |
| 8 | `yield`-dependency cleanup runs (commit/close); middleware sees the response |

## 3. Request and response models

```python
from fastapi import FastAPI, HTTPException, Response
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

class NoteIn(BaseModel):
    title: str = Field(min_length=1, max_length=80)
    body: str = ""

class NoteUpdate(BaseModel):                  # PATCH: everything optional
    title: str | None = Field(default=None, min_length=1, max_length=80)
    body: str | None = None

class NoteOut(BaseModel):
    id: int
    title: str
    body: str

app = FastAPI()
notes: dict[int, dict] = {}

@app.post("/notes", status_code=201, response_model=NoteOut)
def create(note: NoteIn):
    nid = len(notes) + 1
    notes[nid] = {"id": nid, **note.model_dump(), "owner_token": "secret"}   # internal field
    return notes[nid]                                                     # filtered by NoteOut

@app.patch("/notes/{nid}", response_model=NoteOut)
def patch(nid: int, changes: NoteUpdate):
    if nid not in notes:
        raise HTTPException(404, "note not found")
    notes[nid].update(changes.model_dump(exclude_unset=True))   # only the fields the client SENT
    return notes[nid]

@app.delete("/notes/{nid}", status_code=204)
def delete(nid: int):
    notes.pop(nid, None)
    return Response(status_code=204)                             # 204 must have no body

c = TestClient(app)
print(c.post("/notes", json={"title": "Plan", "body": "v1"}).json())   # no owner_token
print(c.patch("/notes/1", json={"body": "v2"}).json())                 # title kept
print(c.delete("/notes/1").status_code)
```

- **Separate input and output models.** Clients mustn't set server-owned fields (`id`, `version`), and responses must never include internal ones (password hashes, tokens). `response_model` is a security boundary: it drops undeclared fields even if you return the raw record.
- **`exclude_unset=True`** distinguishes "not sent" from "sent as null", which is the heart of PATCH.
- **Generic models** (`class Page(BaseModel, Generic[T])`) give typed envelopes such as `Page[RobotOut]`.

## 4. Status codes and errors

| Situation | Code | How |
|---|---|---|
| created | 201 | `@app.post(..., status_code=201)` (+ `Location` via a `Response` parameter) |
| deleted, nothing to return | 204 | `status_code=204`, return `Response(status_code=204)` |
| unknown resource | 404 | `raise HTTPException(404, "robot not found")` |
| state conflict (duplicate, busy) | 409 | `HTTPException(409, ...)` |
| malformed or invalid input | 422 | automatic `RequestValidationError` |
| not authenticated / not allowed | 401 / 403 | in a dependency |

`HTTPException` gives `{"detail": ...}`. For a consistent error model across a whole service, raise **domain exceptions** from the business layer and translate them in handlers:

```python
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

class DomainError(Exception):
    status, type_ = 400, "/errors/domain"
    def __init__(self, detail):
        super().__init__(detail)
        self.detail = detail

class NotFound(DomainError):
    status, type_ = 404, "/errors/not-found"

app = FastAPI()

@app.exception_handler(DomainError)                   # also catches every subclass
async def on_domain(request: Request, exc: DomainError):
    return JSONResponse({"type": exc.type_, "status": exc.status, "detail": exc.detail},
                        status_code=exc.status, media_type="application/problem+json")

@app.exception_handler(RequestValidationError)        # reshape FastAPI's own 422s
async def on_validation(request: Request, exc: RequestValidationError):
    fields = [".".join(map(str, e["loc"])) for e in exc.errors()]
    return JSONResponse({"type": "/errors/validation", "status": 422, "fields": fields}, status_code=422)

@app.get("/items/{sku}")
def item(sku: str):
    raise NotFound(f"item {sku} not found")             # the service layer knows nothing about HTTP

c = TestClient(app)
print(c.get("/items/X").status_code, c.get("/items/X").json())
```

The format above is **problem details** (RFC 9457). Also register handlers for Starlette's `HTTPException` (routing 404/405, keeping `exc.headers` such as `Allow`) and for `Exception` (500 with a generic message, and the traceback in the logs, never in the response).

## 5. Dependency injection

`Depends(f)` says "call `f` (resolving *its* parameters the same way) and give me the result":

```python
import sqlite3
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.testclient import TestClient

def get_db(request: Request):
    return request.app.state.db

def get_session(db=Depends(get_db)):
    conn = db                                  # in real code: a new session/connection per request
    try:
        yield conn                             # the endpoint runs here
        conn.commit()                          # success -> commit
    except BaseException:
        conn.rollback()                        # any error (incl. HTTPException) -> roll back
        raise
    finally:
        pass                                   # close the session here

def current_user(x_user: Annotated[str | None, Header()] = None, s=Depends(get_session)) -> str:
    if not x_user or s.execute("SELECT 1 FROM users WHERE name = ?", (x_user,)).fetchone() is None:
        raise HTTPException(401, "unknown user")
    return x_user

app = FastAPI()
app.state.db = sqlite3.connect(":memory:", check_same_thread=False)
app.state.db.executescript("CREATE TABLE users(name TEXT); INSERT INTO users VALUES ('ada');")

@app.get("/me")
def me(user: Annotated[str, Depends(current_user)], s=Depends(get_session)):   # same session as current_user
    return {"user": user}

c = TestClient(app)
print(c.get("/me", headers={"X-User": "ada"}).json(), c.get("/me").status_code)
```

- **`yield` dependencies** are per-request context managers: setup before `yield`, cleanup after. Exceptions from the endpoint are thrown into the generator at the `yield`, so you can roll back. Always re-raise.
- **Per-request cache**: `get_session` is used by `current_user` and by the endpoint, but runs **once**, so both share one transaction. `Depends(f, use_cache=False)` opts out.
- **Class dependencies**: `page: Annotated[Pagination, Depends()]` builds a `Pagination` from query parameters declared in its `__init__`. That's a reusable parameter group.
- **Overrides for tests**: `app.dependency_overrides[get_session] = fake_session` swaps the dependency for every dependent, with no monkey-patching.
- **Router- or app-level dependencies**: `APIRouter(dependencies=[Depends(require_api_key)])` protects every route in the router.

## 6. Routers and the application factory

```python
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient

robots = APIRouter(prefix="/robots", tags=["robots"])

@robots.get("")
def list_robots():
    return []

def create_app(settings=None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.ready = True              # startup: open pools, load ML models
        yield
        app.state.ready = False             # shutdown: close pools

    app = FastAPI(lifespan=lifespan)
    app.include_router(robots)
    app.include_router(robots, prefix="/v2")  # same router mounted again: /v2/robots
    return app

with TestClient(create_app()) as c:         # `with` runs the lifespan
    print(c.get("/robots").json(), c.get("/v2/robots").status_code)
```

Each `create_app()` returns an isolated app with its own state, which is what makes tests independent. Settings typically come from the environment with `pydantic-settings`.

## 7. Pagination, filtering and sorting

```python
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, Query, Request, Response
from fastapi.testclient import TestClient

class Pagination:
    def __init__(self, limit: Annotated[int, Query(ge=1, le=50)] = 10,
                 offset: Annotated[int, Query(ge=0)] = 0):
        self.limit, self.offset = limit, offset

ROWS = [{"id": i, "battery": (i * 37 % 10) / 10} for i in range(1, 31)]
app = FastAPI()

@app.get("/robots")
def robots(request: Request, response: Response, page: Annotated[Pagination, Depends()],
           sort: Literal["id", "-battery"] = "id"):
    items = sorted(ROWS, key=lambda r: r["id"])
    if sort == "-battery":
        items.sort(key=lambda r: r["battery"], reverse=True)    # stable: ties stay in id order
    total = len(items)
    nxt = page.offset + page.limit if page.offset + page.limit < total else None
    response.headers["X-Total-Count"] = str(total)
    if nxt is not None:
        response.headers["Link"] = f'<{request.url.include_query_params(offset=nxt)}>; rel="next"'
    return {"items": items[page.offset:page.offset + page.limit], "total": total, "next_offset": nxt}

r = TestClient(app).get("/robots?sort=-battery&limit=3")
print([x["id"] for x in r.json()["items"]], r.headers["link"])
```

- Validate every knob (`Literal` for sort keys and enums, bounds on `limit`), or one request with `limit=10_000_000` takes your service down.
- **Make the order total.** Sorting by a non-unique field without a tie-breaker lets items repeat or vanish between pages.
- **Offset** pagination is simple and allows jumping to page N, but costs O(offset) in the database and shifts under inserts. **Keyset** (`WHERE id > :after ORDER BY id LIMIT :n`) is an O(log n) index seek on every page and is stable, but can't jump.

## 8. async vs sync endpoints

| Endpoint | Runs on | Use for |
|---|---|---|
| `async def` | the event loop | non-blocking I/O with `await` (async DB drivers, `httpx.AsyncClient`) |
| `def` | a thread pool (default 40 threads) | blocking libraries (sqlite3, `requests`, most SDKs) |
| CPU-heavy work | a process pool or separate worker service | ML inference, image processing |

Calling blocking code (`time.sleep`, `requests.get`) inside `async def` **freezes every request** on that worker, because the event loop can't switch tasks while it waits.

## 9. Testing

`TestClient` (built on httpx) calls the ASGI app in-process: no server, no network, deterministic. `with TestClient(app) as c:` also runs the lifespan. Use `TestClient(app, raise_server_exceptions=False)` to see the 500 response instead of the raw exception. Combine it with `dependency_overrides` to swap databases and auth, and assert on status codes, bodies, headers and even `app.openapi()` (contract tests).

## Worked example: a complete mini API with a test

```python
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

app = FastAPI()
ROBOTS: dict[int, dict] = {}

class RobotIn(BaseModel):
    name: str = Field(min_length=1, max_length=32)
    battery: float = Field(ge=0, le=1)

class RobotOut(RobotIn):
    id: int

@app.post("/robots", response_model=RobotOut, status_code=201)
def create(robot: RobotIn):
    rid = len(ROBOTS) + 1
    ROBOTS[rid] = robot.model_dump()
    return {"id": rid, **ROBOTS[rid]}

@app.get("/robots/{rid}", response_model=RobotOut)
def read(rid: int):
    if rid not in ROBOTS:
        raise HTTPException(status_code=404, detail="robot not found")
    return {"id": rid, **ROBOTS[rid]}

client = TestClient(app)
print(client.post("/robots", json={"name": "r1", "battery": 0.9}).json())
print(client.post("/robots", json={"name": "", "battery": 2}).status_code)   # validation fails
print(client.get("/robots/99").status_code)
```

```output
{'name': 'r1', 'battery': 0.9, 'id': 1}
422
404
```

## 10. Complexity and performance

- Validation is O(size of the input). Pydantic v2's core is written in Rust, so it's fast, but deeply nested huge bodies still cost.
- Dependency resolution is O(number of dependencies) per request, and each is cached once per request.
- Throughput: an async endpoint waiting on I/O costs almost nothing while it waits, so concurrency is bounded by the event loop and the downstream systems. A sync endpoint holds one thread of the pool for its whole duration. Scale out with several uvicorn worker processes.

## 11. Pattern recognition

| Requirement | FastAPI tool |
|---|---|
| hide internal fields | `response_model` |
| partial updates | optional-field model + `model_dump(exclude_unset=True)` |
| one DB transaction per request | `yield` dependency with commit/rollback |
| shared auth for a group of routes | `APIRouter(dependencies=[...])` |
| reusable query parameter group | class dependency + `Depends()` |
| consistent error format | domain exceptions + `exception_handler`s |
| swap the DB in tests | `app.dependency_overrides` |
| open/close pools, load a model once | `lifespan` |

## 12. Common mistakes

- **Blocking calls in `async def`** endpoints.
- **No `response_model`**, so internal fields leak.
- **Swallowing exceptions in a `yield` dependency** (forgetting to re-raise): the client gets a wrong response, and the error disappears.
- **Global mutable state** instead of `app.state` and dependencies: tests interfere with each other.
- **`raise HTTPException` deep in the service layer**: your business logic now depends on the web framework.
- **Unbounded `limit`**, and sorting without a tie-breaker.
- **Echoing exception messages** in 500 responses.
- **Mutable default lists in models.** Pydantic copies defaults, so `tags: list[str] = []` is safe in a model, but use `Field(default_factory=list)` when in doubt.

## 13. Interview questions

> [!EXAM]
> **How does FastAPI use type hints, and why is dependency injection valuable?**
> Each endpoint parameter's annotation and default decide where it comes from (path, query, header, or JSON body for Pydantic models) and how it's validated and converted. Invalid input automatically gets a 422 with field-level errors, and the same metadata generates the OpenAPI schema and docs. Dependency injection (`Depends`) declares an endpoint's requirements, such as authentication, database sessions and settings, as reusable functions resolved per request, with cleanup via `yield`. That removes duplicated boilerplate, keeps endpoints focused on logic, and makes testing easy, because dependencies can be swapped with `dependency_overrides`.

> [!INTERVIEW] "How would you manage database sessions in FastAPI?"
> A `yield` dependency that creates a session, yields it, commits after the endpoint returns, rolls back and re-raises on any exception, and closes in `finally`. Endpoints and sub-dependencies (like `current_user`) declare it, and the per-request cache makes them share one transaction. Tests override it with a session bound to a test database or a transaction that's always rolled back.

> [!INTERVIEW] "Offset or cursor pagination?"
> Offset when the data is small or users need random page access. Keyset/cursor for large or fast-changing collections: constant cost per page via an index seek, and no duplicates or gaps when rows are inserted. Either way, use a total order (add the primary key as a tie-breaker) and cap the page size.

> [!INTERVIEW] "When is `async def` the wrong choice?"
> When the endpoint calls blocking libraries or does CPU-heavy work. Blocking the event loop stalls every concurrent request. Use `def` (thread pool) for blocking I/O and a process pool or worker service for CPU work.

## Check your understanding

1. In `def f(robot_id: int, m: MissionIn, verbose: bool = False)` for the path `/robots/{robot_id}`, where does each parameter come from?
2. Why can't `owner_token` leak when the endpoint returns the raw dict with `response_model=NoteOut`?
3. A PATCH body is `{"body": "v2"}`. What does `changes.model_dump(exclude_unset=True)` return, and why does that matter?
4. `get_session` is used by both `current_user` and the endpoint. How many sessions are opened per request?
5. A transfer endpoint debits an account, then raises `HTTPException(409)`. What makes the debit disappear?
6. Why must a sort by `battery` add `id` as a tie-breaker before paginating?

<details><summary>Answers</summary>

1. `robot_id` from the path (it's in the template), `m` from the JSON body (a Pydantic model), `verbose` from the query string (a simple type with a default).
2. FastAPI validates the return value against `NoteOut` and serialises only its declared fields. Undeclared keys are dropped.
3. `{"body": "v2"}` only. Fields that weren't sent are absent (not `None`), so the update changes only what the client asked for, and an explicit `null` can be told apart from "not sent".
4. One. Dependencies are cached per request, so both receive the same session object (and the same transaction).
5. The exception propagates into the `yield` dependency, whose `except` block rolls back the transaction before re-raising.
6. Without a total order, rows with equal battery can come back in a different order on each query, so an item can appear on two pages or on none.

</details>
