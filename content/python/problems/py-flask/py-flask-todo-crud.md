---
id: py-flask-todo-crud
title: JSON CRUD API for Todos
difficulty: Medium
order: 2
tags: Flask, REST, CRUD, JSON, validation, status codes, PUT vs PATCH, Location
time_limit: 5
---
## Statement
Build a REST API for todos with Flask. `create_app()` returns a fresh app with its **own** in-memory store (ids start at 1 and are never reused).

A todo is `{"id": int, "title": str, "done": bool}`.

| Request | Success | Errors |
|---|---|---|
| `POST /todos` | **201**, the todo, header `Location: /todos/<id>` | 415, 400 |
| `GET /todos?done=` | 200, list sorted by id; `done=true` / `done=false` filters | 400 `done must be true or false` |
| `GET /todos/<int:id>` | 200 | 404 |
| `PUT /todos/<int:id>` | 200, full replacement: `title` required, `done` defaults to `false` | 404, 415, 400 |
| `PATCH /todos/<int:id>` | 200, partial update: only the given fields change | 404, 415, 400 |
| `DELETE /todos/<int:id>` | **204**, empty body | 404 |

**Errors** are JSON `{"error": "<message>"}`:
- **404** `todo not found` (check existence first, before looking at the body).
- **415** `expected JSON` when the request's content type isn't `application/json`.
- **400** when the JSON is invalid. Check in this order and report the first failure:
  1. the body isn't a JSON object (or doesn't parse) → `body must be a JSON object`
  2. a key other than `title`/`done` → `unknown field: <name>` (first one in sorted order)
  3. `title` is required (POST, PUT) but missing → `title is required`
  4. `title` present but not a string, or empty after `strip()` → `title must be a non-empty string`
  5. `title` longer than 100 characters after stripping → `title too long`
  6. `done` present but not a JSON boolean (`1` and `"true"` are invalid) → `done must be a boolean`

Store titles **stripped**. `PATCH` with `{}` is valid and changes nothing.

## Starter
```python
from flask import Flask, request


def create_app():
    app = Flask(__name__)
    todos = []

    @app.post("/todos")
    def create():
        data = request.get_json()
        todo = {"id": len(todos) + 1, "title": data["title"], "done": False}
        todos.append(todo)
        return todo

    @app.get("/todos")
    def list_todos():
        return todos

    return app
```

## Driver
```python
import json
import sys

def show(label, r):
    body = r.get_data(as_text=True)
    loc = f" Location={r.headers['Location']}" if "Location" in r.headers else ""
    shown = json.dumps(r.get_json(silent=True), sort_keys=True) if body else "<empty>"
    print(f"{label}: {r.status_code} {shown}{loc}")

def run(g):
    app = create_app()
    c = app.test_client()
    if g == "basic":
        show("create", c.post("/todos", json={"title": "  buy milk "}))
        show("create2", c.post("/todos", json={"title": "write tests", "done": True}))
        show("list", c.get("/todos"))
        show("get1", c.get("/todos/1"))
        show("get9", c.get("/todos/9"))
        show("done=true", c.get("/todos?done=true"))
        show("done=false", c.get("/todos?done=false"))
        show("done=yes", c.get("/todos?done=yes"))
    elif g == "validate":
        show("form", c.post("/todos", data={"title": "x"}))
        show("text", c.post("/todos", data="title=x", content_type="text/plain"))
        show("broken", c.post("/todos", data="{nope", content_type="application/json"))
        show("array", c.post("/todos", json=["title"]))
        show("number", c.post("/todos", json=5))
        show("unknown", c.post("/todos", json={"title": "a", "zeta": 1, "beta": 2}))
        show("missing", c.post("/todos", json={"done": True}))
        show("blank", c.post("/todos", json={"title": "   "}))
        show("nonstr", c.post("/todos", json={"title": 42}))
        show("long", c.post("/todos", json={"title": "x" * 101}))
        show("100", c.post("/todos", json={"title": " " + "y" * 100 + " "}))
        show("done1", c.post("/todos", json={"title": "a", "done": 1}))
        show("donestr", c.post("/todos", json={"title": "a", "done": "true"}))
        show("order", c.post("/todos", json={"title": "", "done": "no"}))
        show("list", c.get("/todos"))
    elif g == "update":
        c.post("/todos", json={"title": "a"}); c.post("/todos", json={"title": "b", "done": True})
        show("put", c.put("/todos/2", json={"title": "B!"}))
        show("put missing title", c.put("/todos/1", json={"done": True}))
        show("put 404 bad body", c.put("/todos/7", json={"zzz": 1}))
        show("patch done", c.patch("/todos/1", json={"done": True}))
        show("patch title", c.patch("/todos/1", json={"title": " A "}))
        show("patch empty", c.patch("/todos/1", json={}))
        show("patch bad", c.patch("/todos/1", json={"done": None}))
        show("patch text", c.patch("/todos/1", data="x", content_type="text/plain"))
        show("list", c.get("/todos"))
    elif g == "delete":
        for t in "abc":
            c.post("/todos", json={"title": t})
        show("del2", c.delete("/todos/2"))
        show("del2 again", c.delete("/todos/2"))
        show("get2", c.get("/todos/2"))
        show("new", c.post("/todos", json={"title": "d"}))
        show("list", c.get("/todos"))
        show("patch deleted", c.patch("/todos/2", json={"done": True}))
        other = create_app().test_client()
        show("other app", other.get("/todos"))
        show("other create", other.post("/todos", json={"title": "fresh"}))

for g in sys.stdin.read().split():
    print("#", g)
    run(g)
```

