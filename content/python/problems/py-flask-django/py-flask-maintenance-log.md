---
id: py-flask-maintenance-log
title: A Flask Maintenance-Log Service
difficulty: Medium
order: 1
tags: Flask, application factory, blueprints, JSON APIs, error handlers, test client
time_limit: 15
---
## Statement
Technicians log maintenance notes for each robot. Build the service with **Flask**: implement `create_app(config=None) -> Flask` using a **Blueprint** mounted at `/api/v1`. The judge uses `app.test_client()`.

**Configuration**: `MAX_LOGS_PER_ROBOT` (default 1000). When a robot exceeds it, its **oldest** entries are dropped. `config` (a dict) overrides the defaults.

**Endpoints** (all JSON):

| Route | Behaviour |
|---|---|
| `POST /api/v1/robots/<name>/logs` | Body `{"severity": "info"\|"warn"\|"error", "msg": str}`. Returns **201** `{"id", "robot", "severity", "msg"}`. Ids increase from 1 across all robots. |
| `GET /api/v1/robots/<name>/logs?severity=&limit=` | That robot's entries, **newest first**, optionally filtered by severity. `limit` defaults to 50 and must be an integer 1–100. An unknown robot gives an empty list. |
| `GET /api/v1/summary` | `{robot: {"info": a, "warn": b, "error": c}}` over the current entries. Robots with no entries are omitted. |
| `DELETE /api/v1/logs/<int:log_id>` | **204** with an empty body, or 404. |

**Errors** are always JSON `{"error": message}`:
- 400 when the body isn't a JSON object: `"body must be a JSON object"`.
- 400 for a bad severity: `"invalid severity"`.
- 400 when `msg` is missing, not a string, empty after stripping, or over 200 characters: `"invalid msg"`.
- 400 for a bad limit: `"invalid limit"`. A severity filter that isn't one of the three also gives `"invalid severity"`.
- **404 for anything not found, including unknown URLs**: `"not found"`.
- **405** for a wrong method: `"method not allowed"`.

Store `msg` stripped. Robot names are any URL path segment.

## Starter
```python
from flask import Flask, jsonify, request


def create_app(config=None):
    app = Flask(__name__)
    logs = []

    @app.post("/api/v1/robots/<name>/logs")
    def add(name):
        data = request.get_json()
        logs.append({"id": len(logs) + 1, "robot": name, **data})
        return jsonify(logs[-1])

    @app.get("/api/v1/robots/<name>/logs")
    def get(name):
        return jsonify([l for l in logs if l["robot"] == name])

    return app
```

## Driver
```python
import json
import sys

def show(label, r):
    body = r.get_data(as_text=True)
    try:
        body = json.dumps(json.loads(body), sort_keys=True) if body else "<empty>"
    except ValueError:
        body = "<non-json>"
    print(f"{label}: {r.status_code} {body}")

for cmd in sys.stdin.read().split():
    app = create_app({"TESTING": True})
    c = app.test_client()
    P = "/api/v1"
    if cmd == "basic":
        show("add1", c.post(f"{P}/robots/rover/logs", json={"severity": "info", "msg": "  boot ok "}))
        show("add2", c.post(f"{P}/robots/rover/logs", json={"severity": "warn", "msg": "wheel slip"}))
        show("add3", c.post(f"{P}/robots/arm/logs", json={"severity": "error", "msg": "joint 3 overheat"}))
        show("add4", c.post(f"{P}/robots/rover/logs", json={"severity": "error", "msg": "lidar timeout"}))
        show("rover", c.get(f"{P}/robots/rover/logs"))
        show("rover warn", c.get(f"{P}/robots/rover/logs?severity=warn"))
        show("rover limit", c.get(f"{P}/robots/rover/logs?limit=2"))
        show("ghost", c.get(f"{P}/robots/ghost/logs"))
        show("summary", c.get(f"{P}/summary"))
        show("delete", c.delete(f"{P}/logs/2"))
        show("delete again", c.delete(f"{P}/logs/2"))
        show("summary", c.get(f"{P}/summary"))
    elif cmd == "errors":
        show("no json", c.post(f"{P}/robots/r/logs", data="hello", content_type="text/plain"))
        show("list body", c.post(f"{P}/robots/r/logs", json=[1, 2]))
        show("bad sev", c.post(f"{P}/robots/r/logs", json={"severity": "fatal", "msg": "x"}))
        show("no msg", c.post(f"{P}/robots/r/logs", json={"severity": "info"}))
        show("blank msg", c.post(f"{P}/robots/r/logs", json={"severity": "info", "msg": "   "}))
        show("num msg", c.post(f"{P}/robots/r/logs", json={"severity": "info", "msg": 5}))
        show("long msg", c.post(f"{P}/robots/r/logs", json={"severity": "info", "msg": "x" * 201}))
        show("max msg", c.post(f"{P}/robots/r/logs", json={"severity": "info", "msg": "y" * 200}).status_code and c.get(f"{P}/robots/r/logs?limit=1"))
        for q in ["limit=0", "limit=101", "limit=abc", "limit=100", "severity=debug"]:
            show(q, c.get(f"{P}/robots/r/logs?{q}"))
        show("unknown url", c.get("/nowhere"))
        show("bad id", c.delete(f"{P}/logs/abc"))
        show("method", c.put(f"{P}/summary"))
        show("method2", c.get(f"{P}/logs/1"))
    elif cmd == "cap":
        app2 = create_app({"TESTING": True, "MAX_LOGS_PER_ROBOT": 3})
        c2 = app2.test_client()
        for i in range(5):
            c2.post(f"{P}/robots/a/logs", json={"severity": ["info", "warn"][i % 2], "msg": f"m{i}"})
        c2.post(f"{P}/robots/b/logs", json={"severity": "error", "msg": "b0"})
        show("a", c2.get(f"{P}/robots/a/logs"))
        show("summary", c2.get(f"{P}/summary"))
        show("delete dropped", c2.delete(f"{P}/logs/1"))
        show("other app", c.get(f"{P}/summary"))
    elif cmd == "load":
        sev = ["info", "warn", "error"]
        for i in range(3000):
            c.post(f"{P}/robots/bot{i % 7}/logs", json={"severity": sev[i * 7 % 3], "msg": f"event {i}"})
        for i in range(1, 3001, 5):
            c.delete(f"{P}/logs/{i}")
        show("summary", c.get(f"{P}/summary"))
        r = c.get(f"{P}/robots/bot3/logs?severity=error&limit=3")
        show("bot3 errors", r)
```

