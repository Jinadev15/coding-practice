---
id: py-flask-error-handlers
title: Error Handlers and a Consistent Error Model
difficulty: Medium
order: 6
tags: Flask, errorhandler, HTTPException, custom exceptions, validation, 413, 500, logging, JSON errors
time_limit: 5
---
## Statement
Clients of a JSON API need **every** error, including 404s, 405s, oversized bodies and crashes, in the same shape:

```json
{"error": {"code": "<snake_case_code>", "message": "<human text>", "details": [...]}}
```

`details` is a list (empty when there's nothing to add).

```python
class ApiError(Exception):
    def __init__(self, status: int, code: str, message: str, details: list | None = None): ...

def create_app() -> Flask: ...
```

**Handlers** (register them on the app):
1. `ApiError` → its own status, code, message and details.
2. Any `werkzeug.exceptions.HTTPException` (404, 405, 413, 418, …) → its status, with `code` = the exception's `name` lower-cased and with spaces and apostrophes replaced by `_` (`Not Found` → `not_found`, `I'm a teapot` → `i_m_a_teapot`), and `message` = its `description`. **Keep the exception's own headers** (a 405 must still carry `Allow`): use `e.get_response()` and replace its body.
3. Any other `Exception` → **500**, code `internal_error`, message `internal server error`, empty details. Never leak the exception text to the client. Log it instead with `app.logger.exception(...)`.

Set `MAX_CONTENT_LENGTH = 1024` (bigger bodies give werkzeug's 413).

**Endpoints:**
- `POST /orders` validates a JSON body and returns **201** `{"order": {"items": [...], "total_qty": n}}`.
  - Not JSON, or JSON that doesn't parse → `ApiError(400, "bad_json", "body must be valid JSON")`.
  - Then collect **all** problems (don't stop at the first) and raise `ApiError(422, "validation_failed", "invalid order", details)` where each detail is `{"field": ..., "msg": ...}`:
    - the body isn't an object → `{"field": "$", "msg": "must be an object"}` (and nothing else is checked);
    - `items` missing or not a non-empty list → `{"field": "items", "msg": "must be a non-empty list"}`;
    - for each `items[i]`: not an object → `{"field": "items[i]", "msg": "must be an object"}`; otherwise `sku` must be a string whose **whole** value matches `[A-Z]{3}-[0-9]{3}` (use `re.fullmatch`: `$` would also accept a trailing newline) (`"items[i].sku"`, `"invalid sku"`), and `qty` must be an int (not bool) from 1 to 99 (`"items[i].qty"`, `"must be an integer 1..99"`).
    - Details are in that order: items by index, and `sku` before `qty`.
- `GET /orders/<int:oid>` → always raises `ApiError(404, "order_not_found", "order <oid> does not exist")`.
- `GET /boom` → divides by zero (a bug). The client gets the generic 500.
- `GET /teapot` → `abort(418)`.

Don't set `TESTING = True`, because that makes Flask re-raise exceptions instead of calling your 500 handler.

## Starter
```python
from flask import Flask, abort, request


class ApiError(Exception):
    def __init__(self, status, code, message, details=None):
        super().__init__(message)
        self.status, self.code, self.message, self.details = status, code, message, details or []


def create_app():
    app = Flask(__name__)

    @app.post("/orders")
    def orders():
        data = request.get_json()
        return {"order": {"items": data["items"], "total_qty": sum(i["qty"] for i in data["items"])}}, 201

    @app.get("/boom")
    def boom():
        return str(1 / 0)

    return app
```

## Driver
```python
import json
import logging
import sys

class Capture(logging.Handler):
    def __init__(self):
        super().__init__()
        self.records = []
    def emit(self, record):
        self.records.append((record.levelname, record.exc_info[0].__name__ if record.exc_info else None))

def show(label, r):
    j = r.get_json(silent=True)
    allow = f" Allow={', '.join(sorted(r.headers['Allow'].split(', ')))}" if "Allow" in r.headers else ""
    print(f"{label}: {r.status_code} {r.mimetype}{allow} {json.dumps(j, sort_keys=True) if j is not None else r.get_data(as_text=True)[:60]!s}")

for g in sys.stdin.read().split():
    print("#", g)
    app = create_app()
    cap = Capture()
    app.logger.handlers = [cap]
    app.logger.propagate = False
    c = app.test_client()
    if g == "http":
        show("404", c.get("/nowhere"))
        show("405", c.delete("/orders"))
        show("418", c.get("/teapot"))
        show("order 7", c.get("/orders/7"))
        show("order x", c.get("/orders/x"))
    elif g == "crash":
        show("boom", c.get("/boom"))
        print("logged:", cap.records)
        show("413", c.post("/orders", data="x" * 2000, content_type="application/json"))
        print("logged after 413:", cap.records)
    elif g == "valid":
        show("ok", c.post("/orders", json={"items": [{"sku": "PEN-001", "qty": 2}, {"sku": "INK-042", "qty": 99}]}))
        show("one", c.post("/orders", json={"items": [{"sku": "ABC-123", "qty": 1}]}))
        show("text", c.post("/orders", data="hello", content_type="text/plain"))
        show("broken", c.post("/orders", data="{bad json", content_type="application/json"))
        show("list body", c.post("/orders", json=[1, 2]))
        show("no items", c.post("/orders", json={}))
        show("empty items", c.post("/orders", json={"items": []}))
        show("items str", c.post("/orders", json={"items": "PEN-001"}))
    elif g == "details":
        show("many", c.post("/orders", json={"items": [
            {"sku": "PEN-001", "qty": 0}, "oops", {"sku": "pen-001", "qty": True}, {"qty": 5},
            {"sku": "PEN-0011", "qty": 100}, {"sku": "INK-042", "qty": 3}, {"sku": 7, "qty": "2"}, {"sku": "PEN-001\n", "qty": 1}]}))
        show("float qty", c.post("/orders", json={"items": [{"sku": "ABC-999", "qty": 2.0}]}))
        show("bounds", c.post("/orders", json={"items": [{"sku": "ZZZ-000", "qty": 99}, {"sku": "AAA-999", "qty": 1}]}))
        print("logged:", cap.records)
```

## Tests
=== sample
http
---
# http
404: 404 application/json {"error": {"code": "not_found", "details": [], "message": "The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again."}}
405: 405 application/json Allow=OPTIONS, POST {"error": {"code": "method_not_allowed", "details": [], "message": "The method is not allowed for the requested URL."}}
418: 418 application/json {"error": {"code": "i_m_a_teapot", "details": [], "message": "This server is a teapot, not a coffee machine"}}
order 7: 404 application/json {"error": {"code": "order_not_found", "details": [], "message": "order 7 does not exist"}}
order x: 404 application/json {"error": {"code": "not_found", "details": [], "message": "The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again."}}
=== hidden
crash
---
# crash
boom: 500 application/json {"error": {"code": "internal_error", "details": [], "message": "internal server error"}}
logged: [('ERROR', 'ZeroDivisionError')]
413: 413 application/json {"error": {"code": "request_entity_too_large", "details": [], "message": "The data value transmitted exceeds the capacity limit."}}
logged after 413: [('ERROR', 'ZeroDivisionError')]
=== hidden
valid
---
# valid
ok: 201 application/json {"order": {"items": [{"qty": 2, "sku": "PEN-001"}, {"qty": 99, "sku": "INK-042"}], "total_qty": 101}}
one: 201 application/json {"order": {"items": [{"qty": 1, "sku": "ABC-123"}], "total_qty": 1}}
text: 400 application/json {"error": {"code": "bad_json", "details": [], "message": "body must be valid JSON"}}
broken: 400 application/json {"error": {"code": "bad_json", "details": [], "message": "body must be valid JSON"}}
list body: 422 application/json {"error": {"code": "validation_failed", "details": [{"field": "$", "msg": "must be an object"}], "message": "invalid order"}}
no items: 422 application/json {"error": {"code": "validation_failed", "details": [{"field": "items", "msg": "must be a non-empty list"}], "message": "invalid order"}}
empty items: 422 application/json {"error": {"code": "validation_failed", "details": [{"field": "items", "msg": "must be a non-empty list"}], "message": "invalid order"}}
items str: 422 application/json {"error": {"code": "validation_failed", "details": [{"field": "items", "msg": "must be a non-empty list"}], "message": "invalid order"}}
=== hidden
details
---
# details
many: 422 application/json {"error": {"code": "validation_failed", "details": [{"field": "items[0].qty", "msg": "must be an integer 1..99"}, {"field": "items[1]", "msg": "must be an object"}, {"field": "items[2].sku", "msg": "invalid sku"}, {"field": "items[2].qty", "msg": "must be an integer 1..99"}, {"field": "items[3].sku", "msg": "invalid sku"}, {"field": "items[4].sku", "msg": "invalid sku"}, {"field": "items[4].qty", "msg": "must be an integer 1..99"}, {"field": "items[6].sku", "msg": "invalid sku"}, {"field": "items[6].qty", "msg": "must be an integer 1..99"}, {"field": "items[7].sku", "msg": "invalid sku"}], "message": "invalid order"}}
float qty: 422 application/json {"error": {"code": "validation_failed", "details": [{"field": "items[0].qty", "msg": "must be an integer 1..99"}], "message": "invalid order"}}
bounds: 201 application/json {"order": {"items": [{"qty": 99, "sku": "ZZZ-000"}, {"qty": 1, "sku": "AAA-999"}], "total_qty": 100}}
logged: []

## Hints
- `@app.errorhandler(ApiError)`, `@app.errorhandler(HTTPException)` and `@app.errorhandler(Exception)`: Flask picks the most specific one.
- For HTTP errors: `resp = e.get_response()`, then `resp.set_data(json_text)` and `resp.mimetype = "application/json"`. The name-to-code mapping is `re.sub(r"[ ']", "_", e.name.lower())`.
- Validate into a list of `{"field", "msg"}` dicts, and use `continue` after a non-object item. `type(x) is int` rejects bools and floats.

## Solution
**Handler resolution.** Flask looks for the most specific registered handler along the exception's class hierarchy (MRO). `ApiError` gets its own handler. Every werkzeug HTTP error (`NotFound`, `MethodNotAllowed`, `RequestEntityTooLarge`, …) is an `HTTPException`. `Exception` catches the rest, which are real bugs.

**Keep protocol headers.** `e.get_response()` builds werkzeug's response, including headers such as `Allow` for 405. Replacing only its body keeps the HTTP semantics while unifying the format. Returning a fresh dict would silently drop `Allow`.

**Don't leak internals.** The 500 handler returns a generic message, and `app.logger.exception` records the traceback for the developers. Stack traces in responses help attackers map your code.

**Validation that helps the client.** Collecting *all* field errors with precise paths (`items[2].qty`) lets a client fix everything in one round trip. Type checks are strict: `type(qty) is not int` rejects `True` (a `bool` is an `int` subclass) and `2.0`.

**400 vs 422.** Unparseable input is 400. Well-formed JSON with invalid content is 422.

Complexity: O(number of items).

```python
import re

from flask import Flask, abort, request
from werkzeug.exceptions import HTTPException

SKU = re.compile(r"[A-Z]{3}-[0-9]{3}")


class ApiError(Exception):
    def __init__(self, status, code, message, details=None):
        super().__init__(message)
        self.status, self.code, self.message, self.details = status, code, message, details or []


def error_body(code, message, details=None):
    return {"error": {"code": code, "message": message, "details": details or []}}


def validate_order(data):
    if not isinstance(data, dict):
        return [{"field": "$", "msg": "must be an object"}]
    errs = []
    items = data.get("items")
    if not isinstance(items, list) or not items:
        return [{"field": "items", "msg": "must be a non-empty list"}]
    for i, it in enumerate(items):
        if not isinstance(it, dict):
            errs.append({"field": f"items[{i}]", "msg": "must be an object"})
            continue
        sku, qty = it.get("sku"), it.get("qty")
        if not isinstance(sku, str) or not SKU.fullmatch(sku):
            errs.append({"field": f"items[{i}].sku", "msg": "invalid sku"})
        if type(qty) is not int or not 1 <= qty <= 99:
            errs.append({"field": f"items[{i}].qty", "msg": "must be an integer 1..99"})
    return errs


def create_app():
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 1024

    @app.errorhandler(ApiError)
    def api_error(e):
        return error_body(e.code, e.message, e.details), e.status

    @app.errorhandler(HTTPException)
    def http_error(e):
        resp = e.get_response()                       # keeps headers such as Allow
        code = re.sub(r"[ ']", "_", e.name.lower())
        resp.set_data(app.json.dumps(error_body(code, e.description)))
        resp.mimetype = "application/json"
        return resp

    @app.errorhandler(Exception)
    def unexpected(e):
        app.logger.exception("unhandled error on %s", request.path)
        return error_body("internal_error", "internal server error"), 500

    @app.post("/orders")
    def orders():
        if not request.is_json:
            raise ApiError(400, "bad_json", "body must be valid JSON")
        data = request.get_json(silent=True)
        if data is None:
            raise ApiError(400, "bad_json", "body must be valid JSON")
        errs = validate_order(data)
        if errs:
            raise ApiError(422, "validation_failed", "invalid order", errs)
        return {"order": {"items": data["items"], "total_qty": sum(i["qty"] for i in data["items"])}}, 201

    @app.get("/orders/<int:oid>")
    def get_order(oid):
        raise ApiError(404, "order_not_found", f"order {oid} does not exist")

    @app.get("/boom")
    def boom():
        return str(1 / 0)

    @app.get("/teapot")
    def teapot():
        abort(418)

    return app
```
