---
id: py-resilient-fleet-client
title: A Resilient HTTP Client for a Fleet API
difficulty: Hard
order: 1
tags: httpx, retries, backoff, Retry-After, pagination, idempotency, validation, MockTransport
time_limit: 10
---
## Statement
Robots report to a fleet server over a flaky network. Write `FleetClient` on top of an injected `httpx.Client`. The judge passes a client built on `httpx.MockTransport` that scripts outages, rate limits and bad payloads. It also injects `sleep`, so it can check every backoff delay without actually waiting.

```python
class ApiError(Exception):
    def __init__(self, status, message): ...   # keep .status (int or None) and .message
class RobotNotFound(ApiError): ...             # status 404

class FleetClient:
    def __init__(self, client, *, retries=3, backoff=0.5, sleep=time.sleep): ...
    def get_robot(self, robot_id) -> dict
    def list_robots(self, status=None) -> list[dict]
    def send_command(self, robot_id, command: dict, key: str) -> dict
```

**Retry policy** (all requests):
- A **transient** failure is an `httpx.TransportError` (connect error, timeout, …) or a response with status **429, 502, 503 or 504**.
- Retry transient failures up to `retries` times, so there are at most `retries + 1` attempts.
- Before retry number `k` (k = 0, 1, …), call `sleep(d)`:
  - `d = float(Retry-After)` when the response has a numeric `Retry-After` header;
  - otherwise `d = backoff * 2**k`.
- When the attempts run out: if the last failure was an exception, re-raise it; if it was a response, raise `ApiError(status, "unavailable")`.
- Any other non-2xx status is **not** retried: 404 raises `RobotNotFound(404, ...)`, and anything else raises `ApiError(status, ...)`.

**Endpoints:**
- `get_robot(id)`: `GET /robots/{id}`. The payload must be a JSON object with `"id"` a string and `"battery"` a number (not bool) in [0, 1]. Otherwise raise `ApiError(None, "invalid payload")`. Invalid JSON also counts as an invalid payload.
- `list_robots(status=None)`: `GET /robots` with the query `status=...` only when given. The body is `{"items": [...]}`. Follow `rel="next"` `Link` headers until there are no more (use `response.links`) and return all items in order. Each page request has its own retry budget.
- `send_command(id, command, key)`: `POST /robots/{id}/commands` with JSON body `command` and the header `Idempotency-Key: key`. Every retry must reuse the **same** key. Return the response JSON (expected status 200 or 202).

## Starter
```python
import time
import httpx


class ApiError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status
        self.message = message


class RobotNotFound(ApiError):
    pass


class FleetClient:
    def __init__(self, client, *, retries=3, backoff=0.5, sleep=time.sleep):
        self.client = client

    def get_robot(self, robot_id):
        return self.client.get(f"/robots/{robot_id}").json()

    def list_robots(self, status=None):
        return self.client.get("/robots", params={"status": status}).json()["items"]

    def send_command(self, robot_id, command, key):
        return self.client.post(f"/robots/{robot_id}/commands", json=command).json()
```

