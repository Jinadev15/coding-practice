---
id: py-fastapi-error-model
title: Domain Exceptions and Problem Details Errors
difficulty: Medium
order: 5
tags: FastAPI, exception_handler, RequestValidationError, HTTPException, RFC 9457 problem details, service layer, 500 handling
time_limit: 10
---
## Statement
Keep HTTP out of your business logic: the **service layer** raises domain exceptions, and FastAPI **exception handlers** translate them into one standard error format, *problem details* (RFC 9457, formerly RFC 7807), sent with media type `application/problem+json`:

```json
{"type": "/errors/not-found", "title": "Not Found", "status": 404, "detail": "item ABC-001 not found"}
```

```python
class DomainError(Exception): ...            # .detail: str
class NotFound(DomainError): ...
class Conflict(DomainError): ...
class RuleViolation(DomainError): ...

class Inventory:                             # pure Python: no FastAPI imports used here
    def add(self, sku: str, stock: int) -> dict        # Conflict "item <sku> already exists"
    def get(self, sku: str) -> dict                    # NotFound "item <sku> not found"
    def reserve(self, sku: str, qty: int) -> dict      # NotFound; RuleViolation "only <stock> left"
                                                       # items are {"sku": str, "stock": int}
def create_app() -> FastAPI: ...
```

**Mapping** (register handlers with `@app.exception_handler(...)`):

| Exception | status | type | title |
|---|---|---|---|
| `NotFound` | 404 | `/errors/not-found` | `Not Found` |
| `Conflict` | 409 | `/errors/conflict` | `Conflict` |
| `RuleViolation` | 422 | `/errors/rule-violation` | `Rule Violation` |
| `RequestValidationError` | 422 | `/errors/validation` | `Invalid Request`; `detail` = `"<n> invalid field(s)"`, plus `"fields"`: the error `loc`s joined with `.` (e.g. `body.qty`), in the order FastAPI reports them |
| Starlette `HTTPException` (unknown route, 405, …) | its status | `about:blank` | the standard reason phrase (`http.HTTPStatus(code).phrase`); `detail` = the exception's detail. Keep its headers (a 405 has `Allow`) |
| any other `Exception` | 500 | `/errors/internal` | `Internal Server Error`; `detail` = `unexpected error`. Never echo the exception message |

The `detail` of domain errors is the exception's `detail` text.

**Endpoints** (one `Inventory` per app):
- `POST /items`, body `{"sku": "^[A-Z]{3}-[0-9]{3}$", "stock": int >= 0}` → **201** item.
- `GET /items/{sku}` → item.
- `POST /items/{sku}/reserve`, body `{"qty": int 1..1000}` → item with the reduced stock. Reserving more than the stock raises `RuleViolation` and changes nothing.
- `GET /crash` → raises `RuntimeError("db password=hunter2")` (a simulated bug).

## Starter
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class DomainError(Exception):
    def __init__(self, detail):
        super().__init__(detail)
        self.detail = detail


class NotFound(DomainError): pass
class Conflict(DomainError): pass
class RuleViolation(DomainError): pass


class Inventory:
    def __init__(self):
        self.items = {}

    def add(self, sku, stock):
        self.items[sku] = {"sku": sku, "stock": stock}
        return self.items[sku]

    def get(self, sku):
        return self.items[sku]

    def reserve(self, sku, qty):
        self.items[sku]["stock"] -= qty
        return self.items[sku]


def create_app():
    app = FastAPI()
    inv = Inventory()

    @app.get("/items/{sku}")
    def get_item(sku: str):
        try:
            return inv.get(sku)
        except KeyError:
            raise HTTPException(404, "not found")

    return app
```

## Driver
```python
import json
import sys
import warnings
warnings.simplefilter("ignore")
from fastapi.testclient import TestClient

def show(label, r):
    allow = f" Allow={r.headers['allow']}" if "allow" in r.headers else ""
    print(f"{label}: {r.status_code} {r.headers.get('content-type')}{allow} {json.dumps(r.json(), sort_keys=True)}")

