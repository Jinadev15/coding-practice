# Flask and Django Overview

Before FastAPI, Python web development meant **Flask** (a micro-framework: minimal core, pick your own extensions) or **Django** ("batteries included": ORM, admin site, auth, migrations, templates, forms). Both remain hugely popular: Django powers Instagram's backend and countless dashboards, and Flask runs many internal tools and ML demos. This lesson explains WSGI vs ASGI, Flask's application factory, blueprints, request context and testing, Django's architecture (MTV, ORM, migrations, admin), and how to choose a framework.

## 1. WSGI and ASGI

| | WSGI (PEP 3333) | ASGI |
|---|---|---|
| Model | synchronous: one request per worker thread or process | async: one event loop, many concurrent connections |
| Interface | `app(environ, start_response) -> iterable` | `async app(scope, receive, send)` |
| Supports | HTTP request/response | HTTP, WebSockets, long-lived connections |
| Servers | gunicorn, uWSGI, mod_wsgi | uvicorn, hypercorn, daphne |
| Frameworks | Flask, Django (classic) | FastAPI, Starlette, Django (async views), Quart |

## 2. Flask essentials

```python
from flask import Flask, jsonify, request, abort

def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(TESTING=False, MAX_ROBOTS=100)
    if config: app.config.update(config)
    app.extensions["robots"] = {}                      # app-scoped state (or a DB via an extension)

    @app.get("/robots/<int:rid>")
    def get_robot(rid: int):
        robot = app.extensions["robots"].get(rid)
        if robot is None:
            abort(404, description=f"robot {rid} not found")
        return jsonify(robot)

    @app.post("/robots")
    def add_robot():
        data = request.get_json(silent=True)
        if not isinstance(data, dict) or "name" not in data:
            return jsonify(error="name is required"), 400
        rid = len(app.extensions["robots"]) + 1
        app.extensions["robots"][rid] = {"id": rid, "name": data["name"]}
        return jsonify(app.extensions["robots"][rid]), 201

    @app.errorhandler(404)
    def not_found(e):
        return jsonify(error=e.description), 404
    return app
```

- `<int:rid>` is a URL converter (`string`, `int`, `float`, `path`, `uuid`).
- A view returns a `str`, a `dict` (auto-JSON), a `Response`, or a tuple `(body, status[, headers])`.
- `request` and `g` are **context locals**: they look global, but they're bound to the current request (thread- and greenlet-safe). `current_app` refers to the active application.

> [!KEY]
> Use an **application factory** (`create_app`) instead of a module-level `app`. It lets tests create isolated apps with test configuration, avoids import-time side effects, and lets one process host several configured apps.

**Blueprints** group related routes into modules, which are registered on the app with a URL prefix:

```python
from flask import Blueprint
bp = Blueprint("missions", __name__, url_prefix="/missions")
@bp.get("/")
def list_missions(): ...
# in create_app:  app.register_blueprint(bp)
```

**Testing:**

```python
def test_add_and_get():
    app = create_app({"TESTING": True})
    client = app.test_client()
    r = client.post("/robots", json={"name": "rover"})
    assert r.status_code == 201 and r.get_json()["id"] == 1
    assert client.get("/robots/1").get_json()["name"] == "rover"
    assert client.get("/robots/9").status_code == 404
```

Common extensions: Flask-SQLAlchemy (ORM), Flask-Migrate (Alembic migrations), Flask-Login, and Flask-WTF (forms plus CSRF).

## 3. Django's architecture

```text
mysite/                 project: settings.py, urls.py, asgi.py / wsgi.py
fleet/                  an "app" (a reusable component)
    models.py           ORM models -> database tables
    views.py            request handlers
    urls.py             URL routes
    admin.py            admin-site registration
    migrations/         generated schema migrations
    templates/fleet/    HTML templates
```

Django calls its pattern **MTV**: Model (data), Template (presentation), View (logic, the "controller" of MVC).

```python
# models.py
from django.db import models

class Robot(models.Model):
    name = models.CharField(max_length=50, unique=True)
    battery = models.FloatField(default=1.0)
    created = models.DateTimeField(auto_now_add=True)

class Mission(models.Model):
    robot = models.ForeignKey(Robot, on_delete=models.CASCADE, related_name="missions")
    status = models.CharField(max_length=20, choices=[("queued", "Queued"), ("done", "Done")])
```