## Tests
=== sample
basic
---
add1: 201 {"id": 1, "msg": "boot ok", "robot": "rover", "severity": "info"}
add2: 201 {"id": 2, "msg": "wheel slip", "robot": "rover", "severity": "warn"}
add3: 201 {"id": 3, "msg": "joint 3 overheat", "robot": "arm", "severity": "error"}
add4: 201 {"id": 4, "msg": "lidar timeout", "robot": "rover", "severity": "error"}
rover: 200 [{"id": 4, "msg": "lidar timeout", "robot": "rover", "severity": "error"}, {"id": 2, "msg": "wheel slip", "robot": "rover", "severity": "warn"}, {"id": 1, "msg": "boot ok", "robot": "rover", "severity": "info"}]
rover warn: 200 [{"id": 2, "msg": "wheel slip", "robot": "rover", "severity": "warn"}]
rover limit: 200 [{"id": 4, "msg": "lidar timeout", "robot": "rover", "severity": "error"}, {"id": 2, "msg": "wheel slip", "robot": "rover", "severity": "warn"}]
ghost: 200 []
summary: 200 {"arm": {"error": 1, "info": 0, "warn": 0}, "rover": {"error": 1, "info": 1, "warn": 1}}
delete: 204 <empty>
delete again: 404 {"error": "not found"}
summary: 200 {"arm": {"error": 1, "info": 0, "warn": 0}, "rover": {"error": 1, "info": 1, "warn": 0}}
=== hidden
errors
---
no json: 400 {"error": "body must be a JSON object"}
list body: 400 {"error": "body must be a JSON object"}
bad sev: 400 {"error": "invalid severity"}
no msg: 400 {"error": "invalid msg"}
blank msg: 400 {"error": "invalid msg"}
num msg: 400 {"error": "invalid msg"}
long msg: 400 {"error": "invalid msg"}
max msg: 200 [{"id": 1, "msg": "yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy", "robot": "r", "severity": "info"}]
limit=0: 400 {"error": "invalid limit"}
limit=101: 400 {"error": "invalid limit"}
limit=abc: 400 {"error": "invalid limit"}
limit=100: 200 [{"id": 1, "msg": "yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy", "robot": "r", "severity": "info"}]
severity=debug: 400 {"error": "invalid severity"}
unknown url: 404 {"error": "not found"}
bad id: 404 {"error": "not found"}
method: 405 {"error": "method not allowed"}
method2: 405 {"error": "method not allowed"}
=== hidden
cap
---
a: 200 [{"id": 5, "msg": "m4", "robot": "a", "severity": "info"}, {"id": 4, "msg": "m3", "robot": "a", "severity": "warn"}, {"id": 3, "msg": "m2", "robot": "a", "severity": "info"}]
summary: 200 {"a": {"error": 0, "info": 2, "warn": 1}, "b": {"error": 1, "info": 0, "warn": 0}}
delete dropped: 404 {"error": "not found"}
other app: 200 {}
=== hidden
load
---
summary: 200 {"bot0": {"error": 114, "info": 114, "warn": 115}, "bot1": {"error": 114, "info": 114, "warn": 115}, "bot2": {"error": 115, "info": 114, "warn": 115}, "bot3": {"error": 115, "info": 114, "warn": 114}, "bot4": {"error": 115, "info": 114, "warn": 114}, "bot5": {"error": 114, "info": 115, "warn": 113}, "bot6": {"error": 113, "info": 115, "warn": 114}}
bot3 errors: 200 [{"id": 3000, "msg": "event 2999", "robot": "bot3", "severity": "error"}, {"id": 2979, "msg": "event 2978", "robot": "bot3", "severity": "error"}, {"id": 2958, "msg": "event 2957", "robot": "bot3", "severity": "error"}]

