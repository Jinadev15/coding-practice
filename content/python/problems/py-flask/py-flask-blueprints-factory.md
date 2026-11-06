---
id: py-flask-blueprints-factory
title: Blueprints and the Application Factory
difficulty: Medium
order: 3
tags: Flask, blueprints, app factory, config, before_request, after_request, url_for, blueprint error handlers
time_limit: 5
---
## Statement
Structure a Flask app the way real projects do: an **application factory** plus **blueprints**.

```python
DEFAULTS = {"GREETING": "hello", "ENV_NAME": "dev", "ADMIN_TOKEN": None, "USERS": {}}
def create_app(config: dict | None = None) -> Flask: ...
```

**Config:** load `DEFAULTS` with `app.config.from_mapping`, then apply `config` on top. Two apps must never share state or config.

**Blueprint `public`** (no prefix):
- `GET /` → text `<GREETING> from <ENV_NAME>`.
- `GET /visits` → JSON `{"visits": n}`, where `n` counts the requests handled by **this blueprint** in this app so far, including the current one. Count them in a **blueprint-level** `before_request`.

**Blueprint `admin`** (prefix `/admin`):
- A blueprint-level `before_request` requires the header `X-Admin-Token` to equal `ADMIN_TOKEN`. If it doesn't, or `ADMIN_TOKEN` is `None`, respond **403** `{"error": "forbidden"}`.
- `GET /admin/` → `{"dashboard": true, "links": [url_for("admin.user", uid=1), url_for("public.index")]}`.
- `GET /admin/users/<int:uid>` → `{"id": uid, "name": USERS[uid]}`. An unknown uid calls `abort(404)`, and a **blueprint error handler** for 404 turns it into `{"error": "no such user"}` (status 404).

**Blueprint `api`**: **one** `Blueprint` object registered **twice**, at `/api/v1` with `name="v1"` and at `/api/v2` with `name="v2"`.
- `GET <prefix>/status` → `{"version": request.blueprint, "self": url_for(".status")}`. The leading dot resolves inside the current blueprint, so v1 links to v1.

**App-wide:** an `after_request` hook adds the header `X-Env: <ENV_NAME>` to **every** response, errors included.

The driver also prints the registered blueprint names and every URL rule with its endpoint, so the endpoint names (`public.index`, `public.visits`, `admin.dashboard`, `admin.user`, `v1.status`, `v2.status`) must match exactly.

## Starter
```python
from flask import Blueprint, Flask, jsonify, request, url_for

DEFAULTS = {"GREETING": "hello", "ENV_NAME": "dev", "ADMIN_TOKEN": None, "USERS": {}}


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(DEFAULTS)

    @app.get("/")
    def index():
        return f"{app.config['GREETING']} from {app.config['ENV_NAME']}"

    return app
```

## Driver
```python
import json
import sys

def show(label, r):
    body = r.get_json(silent=True)
    body = json.dumps(body, sort_keys=True) if body is not None else r.get_data(as_text=True)
    if r.status_code == 404 and r.mimetype == "text/html":
        body = "<flask default 404>"
    print(f"{label}: {r.status_code} X-Env={r.headers.get('X-Env')} {body}")

def run(g):
    if g == "structure":
        app = create_app()
        print("blueprints", sorted(app.blueprints))
        print("rules", sorted((r.rule, r.endpoint) for r in app.url_map.iter_rules() if r.endpoint != "static"))
        c = app.test_client()
        show("index", c.get("/"))
        show("v1", c.get("/api/v1/status"))
        show("v2", c.get("/api/v2/status"))
        show("v3", c.get("/api/v3/status"))
    elif g == "config":
        a = create_app({"GREETING": "hi", "ENV_NAME": "prod"})
        b = create_app()
        show("a", a.test_client().get("/"))
        show("b", b.test_client().get("/"))
        print("defaults untouched", DEFAULTS["GREETING"], b.config["ENV_NAME"], a.config["ADMIN_TOKEN"])
    elif g == "visits":
        a, b = create_app().test_client(), create_app().test_client()
        a.get("/"); a.get("/")
        a.get("/api/v1/status"); a.get("/missing")
        show("a visits", a.get("/visits"))
        show("a visits again", a.get("/visits"))
        show("b visits", b.get("/visits"))
    elif g == "admin":
        app = create_app({"ADMIN_TOKEN": "s3cret", "USERS": {1: "ada", 7: "linus"}, "ENV_NAME": "stage"})
        c = app.test_client()
        H = {"X-Admin-Token": "s3cret"}
        show("no token", c.get("/admin/"))
        show("wrong token", c.get("/admin/", headers={"X-Admin-Token": "guess"}))
        show("dashboard", c.get("/admin/", headers=H))
        show("user 7", c.get("/admin/users/7", headers=H))
        show("user 2", c.get("/admin/users/2", headers=H))
        show("user 2 no token", c.get("/admin/users/2"))
        show("unrouted", c.get("/admin/nope", headers=H))
        show("public 404", c.get("/nope"))
        show("visits", c.get("/visits"))
        open_app = create_app().test_client()
        show("no ADMIN_TOKEN set", open_app.get("/admin/", headers={"X-Admin-Token": "None"}))

for g in sys.stdin.read().split():
    print("#", g)
    run(g)
```