```python
# querying with the ORM (lazy QuerySets compile to SQL)
low = Robot.objects.filter(battery__lt=0.2).order_by("name")
busy = Robot.objects.annotate(n=models.Count("missions")).filter(n__gt=3)
for m in Mission.objects.select_related("robot"):      # JOIN, avoiding N+1 queries
    print(m.robot.name, m.status)
```

```bash
python manage.py makemigrations && python manage.py migrate     # schema evolves under version control
python manage.py createsuperuser && python manage.py runserver  # the admin is at /admin
```

> [!DANGER]
> **The N+1 query problem**: looping over 100 missions and touching `m.robot` runs 101 queries. Use `select_related` (a JOIN, for foreign keys) or `prefetch_related` (a second batched query, for many-to-many and reverse relations). The same trap exists in SQLAlchemy (`joinedload`/`selectinload`).

Django also includes authentication and permissions, sessions, forms with validation, CSRF protection, caching, i18n, signals, and the **admin**: a full CRUD interface generated from models. That's a huge productivity win for internal robot-fleet dashboards. **Django REST Framework** (and the newer Django Ninja) add serializers and API views.

## 4. Choosing a framework

| Need | Pick |
|---|---|
| A JSON API, ML model serving, async I/O, auto docs | **FastAPI** |
| A small service or prototype, or full control over components | **Flask** |
| A data-heavy web application with users, admin, forms and migrations | **Django** |
| Real-time dashboards (WebSockets) | FastAPI/Starlette, or Django Channels |

Common to all: put business logic in plain Python modules, independent of the framework (see the clean architecture lesson), so the web layer stays thin and replaceable.

> [!EXAM]
> **Compare Flask and Django, and explain WSGI vs ASGI.**
> Flask is a micro-framework that provides routing, request/response handling, templating and context locals, and leaves the database, auth and forms to extensions of your choice. It suits small services and custom architectures. Django is batteries-included: ORM with migrations, auto-generated admin, authentication, forms, security middleware and a project/app structure, so it's suited to large, data-driven applications at the price of more convention. WSGI is the synchronous Python server interface (one request per worker), while ASGI is its asynchronous successor, supporting many concurrent connections and WebSockets on an event loop. Django supports both, Flask is WSGI, and FastAPI is ASGI-native.

## Worked example: the same endpoint in both frameworks

**Flask:** you choose every piece and wire it yourself.

```python
from flask import Flask, jsonify, request

def create_app():
    app = Flask(__name__)
    notes: list[str] = []

    @app.post("/notes")
    def add():
        text = (request.get_json(silent=True) or {}).get("text", "").strip()
        if not text:
            return jsonify(error="text required"), 400
        notes.append(text)
        return jsonify(id=len(notes), text=text), 201

    return app

client = create_app().test_client()
print(client.post("/notes", json={"text": "oil the joints"}).get_json())
print(client.post("/notes", json={}).status_code)
```

```output
{'id': 1, 'text': 'oil the joints'}
400
```

**Django:** "batteries included". The equivalent is spread over its conventional files:

```python
# notes/models.py
class Note(models.Model):
    text = models.CharField(max_length=200)

# notes/views.py
def add(request):
    data = json.loads(request.body or "{}")
    if not data.get("text"):
        return JsonResponse({"error": "text required"}, status=400)
    note = Note.objects.create(text=data["text"])          # ORM writes the SQL
    return JsonResponse({"id": note.id, "text": note.text}, status=201)

# notes/urls.py
urlpatterns = [path("notes", views.add)]
```

**Which to pick:**

- **Flask (or FastAPI)** suits small services and APIs where you want control.
- **Django** suits database-heavy sites that need an admin panel, authentication, migrations and forms out of the box.

## Common mistakes

- **Module-level `app = Flask(...)` with global state.** Use an application factory (`create_app`) so tests get a fresh app.
- **Running the dev server in production** (`app.run()`, `manage.py runserver`). Use gunicorn or uvicorn behind a proxy.
- **Disabling Django's CSRF protection** to "make POST work". Send the token properly instead.

## Check your understanding

1. What do WSGI and ASGI define?
2. Why is a Django QuerySet called *lazy*?

<details><summary>Answers</summary>

1. The interface between a Python web app and the server. WSGI is synchronous; ASGI also supports async, websockets and long-lived connections.
2. Building it (`.filter()`, `.order_by()`) runs no SQL. The query executes only when you iterate, slice or count it.

</details>
