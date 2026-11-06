# Flask in Depth

Flask is the classic Python **micro-framework**: a small core (routing, request/response objects, templates, sessions) and you choose everything else. It powers internal tools, admin panels, ML demo services and many production APIs, and its explicit design makes it the best framework for learning how web apps really work. This lesson covers routing and converters, the request and response objects, the application factory and config, blueprints, Jinja templates and autoescaping, sessions and flash messages, error handling, request hooks, and testing with `test_client`.

## 1. Why Flask, and what it is underneath

- **Small and explicit.** A Flask app is a Python object you build. Nothing is hidden in magic directories, so it's easy to reason about and to test.
- **WSGI.** Flask is a WSGI application: a callable `app(environ, start_response)`. A WSGI server (gunicorn, uWSGI, or werkzeug's dev server) parses HTTP from the socket, builds the `environ` dict, and calls your app. Flask sits on **Werkzeug** (request/response, routing, the dev server) and **Jinja2** (templates).
- **Synchronous by default.** Each request occupies a worker thread or process. Async views exist (`async def`), but Flask isn't an async framework like FastAPI. For many slow I/O-bound connections, an ASGI framework fits better.
- **When to choose it.** Server-rendered pages and small-to-medium JSON APIs where you want control. For typed JSON APIs with automatic validation and docs, FastAPI. For a full product with ORM, admin and auth built in, Django.

## 2. A first app

```python
from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello, Flask!"                      # str -> text/html response, status 200

@app.get("/add")
def add():
    a = request.args.get("a", type=int)         # None if missing OR not an int
    b = request.args.get("b", type=int)
    if a is None or b is None:
        return {"error": "a and b must be integers"}, 400   # dict -> JSON
    return {"sum": a + b}

client = app.test_client()
print(client.get("/add?a=2&b=40").get_json())   # {'sum': 42}
print(client.get("/add?a=x").status_code)       # 400
```

Run a real server with `flask --app module_name run --debug`. Never use debug mode in production: the interactive debugger allows code execution.

### What a view may return

| Return value | Becomes |
|---|---|
| `str` | `text/html` body |
| `dict` or `list` | JSON (`application/json`) |
| `(body, status)` | body with that status |
| `(body, status, headers)` | plus headers, e.g. `{"Location": "/todos/3"}` |
| a `Response` object | sent as is (`redirect(...)`, `make_response(...)`, `send_file(...)`) |

## 3. Routing and converters

```python
from flask import Flask, request

app = Flask(__name__)

@app.get("/items/<int:item_id>")             # int converter: /items/abc -> 404 before your code runs
def item(item_id):
    return {"id": item_id}

@app.route("/echo", methods=["GET", "POST"])  # other methods -> automatic 405 with an Allow header
def echo():
    if request.method == "GET":
        return "send me a POST"
    return {"length": len(request.get_data())}

@app.get("/docs/")                            # trailing slash: /docs redirects (308) to /docs/
def docs():
    return "docs index"

c = app.test_client()
print(c.get("/items/abc").status_code, c.put("/echo").status_code, c.get("/docs").status_code)   # 404 405 308
```

Converters: `string` (default, no slashes), `int`, `float`, `path` (allows slashes), `uuid`. The endpoint name is the function name, and **`url_for`** builds URLs from it, so templates and redirects never hard-code paths:

```python
from flask import url_for

with app.test_request_context():               # url_for needs an app (here: the app above)
    print(url_for("item", item_id=7))          # /items/7
    print(url_for("item", item_id=7, v=2))     # /items/7?v=2  (unknown args become the query string)
```

## 4. The request and response objects

`request` is a **context-local proxy**: it looks global, but each request (each thread) sees its own object.

| Attribute | Content |
|---|---|
| `request.method`, `request.path`, `request.url` | basics |
| `request.args` | query string (`MultiDict`: `get`, `getlist`) |
| `request.form` | `application/x-www-form-urlencoded` or multipart form fields |
| `request.files` | uploaded files (`FileStorage`, `.save(path)`) |
| `request.get_json(silent=True)` | parsed JSON or `None`; `request.is_json` checks the content type |
| `request.headers`, `request.cookies` | case-insensitive headers, cookie dict |
| `request.get_data()` | raw body bytes |

> [!WARNING]
> `request.args.get("limit", 10, type=int)` returns the **default** when the conversion fails, so `?limit=ten` silently becomes 10. If invalid input must be rejected, convert the raw string yourself.

### Dry run: the life of one request

`POST /todos` with JSON `{"title": "x"}`:

| Step | Who | What happens |
|---|---|---|
| 1 | WSGI server | parses HTTP, builds `environ`, calls `app(environ, start_response)` |
| 2 | Flask | pushes the **app context** (`current_app`, `g`) and **request context** (`request`, `session`) |
| 3 | Werkzeug routing | matches `POST /todos` → endpoint `create`; a miss raises `NotFound`/`MethodNotAllowed` |
| 4 | hooks | `before_request` functions run (app-wide, then the blueprint's); returning a response stops here |
| 5 | view | `create()` runs and returns `(dict, 201, headers)` |
| 6 | Flask | converts the return value into a `Response`; on an exception, finds an error handler |
| 7 | hooks | `after_request` functions modify the response (add headers); the session is saved into a cookie |
| 8 | teardown | `teardown_request`/`teardown_appcontext` run even after errors (close DB connections) |
| 9 | WSGI server | writes status, headers and body to the socket |

## 5. The application factory and config

A module-level `app = Flask(__name__)` is fine for a demo. Real projects use a **factory**, a function that builds and returns a configured app:

```python
from flask import Flask

DEFAULTS = {"GREETING": "hello", "ENV_NAME": "dev", "MAX_CONTENT_LENGTH": 1024 * 1024}

def create_app(config=None):
    app = Flask(__name__)
    app.config.from_mapping(DEFAULTS)
    if config:
        app.config.update(config)          # test or deployment overrides
    # app.config.from_prefixed_env()       # reads FLASK_* environment variables (12-factor)

    @app.get("/")
    def index():
        return f"{app.config['GREETING']} from {app.config['ENV_NAME']}"

    return app

prod = create_app({"ENV_NAME": "prod"})
test = create_app({"ENV_NAME": "test"})
print(prod.test_client().get("/").text, "|", test.test_client().get("/").text)
```

Why: every test gets a fresh, isolated app; one code base runs with dev, test and prod configs; extensions (`db.init_app(app)`) bind late; no circular imports. Keep secrets such as `SECRET_KEY` out of the code and load them from the environment.

## 6. Blueprints

A **blueprint** is a group of routes, hooks, templates and error handlers that you register on an app, optionally under a URL prefix:

```python
from flask import Blueprint, Flask, abort, current_app, request, url_for

admin = Blueprint("admin", __name__, url_prefix="/admin")

@admin.before_request                      # runs only for requests routed to THIS blueprint
def require_token():
    if request.headers.get("X-Admin-Token") != current_app.config["ADMIN_TOKEN"]:
        return {"error": "forbidden"}, 403

@admin.errorhandler(404)                   # catches abort(404) raised in admin views
def admin_404(e):
    return {"error": "no such user"}, 404

@admin.get("/users/<int:uid>")
def user(uid):
    users = current_app.config["USERS"]
    if uid not in users:
        abort(404)
    return {"id": uid, "name": users[uid], "self": url_for("admin.user", uid=uid)}

app = Flask(__name__)
app.config.update(ADMIN_TOKEN="t", USERS={1: "ada"})
app.register_blueprint(admin)
c = app.test_client()
print(c.get("/admin/users/1", headers={"X-Admin-Token": "t"}).get_json())
print(c.get("/admin/users/2", headers={"X-Admin-Token": "t"}).get_json())
print(c.get("/admin/users/1").status_code)
```

- Endpoints are namespaced: `admin.user`. Inside a blueprint, `url_for(".user", ...)` means "in the current blueprint".
- One blueprint object can be registered **twice** with different `name=` and `url_prefix=` (for example `/api/v1` and `/api/v2`).
- A blueprint's 404 handler sees only `abort(404)` from its own views. A URL that matches no route at all never reaches a blueprint, so the app-level handler deals with it.
- Use `current_app`, never an imported global app, inside blueprint code: the blueprint may be registered on many apps.

## 7. Templates with Jinja2

```python
import jinja2
from flask import Flask, render_template

TEMPLATES = {
    "base.html": "<title>{% block title %}{% endblock %} | Shop</title>\n"
                 "<main>{% block content %}{% endblock %}</main>\n"
                 "<footer>{% block footer %}Shop{% endblock %}</footer>",
    "list.html": "{% extends 'base.html' %}"
                 "{% block title %}Products{% endblock %}"
                 "{% block content %}<ul>{% for p in products %}"
                 "<li>{{ loop.index }}. {{ p.name }} - {{ p.cents|money }}</li>"
                 "{% else %}<li>none</li>{% endfor %}</ul>{% endblock %}",
}

app = Flask(__name__)
app.jinja_loader = jinja2.DictLoader(TEMPLATES)      # normally: files in templates/

@app.template_filter("money")
def money(cents):
    return f"${cents // 100:,}.{cents % 100:02d}"

@app.get("/")
def products():
    return render_template("list.html", products=[{"name": "Tom & Jerry", "cents": 123456}])

print(app.test_client().get("/").text)
```

- **Inheritance**: the base declares `{% block %}`s, and children `{% extends %}` and override some. A block a child doesn't override keeps the base's default.
- **Expressions and statements**: `{{ value|filter }}`, `{% if %}`, `{% for %}…{% else %}…{% endfor %}` (the `else` runs for an empty sequence), `loop.index`, macros (`{% macro row(p) %}`) for reusable fragments.
- **Autoescaping** is on for `.html` templates: `{{ p.name }}` renders `Tom &amp; Jerry`, and `<script>` becomes `&lt;script&gt;`. This is your main defence against **XSS**. `|safe` (or `Markup(...)`) disables it, so use it only for HTML you trust, never for user input.
- Templates should *present* data. Compute in the view, format with filters.

## 8. Sessions and flash messages

Flask's default `session` is a **signed cookie**: the dict is serialised, signed with `SECRET_KEY`, and stored in the browser. The user can read it (base64) but can't modify it without invalidating the signature.

```python
from flask import Flask, flash, get_flashed_messages, redirect, session

app = Flask(__name__)
app.config.update(SECRET_KEY="dev-only", SESSION_COOKIE_SAMESITE="Lax", SESSION_COOKIE_HTTPONLY=True)

@app.post("/login/<name>")
def login(name):
    session.clear()                          # fresh session on login
    session["user"] = name
    flash(f"Welcome, {name}!", "success")    # stored in the session until read once
    return redirect("/")                     # Post/Redirect/Get

@app.post("/cart/<item>")
def add(item):
    cart = session.setdefault("cart", {})
    cart[item] = cart.get(item, 0) + 1
    session.modified = True                  # in-place change: tell Flask to re-save
    return cart

@app.get("/")
def home():
    msgs = [f"{c}: {m}" for c, m in get_flashed_messages(with_categories=True)]
    return "\n".join(msgs + [f"user: {session.get('user', 'anonymous')}"])

c = app.test_client()
c.post("/login/ada"); c.post("/cart/pen"); c.post("/cart/pen")
print(c.get("/").text)                       # success: Welcome, ada! / user: ada
print(c.get("/").text)                       # the flash is gone: user: ada
```

- **Never store secrets** in a cookie session. Store an id and look up the rest server-side if needed (server-side sessions in Redis or a DB give you revocation).
- **`session.modified = True`** after mutating nested objects, or the change isn't saved.
- **Open redirects**: `redirect(request.args["next"])` lets attackers bounce users from your login page to `//evil.example`. Accept only relative paths that start with a single `/`.
- **Cookie flags**: `HttpOnly` (no JS access), `Secure` (HTTPS only), `SameSite=Lax` (not sent on cross-site POSTs, which blocks most CSRF).

## 9. Error handling

```python
from flask import Flask, abort
from werkzeug.exceptions import HTTPException

class ApiError(Exception):
    def __init__(self, status, code, message):
        super().__init__(message)
        self.status, self.code, self.message = status, code, message

app = Flask(__name__)

@app.errorhandler(ApiError)
def api_error(e):
    return {"error": {"code": e.code, "message": e.message}}, e.status

@app.errorhandler(HTTPException)              # 404, 405, 413, abort(...) ...
def http_error(e):
    resp = e.get_response()                   # keeps headers such as Allow on a 405
    resp.set_data(app.json.dumps({"error": {"code": e.name.lower().replace(" ", "_"), "message": e.description}}))
    resp.mimetype = "application/json"
    return resp

@app.errorhandler(Exception)                  # real bugs: log the traceback, hide the details
def crash(e):
    app.logger.exception("unhandled")
    return {"error": {"code": "internal_error", "message": "internal server error"}}, 500

@app.get("/orders/<int:oid>")
def order(oid):
    raise ApiError(404, "order_not_found", f"order {oid} does not exist")

c = app.test_client()
print(c.get("/orders/3").get_json())
print(c.delete("/orders/3").status_code, c.delete("/orders/3").headers["Allow"])
```

Flask picks the **most specific** handler along the exception's class hierarchy. `abort(404)` raises `NotFound`. With `TESTING = True` (or `PROPAGATE_EXCEPTIONS`), unhandled exceptions are re-raised into the test instead of becoming 500s. That's handy in unit tests, but it skips your 500 handler.

## 10. Hooks, `g` and teardown

| Hook | Runs | Typical use |
|---|---|---|
| `before_request` | before the view; a returned response short-circuits | auth checks, timing start, load the user into `g` |
| `after_request(resp)` | after the view, on success *and* handled errors | security headers, request ids |
| `teardown_request(exc)` | always, even after an exception | close DB sessions |
| `context_processor` | at template render | inject variables into every template |

`g` is a per-request scratch namespace (`g.user`, `g.db`). It disappears after the request.

## 11. Testing

```python
def test_todo_flow():
    app = create_app({"TESTING": True})      # the factory gives each test a fresh app
    c = app.test_client()
    r = c.post("/todos", json={"title": "x"})
    assert r.status_code == 201 and r.headers["Location"] == "/todos/1"
```

- `test_client()` sends requests through the full WSGI stack with no network: `get`, `post(json=..., data=..., headers=...)`, cookies are kept between calls, and `follow_redirects=True` follows redirects.
- `app.test_request_context("/path")` gives you a request context for testing helpers such as `url_for`.
- With pytest, put `app` and `client` in fixtures.

## 12. Complexity and performance

Routing is a precompiled set of regular expressions, effectively O(number of rules) in the worst case but fast in practice. Each request costs O(body size) to parse and O(rendered size) to template. Throughput comes from **workers**: gunicorn with N processes × M threads handles N·M requests at once, so a slow database call blocks one worker, not the server. The cookie session is re-serialised and re-signed on every modified response, so keep it small (cookies are limited to about 4 KB).

## 13. Pattern recognition

| Requirement | Flask tool |
|---|---|
| different configs for dev/test/prod, isolated tests | application factory + `app.config` |
| group admin routes with a shared auth check | blueprint + blueprint `before_request` |
| two API versions sharing code | one blueprint registered twice with `name=` |
| render user content in HTML safely | Jinja autoescape; `\|safe` only for trusted HTML |
| one-time "Saved!" message after a form POST | `flash` + redirect (Post/Redirect/Get) |
| consistent JSON errors everywhere | `errorhandler(HTTPException)` + custom exception + `Exception` fallback |
| header on every response | `after_request` |

## 14. Common mistakes

- **Module-level state** (`todos = []` at the top of the file): tests leak into each other. Keep state inside the factory or in a database.
- **`app.run(debug=True)` in production**: remote code execution through the debugger.
- **Using `|safe` on user input**, or building HTML with f-strings: XSS.
- **Hard-coded `SECRET_KEY`** committed to git: anyone can forge sessions.
- **Mutating `session["cart"]` without `session.modified = True`.**
- **Returning `{"error": ...}` with status 200.**
- **Trusting `request.args.get(..., type=int)` with a default** to reject bad input.
- **Importing the global `app` inside blueprints** (circular imports, and it breaks factories). Use `current_app`.
- **Redirecting to an unchecked `next` parameter** (open redirect).

## 15. Interview questions

> [!INTERVIEW] "What are the application and request contexts in Flask?"
> Flask keeps per-request state in context-local proxies so views can use `request`, `session`, `g` and `current_app` without passing them around. When a request arrives, Flask pushes an application context (`current_app`, `g`) and a request context (`request`, `session`). They're bound to the current thread or coroutine, so concurrent requests don't see each other's data, and they're popped after teardown. Outside a request, for example in a CLI script, you push one yourself with `app.app_context()`.

> [!INTERVIEW] "Why use an application factory?"
> It builds the app on demand with a given config, so tests get isolated apps, the same code runs in several environments, extensions are initialised with `init_app` without circular imports, and you can even run several apps in one process.

> [!EXAM] Explain how Flask's default session works and its security limits.
> The session dict is serialised to JSON, signed with an HMAC keyed by `SECRET_KEY` (itsdangerous), and stored in a cookie. On each request, Flask verifies the signature and loads the dict. A modified or foreign-key cookie fails verification and yields an empty session. Limits: the contents are readable by the client (don't store secrets), the size is about 4 KB, and the server can't revoke a single session before expiry unless it rotates the key. Server-side sessions solve the last two.

> [!INTERVIEW] "Flask vs FastAPI vs Django?"
> Flask: minimal WSGI core, explicit, great for small services and server-rendered pages, and you choose the ORM, validation and auth. FastAPI: ASGI, async, type-hint validation with Pydantic and automatic OpenAPI docs, ideal for JSON APIs. Django: batteries included (ORM, migrations, admin, auth, forms), ideal for full products with a relational data model.

## Check your understanding

1. What does a view return to send JSON with status 201 and a `Location` header?
2. Why does `/admin/nope` give 404 rather than 403 when the admin blueprint's `before_request` checks a token?
3. What does `{% for p in products %}…{% else %}…{% endfor %}` do when `products` is empty?
4. A user's cart changes inside `session["cart"]`, but the change disappears on the next request. Why?
5. Why does a 405 handler that returns a fresh dict lose information, and how do you keep it?
6. Why is `redirect(request.args.get("next"))` dangerous?

<details><summary>Answers</summary>

1. A tuple: `return todo, 201, {"Location": f"/todos/{todo['id']}"}`.
2. No route matched, so the request was never routed to the admin blueprint, and its hooks never ran. The routing `NotFound` goes to the app-level handling.
3. The `else` branch runs once. It's the "empty state" of the loop.
4. The session tracks assignments to its own keys, not mutations inside nested objects. Set `session.modified = True` (or reassign `session["cart"]`).
5. The `Allow` header (required on a 405) is part of werkzeug's response. Start from `e.get_response()` and replace only the body.
6. It's an open redirect: an attacker sends victims a link to your real login page that bounces them to `//evil.example` after logging in, which makes phishing convincing. Allow only relative paths starting with a single `/`.

</details>