## Hints
- `bp = Blueprint("maint", __name__)`, then `app.register_blueprint(bp, url_prefix="/api/v1")`. Build the blueprint **inside** `create_app` (or keep the state in `app.extensions`), so apps don't share data.
- `request.get_json(silent=True)` returns None instead of raising on non-JSON bodies.
- App-wide JSON errors: `@app.errorhandler(404)` and `@app.errorhandler(405)` return `jsonify(error=...)` with the status. Use `abort(404)` in views.
- A per-robot `collections.deque(maxlen=cap)` drops the oldest entries automatically. Keep an id → (robot, entry) index for deletes, and remember to remove dropped entries from it.
- `return "", 204` for an empty response.

## Solution
```python
from collections import deque

from flask import Blueprint, Flask, abort, current_app, jsonify, request

SEVERITIES = ("info", "warn", "error")


class LogStore:
    def __init__(self, cap):
        self.cap = cap
        self.by_robot = {}
        self.by_id = {}
        self.next_id = 1

    def add(self, robot, severity, msg):
        entry = {"id": self.next_id, "robot": robot, "severity": severity, "msg": msg}
        self.next_id += 1
        q = self.by_robot.setdefault(robot, deque())
        q.append(entry)
        self.by_id[entry["id"]] = entry
        while len(q) > self.cap:
            dropped = q.popleft()
            del self.by_id[dropped["id"]]
        return entry

    def delete(self, log_id):
        entry = self.by_id.pop(log_id, None)
        if entry is None:
            return False
        self.by_robot[entry["robot"]].remove(entry)
        return True


def bad_request(message):
    return jsonify(error=message), 400


def make_blueprint():
    bp = Blueprint("maint", __name__)

    def store():
        return current_app.extensions["logstore"]

    @bp.post("/robots/<name>/logs")
    def add_log(name):
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return bad_request("body must be a JSON object")
        if data.get("severity") not in SEVERITIES:
            return bad_request("invalid severity")
        msg = data.get("msg")
        if not isinstance(msg, str) or not msg.strip() or len(msg.strip()) > 200:
            return bad_request("invalid msg")
        return jsonify(store().add(name, data["severity"], msg.strip())), 201

    @bp.get("/robots/<name>/logs")
    def list_logs(name):
        severity = request.args.get("severity")
        if severity is not None and severity not in SEVERITIES:
            return bad_request("invalid severity")
        try:
            limit = int(request.args.get("limit", 50))
        except ValueError:
            return bad_request("invalid limit")
        if not 1 <= limit <= 100:
            return bad_request("invalid limit")
        entries = [e for e in reversed(store().by_robot.get(name, ())) if severity in (None, e["severity"])]
        return jsonify(entries[:limit])

    @bp.get("/summary")
    def summary():
        out = {}
        for robot, q in store().by_robot.items():
            if q:
                counts = dict.fromkeys(SEVERITIES, 0)
                for e in q:
                    counts[e["severity"]] += 1
                out[robot] = counts
        return jsonify(out)

    @bp.delete("/logs/<int:log_id>")
    def delete_log(log_id):
        if not store().delete(log_id):
            abort(404)
        return "", 204

    return bp


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(MAX_LOGS_PER_ROBOT=1000)
    if config:
        app.config.update(config)
    app.extensions["logstore"] = LogStore(app.config["MAX_LOGS_PER_ROBOT"])
    app.register_blueprint(make_blueprint(), url_prefix="/api/v1")

    @app.errorhandler(404)
    def not_found(_):
        return jsonify(error="not found"), 404

    @app.errorhandler(405)
    def method_not_allowed(_):
        return jsonify(error="method not allowed"), 405

    return app
```

- **The application factory** creates a fresh `LogStore` per app in `app.extensions`, and views reach it through `current_app`. Two apps (or two tests) never share state.
- **Blueprints** group the API routes under one versioned prefix (`/api/v1`). A `/api/v2` blueprint could later live alongside it.
- **App-level error handlers** make every 404 and 405 JSON, including Flask's own routing errors for unknown URLs and non-integer ids, so API clients never receive an HTML error page.
- **Validation before mutation**: each check returns a precise 400 message, and nothing is stored unless the request is fully valid.
- **Bounded storage**: a per-robot deque with eviction keeps memory bounded. The id index is updated on eviction, so deleting a dropped entry correctly returns 404.
