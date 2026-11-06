---
id: py-flask-routes-query
title: Hello Routes, Converters and Query Parameters
difficulty: Easy
order: 1
tags: Flask, routing, URL converters, request.args, methods, 405, url_for, escaping
time_limit: 5
---
## Statement
Write `create_app() -> Flask` with these routes. The judge calls them through `app.test_client()`.

| Route | Behaviour |
|---|---|
| `GET /` | text `Hello, Flask!` |
| `GET /hello/<name>` | text `Hello, <name>!` with `name` **HTML-escaped** (`markupsafe.escape`), so `/hello/<b>` gives `Hello, &lt;b&gt;!` |
| `GET /add?a=&b=` | JSON `{"sum": a + b}`. Both must be integers (use `request.args.get(..., type=int)`). Otherwise status **400** with JSON `{"error": "a and b must be integers"}` |
| `GET /items/<int:item_id>` | JSON `{"id": item_id}`. A non-integer id must give Flask's own **404** (use the `int` converter) |
| `GET /search?tag=...&tag=...&limit=` | JSON `{"tags": [all tag values in order], "limit": limit}`. `limit` defaults to 10 and must be an integer in 1..50, otherwise **400** `{"error": "limit must be 1..50"}` (so `?limit=ten` is a 400 too) |
| `GET, POST /echo` | GET: text `send me a POST`. POST: JSON `{"method": "POST", "length": <number of body bytes>, "type": <request mimetype or null>}`. Any other method must give Flask's automatic **405** with an `Allow` header |
| `GET /docs/` | text `docs index`. Because the rule ends in `/`, Flask redirects `/docs` to `/docs/` (308) automatically |
| `GET /where` | text: the result of `url_for("hello", name="a b")`. The view function for `/hello/<name>` must be named `hello` |

Return plain strings for text responses (Flask sends them as `text/html`) and dicts for JSON.

The driver prints, for every request: method, path, status, mimetype, the body, and the `Location`/`Allow` headers when present.

## Starter
```python
from flask import Flask, request


def create_app():
    app = Flask(__name__)

    @app.route("/")
    def index():
        return "Hello, Flask!"

    @app.route("/hello/<name>")
    def hello(name):
        return f"Hello, {name}!"

    # TODO: /add, /items/<int:item_id>, /search, /echo, /docs/, /where
    return app
```

## Driver
```python
import sys

app = create_app()
c = app.test_client()

def show(method, path, **kw):
    r = c.open(path, method=method, **kw)
    hv = {"Location": r.headers.get("Location"), "Allow": ", ".join(sorted(r.headers.get("Allow", "").split(", ")))}
    extra = "".join(f" [{h}: {hv[h]}]" for h in ("Location", "Allow") if h in r.headers)
    body = r.get_data(as_text=True).strip().replace("\n", " ")
    if r.status_code in (404, 405) and r.mimetype == "text/html":
        body = "<flask default page>"
    if 300 <= r.status_code < 400:
        body = "<redirect page>"
    print(f"{method} {path} -> {r.status_code} {r.mimetype} {body}{extra}")

GROUPS = {
    "basics": [("GET", "/"), ("GET", "/hello/ada"), ("GET", "/hello/<script>x"), ("GET", "/hello/a%20b"), ("GET", "/where"),
               ("GET", "/docs/"), ("GET", "/docs")],
    "add": [("GET", "/add?a=2&b=40"), ("GET", "/add?a=-7&b=3"), ("GET", "/add?a=2"), ("GET", "/add?a=x&b=1"),
            ("GET", "/add?a=1.5&b=1"), ("GET", "/add")],
    "items": [("GET", "/items/7"), ("GET", "/items/0"), ("GET", "/items/abc"), ("GET", "/items/-1"), ("GET", "/nothing")],
    "search": [("GET", "/search"), ("GET", "/search?tag=a&tag=b%20c&tag=a"), ("GET", "/search?limit=50&tag=x"),
               ("GET", "/search?limit=0"), ("GET", "/search?limit=51"), ("GET", "/search?limit=ten"), ("GET", "/search?limit=1")],
    "echo": [("GET", "/echo"), ("POST", "/echo"), ("PUT", "/echo"), ("DELETE", "/")],
}
for g in sys.stdin.read().split():
    print("#", g)
    for m, p in GROUPS[g]:
        show(m, p)
    if g == "echo":
        r = c.post("/echo", json={"speed": 1.5})
        print("POST json ->", r.status_code, r.get_json())
        r = c.post("/echo", data="héllo", content_type="text/plain")
        print("POST text ->", r.status_code, r.get_json())
```

