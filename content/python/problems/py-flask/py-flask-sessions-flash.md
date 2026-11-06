---
id: py-flask-sessions-flash
title: Sessions, Flash Messages and Safe Redirects
difficulty: Medium
order: 5
tags: Flask, session, signed cookies, flash, redirect, open redirect, SameSite, HttpOnly, session.modified
time_limit: 5
---
## Statement
Add login state to a Flask app with its **signed-cookie session** and **flash messages**.

```python
def create_app(secret_key: str, users: dict[str, str]) -> Flask: ...   # users: username -> password
```

Config: `SECRET_KEY = secret_key`, `SESSION_COOKIE_SAMESITE = "Lax"`, `SESSION_COOKIE_HTTPONLY = True`.

| Route | Behaviour |
|---|---|
| `GET /` | text: one line `<category>: <message>` per pending flash message (in order), then a last line `user: <username>` or `user: anonymous`. Lines joined with `\n`. |
| `POST /login` | form fields `username`, `password`. On success: clear the session, store `session["user"]`, flash `Welcome, <username>!` (category `success`), and redirect (302) to the `next` query parameter if it's **safe**, else to `/`. On failure: flash `Invalid credentials` (category `error`) and redirect to `/`. |
| `POST /logout` | clear the session, flash `Signed out` (category `info`), redirect to `/`. |
| `POST /cart/add/<item>` | logged in: increase `session["cart"][item]` by 1 and return JSON `{"cart": {...}}`. Not logged in: **401** `{"error": "login required"}`. |
| `GET /cart` | logged in: `{"user": ..., "cart": {...}}` (empty dict if nothing added). Otherwise 401 as above. |

Rules:
- Compare passwords with `hmac.compare_digest`. An unknown username is a failure, not an exception.
- A `next` target is **safe** only if it starts with `/`, its second character is neither `/` nor `\`, and it contains no `\r` or `\n`. Anything else (for example `https://evil.example` or `//evil.example`) is an **open redirect** and must be replaced by `/`.
- The session stores only `user`, `cart` and Flask's own flash data. Never store the password.
- Mutating a dict inside the session doesn't mark it changed. Set `session.modified = True`, or reassign the key.

The driver follows no redirects automatically. It prints statuses and `Location` headers, the cookie flags, the decoded session contents, and what happens when the cookie is tampered with.

## Starter
```python
from flask import Flask, flash, get_flashed_messages, jsonify, redirect, request, session


def create_app(secret_key, users):
    app = Flask(__name__)
    app.secret_key = secret_key

    @app.get("/")
    def index():
        return f"user: {session.get('user', 'anonymous')}"

    @app.post("/login")
    def login():
        u = request.form["username"]
        if users.get(u) == request.form["password"]:
            session["user"] = u
            session["password"] = request.form["password"]
        return redirect(request.args.get("next", "/"))

    return app
```

## Driver
```python
import sys

USERS = {"ada": "lovelace", "linus": "tux"}

def show(label, r):
    loc = f" -> {r.headers['Location']}" if "Location" in r.headers else ""
    body = r.get_data(as_text=True) if r.status_code < 300 or r.status_code >= 400 else ""
    if r.mimetype == "text/html" and 300 <= r.status_code < 400:
        body = ""
    print(f"{label}: {r.status_code}{loc} {body.strip()!r}" if body else f"{label}: {r.status_code}{loc}")

def session_of(app, c):
    ck = c.get_cookie("session")
    if ck is None:
        return None
    data = app.session_interface.get_signing_serializer(app).loads(ck.value)
    return {k: data[k] for k in sorted(data) if k != "_flashes"} | ({"_flashes": len(data["_flashes"])} if "_flashes" in data else {})

for g in sys.stdin.read().split():
    print("#", g)
    app = create_app("test-secret-key", USERS)
    c = app.test_client()
    if g == "login":
        show("home", c.get("/"))
        r = c.post("/login", data={"username": "ada", "password": "lovelace"})
        show("login", r)
        sc = r.headers.get("Set-Cookie", "")
        print("cookie flags:", "HttpOnly" in sc, "SameSite=Lax" in sc)
        print("session:", session_of(app, c))
        show("home", c.get("/"))
        show("home again", c.get("/"))
        show("logout", c.post("/logout"))
        show("home", c.get("/"))
    elif g == "failures":
        show("wrong pw", c.post("/login", data={"username": "ada", "password": "nope"}))
        show("unknown", c.post("/login", data={"username": "zed", "password": "x"}))
        show("home", c.get("/"))
        print("session:", session_of(app, c))
        show("cart anon", c.get("/cart"))
        show("add anon", c.post("/cart/add/pen"))
    elif g == "redirects":
        for nxt in ["/cart", "/a/b?c=1", "https://evil.example", "//evil.example", "/\\evil.example", "cart", "", "/ok\r\nX: y"]:
            r = c.post("/login", query_string={"next": nxt}, data={"username": "linus", "password": "tux"})
            print(f"next={nxt!r}: {r.status_code} -> {r.headers.get('Location')}")
        c.get("/")
    elif g == "cart":
        c.post("/login", data={"username": "linus", "password": "tux"})
        c.get("/")
        show("empty", c.get("/cart"))
        show("add pen", c.post("/cart/add/pen"))
        show("add pen", c.post("/cart/add/pen"))
        show("add ink", c.post("/cart/add/ink"))
        show("cart", c.get("/cart"))
        print("session:", session_of(app, c))
        good = c.get_cookie("session").value
        c.set_cookie("session", good[:-2] + ("AA" if good[-2:] != "AA" else "BB"))
        show("tampered cart", c.get("/cart"))
        show("tampered home", c.get("/"))
        other = create_app("other-key", USERS)
        oc = other.test_client()
        oc.set_cookie("session", good)
        show("other key", oc.get("/cart"))
        c.set_cookie("session", good)
        show("restored", c.get("/cart"))
        show("relogin as ada", c.post("/login", data={"username": "ada", "password": "lovelace"}))
        show("cart after relogin", c.get("/cart"))
```