## Tests
=== sample
structure
---
# structure
blueprints ['admin', 'public', 'v1', 'v2']
rules [('/', 'public.index'), ('/admin/', 'admin.dashboard'), ('/admin/users/<int:uid>', 'admin.user'), ('/api/v1/status', 'v1.status'), ('/api/v2/status', 'v2.status'), ('/visits', 'public.visits')]
index: 200 X-Env=dev hello from dev
v1: 200 X-Env=dev {"self": "/api/v1/status", "version": "v1"}
v2: 200 X-Env=dev {"self": "/api/v2/status", "version": "v2"}
v3: 404 X-Env=dev <flask default 404>
=== hidden
config
---
# config
a: 200 X-Env=prod hi from prod
b: 200 X-Env=dev hello from dev
defaults untouched hello dev None
=== hidden
visits
---
# visits
a visits: 200 X-Env=dev {"visits": 3}
a visits again: 200 X-Env=dev {"visits": 4}
b visits: 200 X-Env=dev {"visits": 1}
=== hidden
admin
---
# admin
no token: 403 X-Env=stage {"error": "forbidden"}
wrong token: 403 X-Env=stage {"error": "forbidden"}
dashboard: 200 X-Env=stage {"dashboard": true, "links": ["/admin/users/1", "/"]}
user 7: 200 X-Env=stage {"id": 7, "name": "linus"}
user 2: 404 X-Env=stage {"error": "no such user"}
user 2 no token: 403 X-Env=stage {"error": "forbidden"}
unrouted: 404 X-Env=stage <flask default 404>
public 404: 404 X-Env=stage <flask default 404>
visits: 200 X-Env=stage {"visits": 1}
no ADMIN_TOKEN set: 403 X-Env=dev {"error": "forbidden"}

## Hints
- Create blueprints inside functions called from `create_app`, so each app gets fresh blueprint state. Read config through `current_app.config`.
- `@bp.before_request` returning a response short-circuits the view (use it for the 403). `@bp.errorhandler(404)` handles `abort(404)` from that blueprint's views.
- `app.register_blueprint(api, url_prefix="/api/v1", name="v1")`, then the same for v2. Inside a view, `url_for(".status")` targets the current blueprint.

## Solution
**The factory** builds a new app on every call: config first, then blueprints, then app-wide hooks. Nothing lives at module level, so tests and multiple deployments (dev, staging, prod configs) can't interfere. Building each blueprint inside a `make_*()` function also gives each app its own blueprint state, such as the visit counter.

**Blueprints** group routes, hooks and error handlers under a name and an optional URL prefix. Endpoints become `name.function` (`admin.user`).
- A blueprint's `before_request` runs only for requests routed to **that** blueprint. That's why the visit counter ignores `/api/...` and unrouted 404s, and why `/admin/nope` gets a plain 404 rather than 403: no admin route matched, so admin's hook never ran.
- A blueprint's `errorhandler(404)` catches `abort(404)` raised **inside** its views. Routing 404s happen before any blueprint is chosen, so they fall through to the app.
- Registering the same blueprint twice with different `name=`/`url_prefix=` mounts one implementation as two API versions. `request.blueprint` tells them apart, and `url_for(".status")` stays inside the current one.

**`current_app`** is the proxy to whichever app is handling the request, so blueprint code never imports a global app object. `after_request` runs for every response, including error responses produced by handlers.

Complexity: O(1) per request.

```python
from flask import Blueprint, Flask, abort, current_app, request, url_for

DEFAULTS = {"GREETING": "hello", "ENV_NAME": "dev", "ADMIN_TOKEN": None, "USERS": {}}


def make_public():
    bp = Blueprint("public", __name__)
    counter = [0]

    @bp.before_request
    def count():
        counter[0] += 1

    @bp.get("/")
    def index():
        cfg = current_app.config
        return f"{cfg['GREETING']} from {cfg['ENV_NAME']}"

    @bp.get("/visits")
    def visits():
        return {"visits": counter[0]}

    return bp


def make_admin():
    bp = Blueprint("admin", __name__, url_prefix="/admin")

    @bp.before_request
    def require_token():
        token = current_app.config["ADMIN_TOKEN"]
        if token is None or request.headers.get("X-Admin-Token") != token:
            return {"error": "forbidden"}, 403

    @bp.errorhandler(404)
    def no_user(e):
        return {"error": "no such user"}, 404

    @bp.get("/")
    def dashboard():
        return {"dashboard": True, "links": [url_for("admin.user", uid=1), url_for("public.index")]}

    @bp.get("/users/<int:uid>")
    def user(uid):
        users = current_app.config["USERS"]
        if uid not in users:
            abort(404)
        return {"id": uid, "name": users[uid]}

    return bp


def make_api():
    bp = Blueprint("api", __name__)

    @bp.get("/status")
    def status():
        return {"version": request.blueprint, "self": url_for(".status")}

    return bp


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_mapping(DEFAULTS)
    if config:
        app.config.update(config)

    app.register_blueprint(make_public())
    app.register_blueprint(make_admin())
    api = make_api()
    app.register_blueprint(api, url_prefix="/api/v1", name="v1")
    app.register_blueprint(api, url_prefix="/api/v2", name="v2")

    @app.after_request
    def add_env(response):
        response.headers["X-Env"] = app.config["ENV_NAME"]
        return response

    return app
```