## Driver
```python
import json as _json
import sys

class Server:
    def __init__(self):
        self.script = {}          # path -> list of actions consumed in order (last one repeats)
        self.log = []
    def handler(self, request):
        path = request.url.path
        q = dict(request.url.params)
        self.log.append((request.method, path + (("?" + "&".join(f"{k}={v}" for k, v in sorted(q.items()))) if q else ""),
                         request.headers.get("idempotency-key"), request.content.decode() or None))
        key = path if path != "/robots" else "/robots?" + q.get("page", "1") + q.get("status", "")
        acts = self.script.get(key) or self.script.get(path)
        if not acts:
            return httpx.Response(404, json={"detail": "nope"})
        act = acts.pop(0) if len(acts) > 1 else acts[0]
        if act == "connect":
            raise httpx.ConnectError("refused", request=request)
        if act == "timeout":
            raise httpx.ReadTimeout("slow", request=request)
        status, body, headers = act
        if isinstance(body, str):
            return httpx.Response(status, content=body.encode(), headers=headers)
        return httpx.Response(status, json=body, headers=headers)

def make(srv, **kw):
    sleeps = []
    c = httpx.Client(transport=httpx.MockTransport(srv.handler), base_url="https://fleet.test")
    return FleetClient(c, sleep=sleeps.append, **kw), sleeps

def attempt(label, fn):
    try:
        r = fn()
        print(f"{label}: ok {_json.dumps(r, sort_keys=True)}")
    except RobotNotFound as e:
        print(f"{label}: RobotNotFound status={e.status}")
    except ApiError as e:
        print(f"{label}: ApiError status={e.status} message={e.message}")
    except httpx.TransportError as e:
        print(f"{label}: {type(e).__name__}")

R1 = (200, {"id": "r1", "battery": 0.75}, {})
for cmd in sys.stdin.read().split():
    if cmd == "basic":
        s = Server(); s.script["/robots/r1"] = [R1]; fc, sl = make(s)
        attempt("get r1", lambda: fc.get_robot("r1"))
        attempt("get r9", lambda: fc.get_robot("r9"))
        print("requests", len(s.log), "sleeps", sl)
    elif cmd == "retry":
        s = Server(); s.script["/robots/r1"] = [(503, {}, {}), "connect", (502, "bad gateway", {}), R1]; fc, sl = make(s)
        attempt("flaky", lambda: fc.get_robot("r1")); print("sleeps", sl, "requests", len(s.log))
        s = Server(); s.script["/robots/r1"] = [(429, {}, {"Retry-After": "7"}), (429, {}, {"Retry-After": "soon"}), R1]; fc, sl = make(s)
        attempt("rate limited", lambda: fc.get_robot("r1")); print("sleeps", sl)
        s = Server(); s.script["/robots/r1"] = [(503, {}, {})]; fc, sl = make(s, retries=4, backoff=0.25)
        attempt("down", lambda: fc.get_robot("r1")); print("sleeps", sl, "requests", len(s.log))
        s = Server(); s.script["/robots/r1"] = ["timeout"]; fc, sl = make(s, retries=2)
        attempt("timeouts", lambda: fc.get_robot("r1")); print("sleeps", sl, "requests", len(s.log))
        s = Server(); s.script["/robots/r1"] = [(500, {}, {}), R1]; fc, sl = make(s)
        attempt("500 not retried", lambda: fc.get_robot("r1")); print("sleeps", sl, "requests", len(s.log))
        s = Server(); s.script["/robots/r1"] = [(401, {"detail": "no"}, {})]; fc, sl = make(s)
        attempt("401", lambda: fc.get_robot("r1")); print("requests", len(s.log))
    elif cmd == "validate":
        bodies = [{"id": "r1", "battery": 1}, {"id": 5, "battery": 0.5}, {"id": "r1", "battery": 1.2},
                  {"id": "r1", "battery": True}, {"id": "r1"}, [1, 2], "not json{", {"id": "r1", "battery": "0.5"}]
        for b in bodies:
            s = Server(); s.script["/robots/r1"] = [(200, b, {})]; fc, sl = make(s)
            attempt(f"payload {b!r}", lambda: fc.get_robot("r1"))
    elif cmd == "pages":
        s = Server()
        s.script["/robots?1"] = [(200, {"items": [{"id": "a"}, {"id": "b"}]}, {"Link": '<https://fleet.test/robots?page=2>; rel="next"'})]
        s.script["/robots?2"] = [(503, {}, {}), (200, {"items": [{"id": "c"}]}, {"Link": '<https://fleet.test/robots?page=3>; rel="next"'})]
        s.script["/robots?3"] = [(200, {"items": []}, {})]
        s.script["/robots?1idle"] = [(200, {"items": [{"id": "z"}]}, {})]
        fc, sl = make(s)
        attempt("all", lambda: fc.list_robots()); print("sleeps", sl)
        attempt("idle", lambda: fc.list_robots(status="idle"))
        for m, p, k, b in s.log: print(" ", m, p)
    elif cmd == "commands":
        s = Server(); s.script["/robots/r1/commands"] = ["timeout", (503, {}, {}), (202, {"accepted": True, "id": 17}, {})]; fc, sl = make(s)
        attempt("cmd", lambda: fc.send_command("r1", {"type": "goto", "x": 1.5}, "k-123"))
        for m, p, k, b in s.log: print(" ", m, p, k, b)
        print("sleeps", sl)
        s = Server(); s.script["/robots/r1/commands"] = [(409, {"detail": "busy"}, {})]; fc, sl = make(s)
        attempt("conflict", lambda: fc.send_command("r1", {"type": "stop"}, "k-9")); print("requests", len(s.log))
```

## Tests
=== sample
basic
retry
---
get r1: ok {"battery": 0.75, "id": "r1"}
get r9: RobotNotFound status=404
requests 2 sleeps []
flaky: ok {"battery": 0.75, "id": "r1"}
sleeps [0.5, 1.0, 2.0] requests 4
rate limited: ok {"battery": 0.75, "id": "r1"}
sleeps [7.0, 1.0]
down: ApiError status=503 message=unavailable
sleeps [0.25, 0.5, 1.0, 2.0] requests 5
timeouts: ReadTimeout
sleeps [0.5, 1.0] requests 3
500 not retried: ApiError status=500 message=request failed
sleeps [] requests 1
401: ApiError status=401 message=request failed
requests 1
=== hidden
validate
---
payload {'id': 'r1', 'battery': 1}: ok {"battery": 1, "id": "r1"}
payload {'id': 5, 'battery': 0.5}: ApiError status=None message=invalid payload
payload {'id': 'r1', 'battery': 1.2}: ApiError status=None message=invalid payload
payload {'id': 'r1', 'battery': True}: ApiError status=None message=invalid payload
payload {'id': 'r1'}: ApiError status=None message=invalid payload
payload [1, 2]: ApiError status=None message=invalid payload
payload 'not json{': ApiError status=None message=invalid payload
payload {'id': 'r1', 'battery': '0.5'}: ApiError status=None message=invalid payload
=== hidden
pages
---
all: ok [{"id": "a"}, {"id": "b"}, {"id": "c"}]
sleeps [0.5]
idle: ok [{"id": "z"}]
  GET /robots
  GET /robots?page=2
  GET /robots?page=2
  GET /robots?page=3
  GET /robots?status=idle