## Tests
=== sample
basics
---
# basics
GET / -> 200 text/html Hello, Flask!
GET /hello/ada -> 200 text/html Hello, ada!
GET /hello/<script>x -> 200 text/html Hello, &lt;script&gt;x!
GET /hello/a%20b -> 200 text/html Hello, a b!
GET /where -> 200 text/html /hello/a%20b
GET /docs/ -> 200 text/html docs index
GET /docs -> 308 text/html <redirect page> [Location: http://localhost/docs/]
=== hidden
add
---
# add
GET /add?a=2&b=40 -> 200 application/json {"sum":42}
GET /add?a=-7&b=3 -> 200 application/json {"sum":-4}
GET /add?a=2 -> 400 application/json {"error":"a and b must be integers"}
GET /add?a=x&b=1 -> 400 application/json {"error":"a and b must be integers"}
GET /add?a=1.5&b=1 -> 400 application/json {"error":"a and b must be integers"}
GET /add -> 400 application/json {"error":"a and b must be integers"}
=== hidden
items
---
# items
GET /items/7 -> 200 application/json {"id":7}
GET /items/0 -> 200 application/json {"id":0}
GET /items/abc -> 404 text/html <flask default page>
GET /items/-1 -> 404 text/html <flask default page>
GET /nothing -> 404 text/html <flask default page>
=== hidden
search
---
# search
GET /search -> 200 application/json {"limit":10,"tags":[]}
GET /search?tag=a&tag=b%20c&tag=a -> 200 application/json {"limit":10,"tags":["a","b c","a"]}
GET /search?limit=50&tag=x -> 200 application/json {"limit":50,"tags":["x"]}
GET /search?limit=0 -> 400 application/json {"error":"limit must be 1..50"}
GET /search?limit=51 -> 400 application/json {"error":"limit must be 1..50"}
GET /search?limit=ten -> 400 application/json {"error":"limit must be 1..50"}
GET /search?limit=1 -> 200 application/json {"limit":1,"tags":[]}
=== hidden
echo
---
# echo
GET /echo -> 200 text/html send me a POST
POST /echo -> 200 application/json {"length":0,"method":"POST","type":null}
PUT /echo -> 405 text/html <flask default page> [Allow: GET, HEAD, OPTIONS, POST]
DELETE / -> 405 text/html <flask default page> [Allow: GET, HEAD, OPTIONS]
POST json -> 200 {'length': 14, 'method': 'POST', 'type': 'application/json'}
POST text -> 200 {'length': 6, 'method': 'POST', 'type': 'text/plain'}

## Hints
- `request.args.get("a", type=int)` returns `None` when the value is missing *or* not an integer.
- `request.args.getlist("tag")` returns all repeated values. For `limit`, beware: `get("limit", 10, type=int)` returns the default 10 for `?limit=ten`. Convert the raw string yourself.
- Use `methods=["GET", "POST"]` on `/echo` and branch on `request.method`. Flask produces the 405 and the `/docs` redirect for you.

## Solution
**Routing.** `@app.route(rule, methods=[...])` maps a URL rule to a view function. `@app.get` and `@app.post` are shortcuts. The endpoint name defaults to the function name, which is what `url_for("hello", name="a b")` looks up. It builds `/hello/a%20b`, with the space URL-encoded, so you never hard-code URLs.

**Converters** (`<int:item_id>`, `<path:p>`, `<uuid:u>`) both convert and filter: `/items/abc` and `/items/-1` don't match the rule at all, so Flask returns 404 before your code runs.

**Query parameters.** `request.args` is a `MultiDict`. `get(name, default, type=int)` returns the default when the key is missing and `None` when the conversion fails (`"x"`, `"1.5"`), so a single `is None` check catches both bad cases. Careful: with a *default*, a failed conversion silently returns the default (`?limit=ten` would become 10), so `limit` is converted by hand to reject it. `getlist("tag")` returns every repeated value in order.

**Automatic HTTP behaviour.** Flask answers methods you didn't list with 405 plus an `Allow` header (it adds `HEAD` and `OPTIONS` for you), and a rule ending in `/` redirects the slash-less URL with 308.

**Escaping.** A plain string is sent as HTML, so echoing user input verbatim is an XSS hole. `markupsafe.escape` turns `<` into `&lt;`. Templates do this automatically.

Complexity: O(1) per request plus the body size.

```python
from flask import Flask, request, url_for
from markupsafe import escape


def create_app():
    app = Flask(__name__)

    @app.route("/")
    def index():
        return "Hello, Flask!"

    @app.route("/hello/<name>")
    def hello(name):
        return f"Hello, {escape(name)}!"

    @app.get("/add")
    def add():
        a = request.args.get("a", type=int)
        b = request.args.get("b", type=int)
        if a is None or b is None:
            return {"error": "a and b must be integers"}, 400
        return {"sum": a + b}

    @app.get("/items/<int:item_id>")
    def item(item_id):
        return {"id": item_id}

    @app.get("/search")
    def search():
        raw = request.args.get("limit", "10")
        try:
            limit = int(raw)
        except ValueError:
            limit = 0                       # not an integer: reject below
        if not 1 <= limit <= 50:
            return {"error": "limit must be 1..50"}, 400
        return {"tags": request.args.getlist("tag"), "limit": limit}

    @app.route("/echo", methods=["GET", "POST"])
    def echo():
        if request.method == "GET":
            return "send me a POST"
        return {"method": "POST", "length": len(request.get_data()), "type": request.mimetype or None}

    @app.get("/docs/")
    def docs():
        return "docs index"

    @app.get("/where")
    def where():
        return url_for("hello", name="a b")

    return app
```