## Tests
=== sample
basic
---
# basic
create: 201 {"done": false, "id": 1, "title": "buy milk"} Location=/todos/1
create2: 201 {"done": true, "id": 2, "title": "write tests"} Location=/todos/2
list: 200 [{"done": false, "id": 1, "title": "buy milk"}, {"done": true, "id": 2, "title": "write tests"}]
get1: 200 {"done": false, "id": 1, "title": "buy milk"}
get9: 404 {"error": "todo not found"}
done=true: 200 [{"done": true, "id": 2, "title": "write tests"}]
done=false: 200 [{"done": false, "id": 1, "title": "buy milk"}]
done=yes: 400 {"error": "done must be true or false"}
=== hidden
validate
---
# validate
form: 415 {"error": "expected JSON"}
text: 415 {"error": "expected JSON"}
broken: 400 {"error": "body must be a JSON object"}
array: 400 {"error": "body must be a JSON object"}
number: 400 {"error": "body must be a JSON object"}
unknown: 400 {"error": "unknown field: beta"}
missing: 400 {"error": "title is required"}
blank: 400 {"error": "title must be a non-empty string"}
nonstr: 400 {"error": "title must be a non-empty string"}
long: 400 {"error": "title too long"}
100: 201 {"done": false, "id": 1, "title": "yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"} Location=/todos/1
done1: 400 {"error": "done must be a boolean"}
donestr: 400 {"error": "done must be a boolean"}
order: 400 {"error": "title must be a non-empty string"}
list: 200 [{"done": false, "id": 1, "title": "yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"}]
=== hidden
update
---
# update
put: 200 {"done": false, "id": 2, "title": "B!"}
put missing title: 400 {"error": "title is required"}
put 404 bad body: 404 {"error": "todo not found"}
patch done: 200 {"done": true, "id": 1, "title": "a"}
patch title: 200 {"done": true, "id": 1, "title": "A"}
patch empty: 200 {"done": true, "id": 1, "title": "A"}
patch bad: 400 {"error": "done must be a boolean"}
patch text: 415 {"error": "expected JSON"}
list: 200 [{"done": true, "id": 1, "title": "A"}, {"done": false, "id": 2, "title": "B!"}]
=== hidden
delete
---
# delete
del2: 204 <empty>
del2 again: 404 {"error": "todo not found"}
get2: 404 {"error": "todo not found"}
new: 201 {"done": false, "id": 4, "title": "d"} Location=/todos/4
list: 200 [{"done": false, "id": 1, "title": "a"}, {"done": false, "id": 3, "title": "c"}, {"done": false, "id": 4, "title": "d"}]
patch deleted: 404 {"error": "todo not found"}
other app: 200 []
other create: 201 {"done": false, "id": 1, "title": "fresh"} Location=/todos/1