for g in sys.stdin.read().split():
    print("#", g)
    app = create_app()
    c = TestClient(app, raise_server_exceptions=False)
    if g == "domain":
        show("add", c.post("/items", json={"sku": "ABC-001", "stock": 5}))
        show("dup", c.post("/items", json={"sku": "ABC-001", "stock": 9}))
        show("get", c.get("/items/ABC-001"))
        show("missing", c.get("/items/ZZZ-999"))
        show("reserve", c.post("/items/ABC-001/reserve", json={"qty": 2}))
        show("too many", c.post("/items/ABC-001/reserve", json={"qty": 4}))
        show("exact", c.post("/items/ABC-001/reserve", json={"qty": 3}))
        show("empty", c.post("/items/ABC-001/reserve", json={"qty": 1}))
        show("reserve missing", c.post("/items/NOP-000/reserve", json={"qty": 1}))
        show("get", c.get("/items/ABC-001"))
    elif g == "validation":
        show("bad sku", c.post("/items", json={"sku": "abc-1", "stock": 1}))
        show("two bad", c.post("/items", json={"sku": "ABC-0011", "stock": -1}))
        show("missing all", c.post("/items", json={}))
        show("not json", c.post("/items", content="nope", headers={"content-type": "application/json"}))
        c.post("/items", json={"sku": "QQQ-111", "stock": 1})
        show("qty 0", c.post("/items/QQQ-111/reserve", json={"qty": 0}))
        show("qty big", c.post("/items/QQQ-111/reserve", json={"qty": 1001}))
        show("qty str", c.post("/items/QQQ-111/reserve", json={"qty": "many"}))
    elif g == "http":
        show("no route", c.get("/nothing/here"))
        show("wrong method", c.delete("/items"))
        show("crash", c.get("/crash"))
        r = c.get("/crash")
        print("leaks secret:", "hunter2" in r.text)
        show("still works", c.post("/items", json={"sku": "OKK-200", "stock": 0}))
    elif g == "layering":
        inv = Inventory()
        print(inv.add("AAA-000", 3))
        for call in [lambda: inv.add("AAA-000", 1), lambda: inv.get("BBB-111"), lambda: inv.reserve("AAA-000", 4),
                     lambda: inv.reserve("CCC-222", 1)]:
            try:
                call()
            except DomainError as e:
                print(type(e).__name__, "|", e.detail, "|", isinstance(e, Exception))
        print(inv.reserve("AAA-000", 3), inv.get("AAA-000"))
        import inspect
        src = inspect.getsource(Inventory)
        print("service imports HTTP:", "HTTPException" in src or "status_code" in src)
```

## Tests
=== sample
domain
---
# domain
add: 201 application/json {"sku": "ABC-001", "stock": 5}
dup: 409 application/problem+json {"detail": "item ABC-001 already exists", "status": 409, "title": "Conflict", "type": "/errors/conflict"}
get: 200 application/json {"sku": "ABC-001", "stock": 5}
missing: 404 application/problem+json {"detail": "item ZZZ-999 not found", "status": 404, "title": "Not Found", "type": "/errors/not-found"}
reserve: 200 application/json {"sku": "ABC-001", "stock": 3}
too many: 422 application/problem+json {"detail": "only 3 left", "status": 422, "title": "Rule Violation", "type": "/errors/rule-violation"}
exact: 200 application/json {"sku": "ABC-001", "stock": 0}
empty: 422 application/problem+json {"detail": "only 0 left", "status": 422, "title": "Rule Violation", "type": "/errors/rule-violation"}
reserve missing: 404 application/problem+json {"detail": "item NOP-000 not found", "status": 404, "title": "Not Found", "type": "/errors/not-found"}
get: 200 application/json {"sku": "ABC-001", "stock": 0}
=== hidden
validation
---
# validation
bad sku: 422 application/problem+json {"detail": "1 invalid field(s)", "fields": ["body.sku"], "status": 422, "title": "Invalid Request", "type": "/errors/validation"}
two bad: 422 application/problem+json {"detail": "2 invalid field(s)", "fields": ["body.sku", "body.stock"], "status": 422, "title": "Invalid Request", "type": "/errors/validation"}
missing all: 422 application/problem+json {"detail": "2 invalid field(s)", "fields": ["body.sku", "body.stock"], "status": 422, "title": "Invalid Request", "type": "/errors/validation"}
not json: 422 application/problem+json {"detail": "1 invalid field(s)", "fields": ["body.0"], "status": 422, "title": "Invalid Request", "type": "/errors/validation"}
qty 0: 422 application/problem+json {"detail": "1 invalid field(s)", "fields": ["body.qty"], "status": 422, "title": "Invalid Request", "type": "/errors/validation"}
qty big: 422 application/problem+json {"detail": "1 invalid field(s)", "fields": ["body.qty"], "status": 422, "title": "Invalid Request", "type": "/errors/validation"}
qty str: 422 application/problem+json {"detail": "1 invalid field(s)", "fields": ["body.qty"], "status": 422, "title": "Invalid Request", "type": "/errors/validation"}
=== hidden
http
---
# http
no route: 404 application/problem+json {"detail": "Not Found", "status": 404, "title": "Not Found", "type": "about:blank"}
wrong method: 405 application/problem+json Allow=POST {"detail": "Method Not Allowed", "status": 405, "title": "Method Not Allowed", "type": "about:blank"}
crash: 500 application/problem+json {"detail": "unexpected error", "status": 500, "title": "Internal Server Error", "type": "/errors/internal"}
leaks secret: False
still works: 201 application/json {"sku": "OKK-200", "stock": 0}
=== hidden
layering
---
# layering
{'sku': 'AAA-000', 'stock': 3}
Conflict | item AAA-000 already exists | True
NotFound | item BBB-111 not found | True
RuleViolation | only 3 left | True
NotFound | item CCC-222 not found | True
{'sku': 'AAA-000', 'stock': 0} {'sku': 'AAA-000', 'stock': 0}
service imports HTTP: False

## Hints
- Raise domain exceptions in `Inventory`, and give each subclass a row in a dict `{cls: (status, type, title)}` used by a single `@app.exception_handler(DomainError)`.
- `RequestValidationError.errors()` gives dicts with `loc` tuples: `".".join(map(str, e["loc"]))`. Import Starlette's `HTTPException` (`starlette.exceptions`) to also catch routing 404/405s, and pass `exc.headers`.
- Build every error with one helper returning `JSONResponse(body, status_code=..., headers=..., media_type="application/problem+json")`. Register `@app.exception_handler(Exception)` for the 500.

## Solution
**Layering.** `Inventory` knows nothing about HTTP. It raises `NotFound`, `Conflict` and `RuleViolation`, so the same service works from a CLI, a queue worker or a test. The web layer owns the translation in **one place**: a mapping from exception class to status, type and title. Adding a new error kind means one new row, not a hunt through every endpoint.

**One error format for everything.** Clients shouldn't need three parsers. Domain errors, framework validation errors (`RequestValidationError`), routing errors (Starlette's `HTTPException`, which FastAPI's own `HTTPException` subclasses) and crashes all produce the same problem-details shape with `application/problem+json`. Handlers are matched by the exception's class hierarchy, so one `DomainError` handler covers all its subclasses.

**Preserve protocol details.** A 405 must keep its `Allow` header, so pass `exc.headers` through.

**Never leak internals.** The catch-all handler returns a fixed message. The exception text (`db password=...`) would hand an attacker your internals, so log it server-side instead. In production, add a request id to both the log and the response so support can correlate them.

**422 for both kinds of validation.** A malformed field (schema) and a broken business rule (not enough stock) are both "understood but can't be processed". Their `type` URIs tell them apart.

Complexity: O(1) per request.

```python
from http import HTTPStatus
from typing import Annotated

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException as StarletteHTTPException


