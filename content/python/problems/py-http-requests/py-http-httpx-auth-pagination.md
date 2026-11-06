---
id: py-http-httpx-auth-pagination
title: httpx Client with Token Refresh and Cursor Pagination
difficulty: Medium
order: 4
tags: httpx, MockTransport, httpx.Auth, bearer tokens, 401 refresh, cursor pagination, generators
time_limit: 5
---
## Statement
Build the client side of a token-protected, paginated JSON API with **httpx**. The judge serves the API from an `httpx.MockTransport`, so nothing touches the network.

```python
class TokenAuth(httpx.Auth):
    def __init__(self, fetch_token): ...       # fetch_token() -> str, may be slow: call it only when needed
    def auth_flow(self, request): ...          # a generator (see below)

def make_client(transport, fetch_token) -> httpx.Client: ...
def iter_items(client, path, page_size): ...   # a generator of item dicts
```

**`TokenAuth`** (an [`httpx.Auth`](https://www.python-httpx.org/advanced/authentication/) subclass):
- Fetch a token lazily on the first request and **cache** it for later requests.
- Send it as `Authorization: Bearer <token>`.
- If the response is **401**, fetch a fresh token and resend the same request **once**. If the retry is 401 too, return that response (no loops). Each request gets at most one refresh.

**`make_client`** returns an `httpx.Client` with `base_url="https://api.test"`, the given `transport`, `auth=TokenAuth(fetch_token)`, default headers `Accept: application/json` and `User-Agent: fleet-client/1.0`, and a 5-second timeout.

**`iter_items(client, path, page_size)`** walks cursor pagination **lazily**:
- The first request is `GET path` with query `limit=<page_size>`. Each later one adds `cursor=<next_cursor>`. Use `params=`, because cursors can contain characters such as spaces and `&`.
- A page's body is `{"items": [...], "next_cursor": <string or null>}`. Yield the items in order, and stop after a page whose `next_cursor` is `null`.
- Call `raise_for_status()` on every page, so an error page raises `httpx.HTTPStatusError` *after* the earlier items were yielded.
- Don't request page `k+1` until the consumer asks for an item beyond page `k`.

The driver prints the items it received, and the server's request log (method, path, query, the token it saw, and the default headers).

## Starter
```python
import httpx


class TokenAuth(httpx.Auth):
    def __init__(self, fetch_token):
        self.fetch_token = fetch_token

    def auth_flow(self, request):
        yield request


def make_client(transport, fetch_token):
    return httpx.Client(transport=transport, base_url="https://api.test")


def iter_items(client, path, page_size):
    r = client.get(path, params={"limit": page_size})
    return r.json()["items"]
```

## Driver
```python
import itertools
import json
import sys

ITEMS = [{"id": i, "name": f"robot-{i}"} for i in range(1, 8)]


class Server:
    def __init__(self, valid=("T1",), fail_page=None, cursor_style="plain", items=ITEMS):
        self.valid, self.fail_page, self.items = set(valid), fail_page, items
        self.cursor_style, self.log, self.seen = cursor_style, [], 0

    def cursor_for(self, i):
        return f"after {i}&x" if self.cursor_style == "weird" else f"c{i}"

    def __call__(self, request):
        self.seen += 1
        auth = request.headers.get("authorization", "-")
        q = "&".join(f"{k}={v}" for k, v in request.url.params.multi_items())
        self.log.append(f"{request.method} {request.url.path} [{q}] auth={auth} "
                        f"accept={request.headers.get('accept')} ua={request.headers.get('user-agent')}")
        if auth.removeprefix("Bearer ") not in self.valid_now():
            return httpx.Response(401, json={"detail": "bad token"})
        if request.url.path == "/echo":
            return httpx.Response(200, json={"echo": json.loads(request.content)})
        limit = int(request.url.params["limit"])
        cur = request.url.params.get("cursor")
        start = 0
        if cur is not None:
            start = next(i for i in range(len(self.items) + 1) if self.cursor_for(i) == cur)
        page_no = start // limit + 1
        if page_no == self.fail_page:
            return httpx.Response(500, json={"detail": "boom"})
        chunk = self.items[start:start + limit]
        nxt = self.cursor_for(start + limit) if start + limit < len(self.items) else None
        return httpx.Response(200, json={"items": chunk, "next_cursor": nxt})

    def valid_now(self):
        return self.valid


class Rotating(Server):
    """T1 works for the first 2 requests, then only T2 (then T3 after 6 requests)."""
    def valid_now(self):
        return {"T1"} if self.seen <= 2 else ({"T2"} if self.seen <= 6 else {"T3"})


def tokens():
    calls = []
    def fetch():
        calls.append(1)
        return f"T{len(calls)}"
    return fetch, calls


def run(cmd):
    fetch, calls = tokens()
    if cmd == "basic":
        srv = Server()
        c = make_client(httpx.MockTransport(srv), fetch)
        print("ids", [it["id"] for it in iter_items(c, "/robots", 3)])
    elif cmd == "lazy":
        srv = Server()
        c = make_client(httpx.MockTransport(srv), fetch)
        print("before", srv.seen, "fetches", len(calls))
        it = iter_items(c, "/robots", 2)
        print("created", srv.seen, "fetches", len(calls))
        print("first3", [x["id"] for x in itertools.islice(it, 3)])
    elif cmd == "rotate":
        srv = Rotating()
        c = make_client(httpx.MockTransport(srv), fetch)
        print("ids", [it["id"] for it in iter_items(c, "/robots", 2)])
        r = c.post("/echo", json={"cmd": "dock", "speed": 0.5})
        print("echo", r.status_code, r.json())
    elif cmd == "reject":
        srv = Server(valid=())
        c = make_client(httpx.MockTransport(srv), fetch)
        r1 = c.get("/robots", params={"limit": 1})
        r2 = c.get("/robots", params={"limit": 1})
        print("status", r1.status_code, r2.status_code)
        try:
            list(iter_items(c, "/robots", 2))
        except httpx.HTTPStatusError as e:
            print("raised", e.response.status_code)
    elif cmd == "error":
        srv = Server(fail_page=3)
        c = make_client(httpx.MockTransport(srv), fetch)
        got = []
        try:
            for x in iter_items(c, "/robots", 2):
                got.append(x["id"])
        except httpx.HTTPStatusError as e:
            print("raised", e.response.status_code, "after", got)
    elif cmd == "weird":
        srv = Server(cursor_style="weird")
        c = make_client(httpx.MockTransport(srv), fetch)
        print("ids", [it["id"] for it in iter_items(c, "/robots", 3)])
    elif cmd == "empty":
        srv = Server(items=[])
        c = make_client(httpx.MockTransport(srv), fetch)
        print("ids", list(iter_items(c, "/robots", 5)))
    elif cmd == "exact":
        srv = Server(items=ITEMS[:6])
        c = make_client(httpx.MockTransport(srv), fetch)
        print("ids", [it["id"] for it in iter_items(c, "/r", 3)], "timeout", c.timeout.read)
    print("fetches", len(calls))
    for line in srv.log:
        print("  ", line)


for cmd in sys.stdin.read().split():
    print("#", cmd)
    run(cmd)
```

## Tests
=== sample
basic
lazy
---
# basic
ids [1, 2, 3, 4, 5, 6, 7]
fetches 1
   GET /robots [limit=3] auth=Bearer T1 accept=application/json ua=fleet-client/1.0
   GET /robots [limit=3&cursor=c3] auth=Bearer T1 accept=application/json ua=fleet-client/1.0
   GET /robots [limit=3&cursor=c6] auth=Bearer T1 accept=application/json ua=fleet-client/1.0
# lazy
before 0 fetches 0
created 0 fetches 0
first3 [1, 2, 3]
fetches 1
   GET /robots [limit=2] auth=Bearer T1 accept=application/json ua=fleet-client/1.0
   GET /robots [limit=2&cursor=c2] auth=Bearer T1 accept=application/json ua=fleet-client/1.0
=== hidden
rotate
---
# rotate
ids [1, 2, 3, 4, 5, 6, 7]
echo 200 {'echo': {'cmd': 'dock', 'speed': 0.5}}
fetches 2
   GET /robots [limit=2] auth=Bearer T1 accept=application/json ua=fleet-client/1.0
   GET /robots [limit=2&cursor=c2] auth=Bearer T1 accept=application/json ua=fleet-client/1.0
   GET /robots [limit=2&cursor=c4] auth=Bearer T1 accept=application/json ua=fleet-client/1.0
   GET /robots [limit=2&cursor=c4] auth=Bearer T2 accept=application/json ua=fleet-client/1.0
   GET /robots [limit=2&cursor=c6] auth=Bearer T2 accept=application/json ua=fleet-client/1.0
   POST /echo [] auth=Bearer T2 accept=application/json ua=fleet-client/1.0
=== hidden
reject
---
# reject
status 401 401
raised 401
fetches 4
   GET /robots [limit=1] auth=Bearer T1 accept=application/json ua=fleet-client/1.0
   GET /robots [limit=1] auth=Bearer T2 accept=application/json ua=fleet-client/1.0
   GET /robots [limit=1] auth=Bearer T2 accept=application/json ua=fleet-client/1.0
   GET /robots [limit=1] auth=Bearer T3 accept=application/json ua=fleet-client/1.0
   GET /robots [limit=2] auth=Bearer T3 accept=application/json ua=fleet-client/1.0
   GET /robots [limit=2] auth=Bearer T4 accept=application/json ua=fleet-client/1.0
=== hidden
error
weird
---
# error
raised 500 after [1, 2, 3, 4]
fetches 1
   GET /robots [limit=2] auth=Bearer T1 accept=application/json ua=fleet-client/1.0
   GET /robots [limit=2&cursor=c2] auth=Bearer T1 accept=application/json ua=fleet-client/1.0
   GET /robots [limit=2&cursor=c4] auth=Bearer T1 accept=application/json ua=fleet-client/1.0
# weird
ids [1, 2, 3, 4, 5, 6, 7]
fetches 1
   GET /robots [limit=3] auth=Bearer T1 accept=application/json ua=fleet-client/1.0
   GET /robots [limit=3&cursor=after 3&x] auth=Bearer T1 accept=application/json ua=fleet-client/1.0
   GET /robots [limit=3&cursor=after 6&x] auth=Bearer T1 accept=application/json ua=fleet-client/1.0
=== hidden
empty
exact
---
# empty
ids []
fetches 1
   GET /robots [limit=5] auth=Bearer T1 accept=application/json ua=fleet-client/1.0
# exact
ids [1, 2, 3, 4, 5, 6] timeout 5.0
fetches 1
   GET /r [limit=3] auth=Bearer T1 accept=application/json ua=fleet-client/1.0
   GET /r [limit=3&cursor=c3] auth=Bearer T1 accept=application/json ua=fleet-client/1.0

## Hints
- In `auth_flow`, `response = yield request` gives you the response. Set the header, yield, check for 401, refresh, set the header again, and yield once more.
- Store the token on `self` and fetch it only when it's `None` or after a 401.
- Write `iter_items` with `while True:` and `yield from page["items"]`. Rebuild `params` each loop with the new cursor.

## Solution
**`httpx.Auth.auth_flow` is a generator conversation with the client.** You `yield` a request, and the client sends it and passes the response back in as the value of the `yield` expression. That lets one object implement "attach token → see 401 → refresh → retry" without the caller knowing. Because the request object is reused, a POST body is re-sent unchanged.

**Caching the token** in the auth object means one fetch serves many requests. Only a 401 triggers a refresh, and only once per request, so a server that rejects everything can't cause an infinite loop.

**Lazy pagination with a generator.** `iter_items` doesn't fetch anything until the first `next()`, and requests page `k+1` only after the consumer has drained page `k`. `islice(it, 3)` with pages of 2 makes exactly two requests. Passing the cursor through `params=` URL-encodes it, so a cursor like `after 2&x` arrives intact instead of being split into two query parameters.

**`raise_for_status()` per page** turns an error page into an exception at the exact point it happens. The consumer keeps the items it already processed.

Complexity: one request per page, O(page_size) memory.

```python
import httpx


class TokenAuth(httpx.Auth):
    def __init__(self, fetch_token):
        self.fetch_token = fetch_token
        self.token = None

    def auth_flow(self, request):
        if self.token is None:
            self.token = self.fetch_token()
        request.headers["Authorization"] = f"Bearer {self.token}"
        response = yield request
        if response.status_code == 401:
            self.token = self.fetch_token()                    # one refresh, one retry
            request.headers["Authorization"] = f"Bearer {self.token}"
            yield request


def make_client(transport, fetch_token):
    return httpx.Client(
        base_url="https://api.test",
        transport=transport,
        auth=TokenAuth(fetch_token),
        headers={"Accept": "application/json", "User-Agent": "fleet-client/1.0"},
        timeout=5.0,
    )


def iter_items(client, path, page_size):
    params = {"limit": page_size}
    while True:
        r = client.get(path, params=params)
        r.raise_for_status()
        page = r.json()
        yield from page["items"]
        if page["next_cursor"] is None:
            return
        params = {"limit": page_size, "cursor": page["next_cursor"]}
```