=== hidden
commands
---
cmd: ok {"accepted": true, "id": 17}
  POST /robots/r1/commands k-123 {"type":"goto","x":1.5}
  POST /robots/r1/commands k-123 {"type":"goto","x":1.5}
  POST /robots/r1/commands k-123 {"type":"goto","x":1.5}
sleeps [0.5, 1.0]
conflict: ApiError status=409 message=request failed
requests 1

## Hints
- Write one private `_request(method, url, **kw)` that owns the retry loop. Every endpoint calls it.
- Inside the loop, `try: r = self.client.request(...)` / `except httpx.TransportError as e:`, and remember the last failure. Check `if attempt == self.retries:` before sleeping.
- `Retry-After` may be non-numeric (an HTTP date). Only use it when `float()` succeeds.
- Pagination: `url = r.links.get("next", {}).get("url")`. httpx accepts absolute URLs on a client that has a `base_url`.
- Check `isinstance(x, bool)` **before** `isinstance(x, (int, float))`, because `True` is an `int`.

## Solution
```python
import time
import httpx


class ApiError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status
        self.message = message


class RobotNotFound(ApiError):
    pass


TRANSIENT = {429, 502, 503, 504}


class FleetClient:
    def __init__(self, client, *, retries=3, backoff=0.5, sleep=time.sleep):
        self.client = client
        self.retries = retries
        self.backoff = backoff
        self.sleep = sleep

    def _delay(self, attempt, response):
        if response is not None:
            ra = response.headers.get("Retry-After")
            if ra is not None:
                try:
                    return float(ra)
                except ValueError:
                    pass
        return self.backoff * 2 ** attempt

    def _request(self, method, url, **kw):
        for attempt in range(self.retries + 1):
            response = None
            try:
                response = self.client.request(method, url, **kw)
            except httpx.TransportError:
                if attempt == self.retries:
                    raise
            else:
                if response.status_code not in TRANSIENT:
                    break
                if attempt == self.retries:
                    raise ApiError(response.status_code, "unavailable")
            self.sleep(self._delay(attempt, response))
        if response.status_code == 404:
            raise RobotNotFound(404, "not found")
        if not 200 <= response.status_code < 300:
            raise ApiError(response.status_code, "request failed")
        return response

    @staticmethod
    def _json(response):
        try:
            return response.json()
        except ValueError:
            raise ApiError(None, "invalid payload") from None

    def get_robot(self, robot_id):
        data = self._json(self._request("GET", f"/robots/{robot_id}"))
        battery = data.get("battery") if isinstance(data, dict) else None
        if (not isinstance(data, dict) or not isinstance(data.get("id"), str)
                or isinstance(battery, bool) or not isinstance(battery, (int, float))
                or not 0 <= battery <= 1):
            raise ApiError(None, "invalid payload")
        return data

    def list_robots(self, status=None):
        items, url = [], "/robots"
        params = {"status": status} if status is not None else None
        while url:
            r = self._request("GET", url, params=params)
            items.extend(self._json(r)["items"])
            url = r.links.get("next", {}).get("url")
            params = None                      # the next link already carries the query
        return items

    def send_command(self, robot_id, command, key):
        r = self._request("POST", f"/robots/{robot_id}/commands", json=command,
                          headers={"Idempotency-Key": key})
        return self._json(r)
```

- **One retry loop** for every endpoint keeps the policy consistent, and puts it in one place to test.
- **Classification first**: transport errors and 429/502/503/504 are worth retrying. A 500 (a server bug) or a 4xx (our fault) would fail again identically, so it's raised at once.
- **Server hints win**: a numeric `Retry-After` overrides exponential backoff. Production code adds jitter and a cap. Here it's omitted so delays are deterministic.
- **Idempotency**: the POST's retries reuse one `Idempotency-Key`, so if a request reached the server but its response was lost, the server can deduplicate the command. The robot doesn't drive to the goal twice.
- **Validate the response**: a fleet-server bug (`"battery": "0.5"`, `True`, 1.2) is caught at the boundary instead of crashing decision logic later.
- **Injected sleep and transport** make a 30-second outage scenario a millisecond test.