class DomainError(Exception):
    def __init__(self, detail):
        super().__init__(detail)
        self.detail = detail


class NotFound(DomainError): pass
class Conflict(DomainError): pass
class RuleViolation(DomainError): pass


class Inventory:
    def __init__(self):
        self.items = {}

    def add(self, sku, stock):
        if sku in self.items:
            raise Conflict(f"item {sku} already exists")
        self.items[sku] = {"sku": sku, "stock": stock}
        return dict(self.items[sku])

    def get(self, sku):
        if sku not in self.items:
            raise NotFound(f"item {sku} not found")
        return dict(self.items[sku])

    def reserve(self, sku, qty):
        item = self.items.get(sku)
        if item is None:
            raise NotFound(f"item {sku} not found")
        if qty > item["stock"]:
            raise RuleViolation(f"only {item['stock']} left")
        item["stock"] -= qty
        return dict(item)


class ItemIn(BaseModel):
    sku: Annotated[str, Field(pattern=r"^[A-Z]{3}-[0-9]{3}$")]
    stock: Annotated[int, Field(ge=0)]


class ReserveIn(BaseModel):
    qty: Annotated[int, Field(ge=1, le=1000)]


MAPPING = {
    NotFound: (404, "/errors/not-found", "Not Found"),
    Conflict: (409, "/errors/conflict", "Conflict"),
    RuleViolation: (422, "/errors/rule-violation", "Rule Violation"),
}


def problem(status, type_, title, detail, headers=None, **extra):
    body = {"type": type_, "title": title, "status": status, "detail": detail, **extra}
    return JSONResponse(body, status_code=status, headers=headers, media_type="application/problem+json")


def create_app():
    app = FastAPI()
    inv = Inventory()

    @app.exception_handler(DomainError)
    async def domain_error(request: Request, exc: DomainError):
        status, type_, title = MAPPING[type(exc)]
        return problem(status, type_, title, exc.detail)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        fields = [".".join(str(p) for p in e["loc"]) for e in exc.errors()]
        return problem(422, "/errors/validation", "Invalid Request", f"{len(fields)} invalid field(s)", fields=fields)

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException):
        return problem(exc.status_code, "about:blank", HTTPStatus(exc.status_code).phrase, exc.detail,
                       headers=getattr(exc, "headers", None))

    @app.exception_handler(Exception)
    async def unexpected(request: Request, exc: Exception):
        return problem(500, "/errors/internal", "Internal Server Error", "unexpected error")

    @app.post("/items", status_code=201)
    def add_item(body: ItemIn):
        return inv.add(body.sku, body.stock)

    @app.get("/items/{sku}")
    def get_item(sku: str):
        return inv.get(sku)

    @app.post("/items/{sku}/reserve")
    def reserve(sku: str, body: ReserveIn):
        return inv.reserve(sku, body.qty)

    @app.get("/crash")
    def crash():
        raise RuntimeError("db password=hunter2")

    return app
```