## Hints
- Write one helper that validates a body and returns either the clean fields or an error response, with a flag for "title required".
- `request.is_json` → 415 check. `request.get_json(silent=True)` gives `None` for broken JSON. `isinstance(x, dict)` and `isinstance(x, bool)` do the rest.
- Return tuples from views: `(body, 201, {"Location": ...})` and `("", 204)`. Keep a separate id counter so deleted ids aren't reused.

## Solution
**One validator, two modes.** POST and PUT require a full representation, while PATCH accepts any subset. A single `parse_body(require_title)` keeps the rules (and their order) in one place. That order matters to clients: check the content type (415), then the shape (400 for non-objects and unknown fields), then each field.

**Strict types.** `request.is_json` checks the `Content-Type`. `get_json(silent=True)` returns `None` instead of raising on broken JSON. JSON booleans arrive as Python `bool`, so `isinstance(v, bool)` rejects `1` and `"true"`. Never use truthiness for validation.

**REST semantics.**
- 201 + `Location` tells the client where the new resource lives.
- PUT replaces, so an omitted `done` resets to `false`. PATCH merges.
- DELETE returns 204 with no body, and a second DELETE returns 404 (the state is the same, which makes DELETE idempotent).
- Ids come from a counter, not `len(todos) + 1`, so they're never reused after a delete (a reused id would make stale client links point at the wrong todo).

**Isolation.** The store lives inside `create_app`, so every app (and every test) starts empty.

Complexity: O(1) per single-item operation, O(n log n) for the sorted list.

```python
from flask import Flask, request

FIELDS = {"title", "done"}


def create_app():
    app = Flask(__name__)
    todos: dict[int, dict] = {}
    next_id = [1]

    def err(status, message):
        return {"error": message}, status

    def parse_body(require_title):
        """Return (clean_fields, None) or (None, error_response)."""
        if not request.is_json:
            return None, err(415, "expected JSON")
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return None, err(400, "body must be a JSON object")
        unknown = sorted(set(data) - FIELDS)
        if unknown:
            return None, err(400, f"unknown field: {unknown[0]}")
        clean = {}
        if "title" not in data:
            if require_title:
                return None, err(400, "title is required")
        else:
            t = data["title"]
            if not isinstance(t, str) or not t.strip():
                return None, err(400, "title must be a non-empty string")
            if len(t.strip()) > 100:
                return None, err(400, "title too long")
            clean["title"] = t.strip()
        if "done" in data:
            if not isinstance(data["done"], bool):
                return None, err(400, "done must be a boolean")
            clean["done"] = data["done"]
        return clean, None

    def find(todo_id):
        return todos.get(todo_id)

    @app.post("/todos")
    def create():
        fields, error = parse_body(require_title=True)
        if error:
            return error
        todo = {"id": next_id[0], "title": fields["title"], "done": fields.get("done", False)}
        todos[todo["id"]] = todo
        next_id[0] += 1
        return todo, 201, {"Location": f"/todos/{todo['id']}"}

    @app.get("/todos")
    def list_todos():
        done = request.args.get("done")
        if done not in (None, "true", "false"):
            return err(400, "done must be true or false")
        items = [todos[k] for k in sorted(todos)]
        if done is not None:
            items = [t for t in items if t["done"] == (done == "true")]
        return items

    @app.get("/todos/<int:todo_id>")
    def get_todo(todo_id):
        todo = find(todo_id)
        return todo if todo else err(404, "todo not found")

    @app.put("/todos/<int:todo_id>")
    def replace(todo_id):
        todo = find(todo_id)
        if todo is None:
            return err(404, "todo not found")
        fields, error = parse_body(require_title=True)
        if error:
            return error
        todo.update(title=fields["title"], done=fields.get("done", False))
        return todo

    @app.patch("/todos/<int:todo_id>")
    def update(todo_id):
        todo = find(todo_id)
        if todo is None:
            return err(404, "todo not found")
        fields, error = parse_body(require_title=False)
        if error:
            return error
        todo.update(fields)
        return todo

    @app.delete("/todos/<int:todo_id>")
    def delete(todo_id):
        if todos.pop(todo_id, None) is None:
            return err(404, "todo not found")
        return "", 204

    return app
```