## Tests
=== sample
login
---
# login
home: 200 'user: anonymous'
login: 302 -> /
cookie flags: True True
session: {'user': 'ada', '_flashes': 1}
home: 200 'success: Welcome, ada!\nuser: ada'
home again: 200 'user: ada'
logout: 302 -> /
home: 200 'info: Signed out\nuser: anonymous'
=== hidden
failures
---
# failures
wrong pw: 302 -> /
unknown: 302 -> /
home: 200 'error: Invalid credentials\nerror: Invalid credentials\nuser: anonymous'
session: None
cart anon: 401 '{"error":"login required"}'
add anon: 401 '{"error":"login required"}'
=== hidden
redirects
---
# redirects
next='/cart': 302 -> /cart
next='/a/b?c=1': 302 -> /a/b?c=1
next='https://evil.example': 302 -> /
next='//evil.example': 302 -> /
next='/\\evil.example': 302 -> /
next='cart': 302 -> /
next='': 302 -> /
next='/ok\r\nX: y': 302 -> /
=== hidden
cart
---
# cart
empty: 200 '{"cart":{},"user":"linus"}'
add pen: 200 '{"cart":{"pen":1}}'
add pen: 200 '{"cart":{"pen":2}}'
add ink: 200 '{"cart":{"ink":1,"pen":2}}'
cart: 200 '{"cart":{"ink":1,"pen":2},"user":"linus"}'
session: {'cart': {'ink': 1, 'pen': 2}, 'user': 'linus'}
tampered cart: 401 '{"error":"login required"}'
tampered home: 200 'user: anonymous'
other key: 401 '{"error":"login required"}'
restored: 200 '{"cart":{"ink":1,"pen":2},"user":"linus"}'
relogin as ada: 302 -> /
cart after relogin: 200 '{"cart":{},"user":"ada"}'

## Hints
- `get_flashed_messages(with_categories=True)` returns `(category, message)` pairs and consumes them. `flash(msg, category)` adds one.
- On successful login: `session.clear()`, set `session["user"]`, flash, then redirect through a `safe_next()` helper that returns `"/"` for anything not starting with a single `/`.
- After `session.setdefault("cart", {})[item] += …`, set `session.modified = True`, or the change is never written back to the cookie.

## Solution
**Flask's session is a signed cookie.** The data is serialised, signed with `SECRET_KEY` (HMAC), and sent to the browser. The client can *read* it (it's only base64), but can't *change* it: a tampered cookie, or one signed with another key, fails verification, and Flask treats the request as having an empty session. So never put secrets (passwords) in it, and keep it small.

**Flash messages** are stored in the session for exactly one later request: `get_flashed_messages()` reads them and removes them. That's the Post/Redirect/Get pattern. The POST changes state and redirects, and the following GET shows the message once, so a browser refresh doesn't resubmit the form.

**Security details.**
- `hmac.compare_digest` compares in constant time, so timing doesn't reveal how much of a password matched. (Real apps store password *hashes*, which the authentication lesson covers.)
- `session.clear()` on login prevents a previous user's data from leaking into the new login.
- `next` redirects are validated: `//evil.example` and `/\evil.example` are treated by browsers as links to another host, so only single-slash relative paths are allowed. Otherwise the login page becomes an **open redirect** that phishers use.
- `SameSite=Lax` stops the cookie being sent on cross-site POSTs (CSRF), and `HttpOnly` hides it from JavaScript (XSS).

**`session.modified`:** the session tracks assignments to its own keys, not changes inside nested objects.

Complexity: O(size of the session) per request (it's re-serialised and re-signed).

```python
import hmac

from flask import Flask, flash, get_flashed_messages, redirect, request, session


def safe_next(target):
    if not target or not target.startswith("/") or target[1:2] in ("/", "\\"):
        return "/"
    if "\r" in target or "\n" in target:
        return "/"
    return target


def create_app(secret_key, users):
    app = Flask(__name__)
    app.config.update(SECRET_KEY=secret_key, SESSION_COOKIE_SAMESITE="Lax", SESSION_COOKIE_HTTPONLY=True)

    @app.get("/")
    def index():
        lines = [f"{cat}: {msg}" for cat, msg in get_flashed_messages(with_categories=True)]
        lines.append(f"user: {session.get('user', 'anonymous')}")
        return "\n".join(lines)

    @app.post("/login")
    def login():
        u = request.form.get("username", "")
        p = request.form.get("password", "")
        expected = users.get(u)
        if expected is not None and hmac.compare_digest(expected.encode(), p.encode()):
            session.clear()                      # drop any previous user's data (and session fixation)
            session["user"] = u
            flash(f"Welcome, {u}!", "success")
            return redirect(safe_next(request.args.get("next", "")))
        flash("Invalid credentials", "error")
        return redirect("/")

    @app.post("/logout")
    def logout():
        session.clear()
        flash("Signed out", "info")
        return redirect("/")

    def require_user():
        return None if "user" in session else ({"error": "login required"}, 401)

    @app.post("/cart/add/<item>")
    def add(item):
        if (e := require_user()):
            return e
        cart = session.setdefault("cart", {})
        cart[item] = cart.get(item, 0) + 1
        session.modified = True                  # in-place mutation is invisible to the session object
        return {"cart": cart}

    @app.get("/cart")
    def cart():
        if (e := require_user()):
            return e
        return {"user": session["user"], "cart": session.get("cart", {})}

    return app
```
