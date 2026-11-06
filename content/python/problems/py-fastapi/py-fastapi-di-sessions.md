---
id: py-fastapi-di-sessions
title: Dependency Injection for Database Sessions
difficulty: Medium
order: 3
tags: FastAPI, Depends, yield dependencies, transactions, commit/rollback, sub-dependencies, dependency_overrides, app.state
time_limit: 10
---
## Statement
The most important FastAPI pattern in real services: **one database session per request**, provided by a dependency that commits on success, rolls back on error and always closes.

The judge gives you a `Database` (built on in-memory sqlite3) through `create_app(db)`:

```python
db.session() -> Session            # a new session; it logs "open#k"
session.execute(sql, params=()) -> sqlite3.Cursor
session.commit() / session.rollback() / session.close()   # log "commit#k" / "rollback#k" / "close#k"
```

Tables: `users(name TEXT PRIMARY KEY)` and `accounts(name TEXT PRIMARY KEY, balance INTEGER)`.

Write these **module-level** functions (the judge overrides `get_session` in a test):

```python
def get_db(request: Request): ...                     # return request.app.state.db
def get_session(db = Depends(get_db)): ...            # yield db.session(); commit / rollback / close
def get_current_user(x_user: str | None = Header(None), session = Depends(get_session)) -> str: ...
def create_app(db) -> FastAPI: ...                    # stores db in app.state.db
```

- `get_session` yields one session. If the endpoint finishes normally, **commit**. If it raises anything (including `HTTPException`), **roll back** and re-raise. **Always close**. Exactly one session is opened per request, even though several dependencies use it (FastAPI caches a dependency within one request).
- `get_current_user` reads the `X-User` header and checks `SELECT 1 FROM users WHERE name = ?`. If the header is missing or the user is unknown → **401** `{"detail": "unknown user"}`.

Endpoints (both need the current user):
- `GET /me` → `{"user": name, "balance": b}`.
- `POST /transfer`, body `{"to": str, "amount": int > 0}` (422 otherwise). In this order, with the same session:
  1. `UPDATE accounts SET balance = balance - ? WHERE name = ?` for the sender;
  2. read the sender's new balance; if it's negative → **409** `{"detail": "insufficient funds"}`;
  3. `UPDATE accounts SET balance = balance + ? WHERE name = ?` for the recipient; if no row changed → **404** `{"detail": "no such account"}`;
  4. return `{"from": name, "to": to, "amount": amount, "balance": new_sender_balance}`.

  Because errors roll back, a failed transfer leaves both balances untouched, even though step 1 already ran.

Always use `?` placeholders. The driver prints responses, balances and the session log of each request.

## Starter
```python
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel


def get_db(request: Request):
    return request.app.state.db


def get_session(db=Depends(get_db)):
    return db.session()


def get_current_user(x_user: str | None = Header(None), session=Depends(get_session)) -> str:
    return x_user


def create_app(db):
    app = FastAPI()
    app.state.db = db

    @app.get("/me")
    def me(user: str = Depends(get_current_user), session=Depends(get_session)):
        bal = session.execute("SELECT balance FROM accounts WHERE name = ?", (user,)).fetchone()[0]
        return {"user": user, "balance": bal}

    return app
```

