# HTTP, requests and httpx

Robots and AI services talk HTTP constantly: fetching maps from a fleet server, posting telemetry, calling model-inference APIs, downloading datasets. Calling `requests.get(url).json()` is easy. Doing it **robustly** isn't: timeouts, retries with backoff, rate limits, pagination, authentication, connection reuse, streaming large files, and testing without a network. This lesson covers HTTP essentials, `requests`, `httpx` (sync and async), resilient client design, and mocking transports for tests.

## 1. HTTP in one table

| Concept | Details |
|---|---|
| Methods | `GET` (read, safe, idempotent), `POST` (create/act), `PUT` (replace, idempotent), `PATCH` (partial update), `DELETE` (idempotent) |
| Status 2xx | 200 OK, 201 Created, 204 No Content |
| Status 3xx | 301/302/307/308 redirects, 304 Not Modified (caching) |
| Status 4xx (client fault) | 400 Bad Request, 401 Unauthenticated, 403 Forbidden, 404 Not Found, 409 Conflict, 422 Unprocessable, **429 Too Many Requests** |
| Status 5xx (server fault) | 500, 502 Bad Gateway, **503 Unavailable**, 504 Gateway Timeout |
| Headers | `Content-Type`, `Authorization: Bearer <token>`, `Accept`, `Retry-After`, `ETag`/`If-None-Match`, `Link` (pagination) |

> [!KEY]
> **Idempotent** means doing it twice has the same effect as once. Only idempotent requests are safe to retry blindly. Retrying a `POST /orders` can create two orders, so for those use an `Idempotency-Key` header that the server deduplicates.

## 2. requests

```python
import requests

with requests.Session() as s:                              # connection pooling + shared headers
    s.headers.update({"Authorization": "Bearer TOKEN", "Accept": "application/json"})
    r = s.get("https://fleet.example/api/robots", params={"status": "active"}, timeout=(3.05, 10))
    r.raise_for_status()                                   # HTTPError for 4xx/5xx
    robots = r.json()
    r = s.post("https://fleet.example/api/missions", json={"robot": "r1", "goal": [3, 4]}, timeout=10)
```

- **Always pass `timeout`**. The default is to wait forever, and a hung server then hangs your robot's thread. `(connect, read)` tuples set the two separately.
- Use a `Session` for multiple requests: it keeps TCP/TLS connections alive (much faster) and shares headers and cookies.
- `json=` serialises the body and sets `Content-Type`. `params=` URL-encodes the query string correctly. Never build URLs with f-strings around user input.

## 3. httpx: modern, sync and async

`httpx` has a requests-like API plus HTTP/2, async support, strict timeouts by default (5 s), and pluggable **transports**:

```python
import httpx

with httpx.Client(base_url="https://fleet.example/api", timeout=httpx.Timeout(10.0, connect=3.0)) as c:
    r = c.get("/robots", params={"status": "active"})
    r.raise_for_status()

async def fetch_all(ids: list[str]) -> list[dict]:
    async with httpx.AsyncClient(base_url="https://fleet.example/api") as c:
        rs = await asyncio.gather(*(c.get(f"/robots/{i}") for i in ids))   # concurrent requests
        return [r.json() for r in rs]
```

## 4. Resilience: retries, backoff and rate limits

Transient failures (connection resets, 502/503/504, 429) should be retried with **exponential backoff and jitter**, honouring `Retry-After`. Permanent ones (400, 401, 404, 422) must not be retried.

```python
import random, time

RETRYABLE = {429, 502, 503, 504}

def get_with_retry(client: httpx.Client, url: str, *, attempts: int = 5, base: float = 0.5,
                   sleep=time.sleep) -> httpx.Response:
    for attempt in range(attempts):
        try:
            r = client.get(url)
        except (httpx.ConnectError, httpx.ReadTimeout):
            if attempt == attempts - 1: raise
            delay = base * 2 ** attempt
        else:
            if r.status_code not in RETRYABLE or attempt == attempts - 1:
                return r
            ra = r.headers.get("Retry-After")
            delay = float(ra) if ra and ra.replace(".", "", 1).isdigit() else base * 2 ** attempt
        sleep(delay * random.uniform(0.5, 1.0) if delay else 0)      # jitter avoids synchronized retry storms
    raise AssertionError("unreachable")
```

> [!TIP]
> Inject `sleep` (and a clock) as parameters. Tests pass a fake that records delays, so a 30-second backoff test runs in a millisecond. The same idea as passing `now_ms` into a state machine.

Libraries: `urllib3.Retry` mounted via `requests.adapters.HTTPAdapter(max_retries=...)`, `tenacity` (decorator-based retries), and `httpx.HTTPTransport(retries=n)`, which retries connection errors only.

**Circuit breaker**: after N consecutive failures, stop calling for a cool-down period and fail fast. It protects both your robot (no thread pile-up) and the overloaded server.

## 5. Pagination

APIs return large collections page by page. Iterate lazily with a generator:

```python
def iter_items(client: httpx.Client, url: str):
    while url:
        r = client.get(url); r.raise_for_status()
        yield from r.json()["items"]
        url = r.links.get("next", {}).get("url")     # RFC 8288 Link header: <...>; rel="next"
```

Styles: page/offset (`?page=3`), **cursor** (`?after=abc`, stable under inserts), and `Link` headers (used by GitHub).

## 6. Streaming large downloads

```python
with httpx.stream("GET", url, timeout=30) as r:
    r.raise_for_status()
    with open("map.pgm", "wb") as f:
        for chunk in r.iter_bytes(chunk_size=1 << 16):     # constant memory
            f.write(chunk)
```

## 7. Testing without the network

`httpx.MockTransport` routes requests to a Python function, with no sockets and fully deterministic:

```python
def handler(request: httpx.Request) -> httpx.Response:
    if request.url.path == "/robots/r1":
        return httpx.Response(200, json={"id": "r1", "battery": 0.8})
    return httpx.Response(404, json={"detail": "not found"})

client = httpx.Client(transport=httpx.MockTransport(handler), base_url="https://fleet.test")
assert client.get("/robots/r1").json()["battery"] == 0.8
assert client.get("/robots/zz").status_code == 404
```

For requests, use the `responses` or `requests-mock` libraries. In both cases you can simulate 503 storms, timeouts (raise `httpx.ReadTimeout` from the handler) and malformed JSON.

## 8. Security essentials

- Keep TLS verification on (`verify=True`, the default). Never ship `verify=False`.
- Keep secrets out of code and URLs. Read tokens from the environment or a secret store, and send them in headers.
- Validate response data (types, ranges) before acting on it. A pydantic model is ideal. A fleet server bug must not make a robot drive at 50 m/s.

> [!EXAM]
> **Design a robust HTTP client for a robot reporting telemetry to a server.**
> Use one long-lived session or client for connection reuse, with explicit connect and read timeouts. Classify failures: retry connection errors and 429/502/503/504 with exponential backoff plus jitter, honouring `Retry-After`, up to a bounded number of attempts. Never retry permanent 4xx errors, and make non-idempotent POSTs safe to retry with an idempotency key. Add a circuit breaker to fail fast during outages, buffer telemetry locally while offline, validate all responses, keep TLS verification and token-based auth, and inject the transport, sleep and clock so the behaviour can be tested deterministically with a mock transport.