## Driver
```python
import json
import sqlite3
import sys
import warnings
warnings.simplefilter("ignore")
from fastapi.testclient import TestClient


class Session:
    def __init__(self, db, k):
        self.db, self.k = db, k
        db.log.append(f"open#{k}")
    def execute(self, sql, params=()):
        return self.db.conn.execute(sql, params)
    def commit(self):
        self.db.log.append(f"commit#{self.k}"); self.db.conn.commit()
    def rollback(self):
        self.db.log.append(f"rollback#{self.k}"); self.db.conn.rollback()
    def close(self):
        self.db.log.append(f"close#{self.k}")


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.conn.executescript("""
            CREATE TABLE users(name TEXT PRIMARY KEY);
            CREATE TABLE accounts(name TEXT PRIMARY KEY, balance INTEGER);
            INSERT INTO users VALUES ('ada'), ('bob'), ('eve');
            INSERT INTO accounts VALUES ('ada', 100), ('bob', 20), ('eve', 0), ('carol', 5);
        """)
        self.log, self.n = [], 0
    def session(self):
        self.n += 1
        return Session(self, self.n)
    def balances(self):
        return dict(self.conn.execute("SELECT name, balance FROM accounts ORDER BY name").fetchall())


def call(db, c, label, method, path, user=None, body=None):
    start = len(db.log)
    h = {"X-User": user} if user else {}
    r = c.request(method, path, headers=h, json=body)
    out = r.json()
    if r.status_code == 422:
        out = "validation error"
    print(f"{label}: {r.status_code} {json.dumps(out, sort_keys=True) if not isinstance(out, str) else out} | log {db.log[start:]}")

for g in sys.stdin.read().split():
    print("#", g)
    db = Database()
    app = create_app(db)
    c = TestClient(app, raise_server_exceptions=False)
    if g == "basic":
        call(db, c, "me ada", "GET", "/me", "ada")
        call(db, c, "me none", "GET", "/me")
        call(db, c, "me carol", "GET", "/me", "carol")
        call(db, c, "transfer", "POST", "/transfer", "ada", {"to": "bob", "amount": 30})
        print("balances", db.balances())
    elif g == "rollback":
        call(db, c, "too much", "POST", "/transfer", "bob", {"to": "ada", "amount": 21})
        print("balances", db.balances())
        call(db, c, "exact", "POST", "/transfer", "bob", {"to": "eve", "amount": 20})
        call(db, c, "no account", "POST", "/transfer", "ada", {"to": "zed", "amount": 10})
        print("balances", db.balances())
        call(db, c, "to carol", "POST", "/transfer", "ada", {"to": "carol", "amount": 100})
        call(db, c, "empty now", "POST", "/transfer", "ada", {"to": "bob", "amount": 1})
        print("balances", db.balances())
    elif g == "validation":
        call(db, c, "zero", "POST", "/transfer", "ada", {"to": "bob", "amount": 0})
        call(db, c, "negative", "POST", "/transfer", "ada", {"to": "bob", "amount": -5})
        call(db, c, "missing to", "POST", "/transfer", "ada", {"amount": 5})
        call(db, c, "unknown user", "POST", "/transfer", "mallory", {"to": "bob", "amount": 5})
        call(db, c, "self", "POST", "/transfer", "eve", {"to": "eve", "amount": 1})
        print("balances", db.balances())
    elif g == "override":
        class ReadOnly:
            def __init__(self):
                self.log = []
            def execute(self, sql, params=()):
                self.log.append(sql.split()[0])
                if sql.split()[0].upper() != "SELECT":
                    raise RuntimeError("read-only session")
                return db.conn.execute(sql, params)
        ro = ReadOnly()
        def fake_session():
            yield ro
        app.dependency_overrides[get_session] = fake_session
        call(db, c, "me via override", "GET", "/me", "bob")
        r = c.post("/transfer", headers={"X-User": "ada"}, json={"to": "bob", "amount": 1})
        print("transfer via override:", r.status_code, "statements", ro.log)
        app.dependency_overrides.clear()
        call(db, c, "after clear", "GET", "/me", "bob")
        print("balances", db.balances())
```

## Tests
=== sample
basic
---
# basic
me ada: 200 {"balance": 100, "user": "ada"} | log ['open#1', 'commit#1', 'close#1']
me none: 401 {"detail": "unknown user"} | log ['open#2', 'rollback#2', 'close#2']
me carol: 401 {"detail": "unknown user"} | log ['open#3', 'rollback#3', 'close#3']
transfer: 200 {"amount": 30, "balance": 70, "from": "ada", "to": "bob"} | log ['open#4', 'commit#4', 'close#4']
balances {'ada': 70, 'bob': 50, 'carol': 5, 'eve': 0}
=== hidden
rollback
---
# rollback
too much: 409 {"detail": "insufficient funds"} | log ['open#1', 'rollback#1', 'close#1']
balances {'ada': 100, 'bob': 20, 'carol': 5, 'eve': 0}
exact: 200 {"amount": 20, "balance": 0, "from": "bob", "to": "eve"} | log ['open#2', 'commit#2', 'close#2']
no account: 404 {"detail": "no such account"} | log ['open#3', 'rollback#3', 'close#3']
balances {'ada': 100, 'bob': 0, 'carol': 5, 'eve': 20}
to carol: 200 {"amount": 100, "balance": 0, "from": "ada", "to": "carol"} | log ['open#4', 'commit#4', 'close#4']
empty now: 409 {"detail": "insufficient funds"} | log ['open#5', 'rollback#5', 'close#5']
balances {'ada': 0, 'bob': 0, 'carol': 105, 'eve': 20}
=== hidden
validation
---
# validation
zero: 422 validation error | log ['open#1', 'rollback#1', 'close#1']
negative: 422 validation error | log ['open#2', 'rollback#2', 'close#2']
missing to: 422 validation error | log ['open#3', 'rollback#3', 'close#3']
unknown user: 401 {"detail": "unknown user"} | log ['open#4', 'rollback#4', 'close#4']
self: 409 {"detail": "insufficient funds"} | log ['open#5', 'rollback#5', 'close#5']
balances {'ada': 100, 'bob': 20, 'carol': 5, 'eve': 0}
=== hidden
override
---
# override
me via override: 200 {"balance": 20, "user": "bob"} | log []
transfer via override: 500 statements ['SELECT', 'SELECT', 'SELECT', 'UPDATE']
after clear: 200 {"balance": 20, "user": "bob"} | log ['open#1', 'commit#1', 'close#1']
balances {'ada': 100, 'bob': 20, 'carol': 5, 'eve': 0}

## Hints
- `get_session`: `s = db.session()`, then `try: yield s; s.commit()` / `except BaseException: s.rollback(); raise` / `finally: s.close()`.
- Don't create sessions anywhere else. Declare `session=Depends(get_session)` wherever you need one, and FastAPI shares a single instance per request.
- Raise `HTTPException` for 409/404 *inside* the endpoint after the first UPDATE. The dependency's rollback undoes it. Use `cursor.rowcount` to detect a missing recipient.

## Solution
**A `yield` dependency is a context manager for the request.** Code before `yield` runs before the endpoint. The yielded value is injected. When the endpoint returns, execution resumes after `yield` (commit). When it raises, the exception is thrown *into* the generator at the `yield`, so `except` can roll back and must re-raise. `finally` closes in every case. That's the unit-of-work-per-request pattern, the same thing `with Session() as s, s.begin():` does in SQLAlchemy.

**Per-request caching.** `get_current_user` and the endpoint both declare `Depends(get_session)`. FastAPI resolves it **once per request** and passes the same object to both, so the user lookup and the transfer share one transaction. (`Depends(get_session, use_cache=False)` would open a second one.)

**Why rollback matters here.** The transfer debits first and checks afterwards. On "insufficient funds" or "no such account", the `HTTPException` propagates through the dependency, the debit is rolled back, and the balances stay consistent.

**Testability.** Because `get_session` is a module-level function, a test can swap it with `app.dependency_overrides[get_session] = fake`, and every dependent (including `get_current_user`) receives the fake. No code changes, no monkey-patching.

Complexity: O(1) queries per request.

```python
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, Field


class TransferIn(BaseModel):
    to: str
    amount: int = Field(gt=0)


def get_db(request: Request):
    return request.app.state.db


def get_session(db=Depends(get_db)):
    session = db.session()
    try:
        yield session
        session.commit()
    except BaseException:
        session.rollback()
        raise
    finally:
        session.close()


def get_current_user(x_user: str | None = Header(None), session=Depends(get_session)) -> str:
    if not x_user or session.execute("SELECT 1 FROM users WHERE name = ?", (x_user,)).fetchone() is None:
        raise HTTPException(401, "unknown user")
    return x_user


def create_app(db):
    app = FastAPI()
    app.state.db = db

    @app.get("/me")
    def me(user: str = Depends(get_current_user), session=Depends(get_session)):
        row = session.execute("SELECT balance FROM accounts WHERE name = ?", (user,)).fetchone()
        return {"user": user, "balance": row[0] if row else 0}

    @app.post("/transfer")
    def transfer(body: TransferIn, user: str = Depends(get_current_user), session=Depends(get_session)):
        session.execute("UPDATE accounts SET balance = balance - ? WHERE name = ?", (body.amount, user))
        row = session.execute("SELECT balance FROM accounts WHERE name = ?", (user,)).fetchone()
        balance = row[0] if row else -body.amount
        if balance < 0:
            raise HTTPException(409, "insufficient funds")
        cur = session.execute("UPDATE accounts SET balance = balance + ? WHERE name = ?", (body.amount, body.to))
        if cur.rowcount == 0:
            raise HTTPException(404, "no such account")
        return {"from": user, "to": body.to, "amount": body.amount, "balance": balance}

    return app
```
