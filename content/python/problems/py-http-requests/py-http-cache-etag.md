---
id: py-http-cache-etag
title: A Private HTTP Cache with Cache-Control and ETags
difficulty: Medium
order: 5
tags: HTTP caching, Cache-Control, max-age, Age, ETag, If-None-Match, 304 Not Modified, stale-if-error, httpx
time_limit: 5
---
## Statement
Browsers and good API clients keep a **private cache** so they don't download the same thing twice. Implement one on top of an `httpx.Client`, plus the server's ETag comparison.

```python
def etag_matches(if_none_match: str, etag: str) -> bool: ...

class CachingClient:
    def __init__(self, client: httpx.Client, clock): ...   # clock() -> current time in seconds (float)
    def get(self, url: str) -> tuple[int, str, str]: ...   # (status, body text, source)
```

**`etag_matches`** (server side, *weak* comparison as used for `If-None-Match`): the header is `*` (matches anything) or a comma-separated list of entity tags such as `"v1", W/"v2"`. A tag matches when it equals `etag` after removing any `W/` prefix from **both**. Ignore spaces around list items.

**`CachingClient.get`**: entries are keyed by URL. Only `GET` responses with status **200** are stored.

1. Parse `Cache-Control` into directives: split on commas, strip, lower-case names. `max-age=N` gives the freshness lifetime; without it the lifetime is 0. Values never contain commas.
2. A stored entry remembers its body, its headers, the time `stored_at` it was received or revalidated, and its initial age (`Age` response header as an int, default 0).
   `current_age = initial_age + (clock() - stored_at)`.
3. If an entry exists, `current_age < lifetime`, and there's no `no-cache` directive, it's **fresh**: return `(200, body, "cache")` without any request.
4. Otherwise, send a GET. If the entry exists, make it **conditional**: add `If-None-Match: <ETag>` if the entry has an `ETag`, and `If-Modified-Since: <Last-Modified>` if it has a `Last-Modified`.
   - **304**: the entry is still valid. Update its stored headers with every header present in the 304 (for example a new `Cache-Control`), set `stored_at = clock()` and the initial age from the 304's `Age` (default 0). Return `(200, cached body, "revalidated")`.
   - **200**: replace the entry (see `no-store`) and return `(200, body, "network")`.
   - **Any other status**: if the entry has a `stale-if-error=N` directive and `current_age < lifetime + N`, return `(200, cached body, "stale")`. Otherwise return `(status, body, "network")`. Keep the entry either way.
5. A 200 response with `no-store` is never stored, and it **removes** any existing entry for that URL.

The judge's origin server runs on an `httpx.MockTransport` with a fake clock. It prints every result and each request the origin saw, with its conditional headers.

## Starter
```python
import httpx


def etag_matches(if_none_match, etag):
    return if_none_match == etag


class CachingClient:
    def __init__(self, client, clock):
        self.client = client
        self.clock = clock
        self.store = {}

    def get(self, url):
        if url in self.store:
            return 200, self.store[url], "cache"
        r = self.client.get(url)
        if r.status_code == 200:
            self.store[url] = r.text
        return r.status_code, r.text, "network"
```

## Driver
```python
import sys


class Clock:
    def __init__(self):
        self.t = 0.0
    def __call__(self):
        return self.t


class Origin:
    """Resources: url -> dict(body, version, headers(extra), etag(bool), lm(bool)). down: set of urls returning 500."""
    def __init__(self):
        self.res, self.down, self.log = {}, set(), []
        self.override_304 = {}

    def put(self, url, body, cc=None, etag=True, lm=False, age=None, status=200):
        old = self.res.get(url)
        v = old["v"] + 1 if old else 1
        self.res[url] = dict(body=body, v=v, cc=cc, etag=etag, lm=lm, age=age, status=status)

    def headers_for(self, url, r):
        h = {}
        if r["cc"]:
            h["Cache-Control"] = r["cc"]
        if r["etag"]:
            h["ETag"] = f'W/"{url.strip("/")}-v{r["v"]}"' if url.endswith("w") else f'"{url.strip("/")}-v{r["v"]}"'
        if r["lm"]:
            h["Last-Modified"] = f"Mon, 0{r['v']} Jan 2024 00:00:00 GMT"
        if r["age"] is not None:
            h["Age"] = str(r["age"])
        return h

    def __call__(self, request):
        url = request.url.path
        inm, ims = request.headers.get("if-none-match"), request.headers.get("if-modified-since")
        self.log.append(f"{url}" + (f" inm={inm}" if inm else "") + (f" ims={ims}" if ims else ""))
        if url in self.down:
            return httpx.Response(500, text="origin down")
        r = self.res.get(url)
        if r is None:
            return httpx.Response(404, text="nope")
        h = self.headers_for(url, r)
        if r["status"] == 200:
            if inm and "ETag" in h and etag_matches(inm, h["ETag"]) or (not inm and ims and ims == h.get("Last-Modified")):
                h304 = {k: v for k, v in h.items() if k != "Last-Modified"}
                h304.update(self.override_304.get(url, {}))
                return httpx.Response(304, headers=h304)
        return httpx.Response(r["status"], text=r["body"], headers=h)


def scenario(name):
    clock, o = Clock(), Origin()
    c = CachingClient(httpx.Client(transport=httpx.MockTransport(o), base_url="https://origin.test"), clock)
    steps = []
    def at(t, url):
        clock.t = t
        steps.append(f"t={t:g} {url} -> {c.get(url)}")
    if name == "fresh":
        o.put("/a", "A1", cc="max-age=60")
        for t in (0, 30, 59.9, 60, 100):
            at(t, "/a")
        o.put("/a", "A2", cc="max-age=60")
        at(119, "/a"); at(121, "/a"); at(122, "/a")
    elif name == "age":
        o.put("/b", "B1", cc="public, max-age=60", age=50)
        at(0, "/b"); at(9.5, "/b"); at(10, "/b"); at(15, "/b")
    elif name == "nostore":
        o.put("/c", "C1", cc="no-store")
        at(0, "/c"); at(1, "/c")
        o.put("/c2", "X1", cc="max-age=100")
        at(2, "/c2"); at(3, "/c2")
        o.put("/c2", "X2", cc="No-Store")
        at(200, "/c2"); at(201, "/c2")
    elif name == "nocache":
        o.put("/d", "D1", cc="no-cache, max-age=600")
        at(0, "/d"); at(1, "/d")
        o.put("/d", "D2", cc="no-cache, max-age=600")
        at(2, "/d"); at(3, "/d")
    elif name == "validators":
        o.put("/e", "E1", cc="max-age=10", etag=False, lm=True)
        o.put("/f", "F1", cc="max-age=10", etag=False)
        at(0, "/e"); at(0, "/f"); at(11, "/e"); at(11, "/f"); at(12, "/f")
    elif name == "error":
        o.put("/g", "G1", cc="max-age=10, stale-if-error=30")
        o.put("/h", "H1", cc="max-age=10")
        at(0, "/g"); at(0, "/h")
        o.down |= {"/g", "/h"}
        at(20, "/g"); at(39.9, "/g"); at(40, "/g"); at(20, "/h")
        o.down.clear()
        at(41, "/g"); at(42, "/g")
    elif name == "update304":
        o.put("/i", "I1", cc="max-age=100")
        o.override_304["/i"] = {"Cache-Control": "max-age=5", "Age": "2"}
        at(0, "/i"); at(150, "/i"); at(152, "/i"); at(153, "/i")
    elif name == "missing":
        at(0, "/zzz"); at(1, "/zzz")
        o.put("/w", "W1", cc="MAX-AGE=20 , Private")
        at(2, "/w"); at(21, "/w"); at(22, "/w")
    elif name == "matches":
        for inm, et in [('"a"', '"a"'), ('"a"', '"b"'), ('*', '"q"'), ('"x", "y" ,W/"z"', '"z"'),
                        ('W/"a"', '"a"'), ('"a"', 'W/"a"'), ('"ab"', '"a"'), ('"a", "b"', 'W/"c"'), ('  "k"  ', '"k"')]:
            steps.append(f"{inm!r} vs {et!r}: {etag_matches(inm, et)}")
    print("#", name)
    for s in steps:
        print(s)
    print("origin saw:", "; ".join(o.log) or "-")


for name in sys.stdin.read().split():
    scenario(name)
```

## Tests
=== sample
fresh
matches
---
# fresh
t=0 /a -> (200, 'A1', 'network')
t=30 /a -> (200, 'A1', 'cache')
t=59.9 /a -> (200, 'A1', 'cache')
t=60 /a -> (200, 'A1', 'revalidated')
t=100 /a -> (200, 'A1', 'cache')
t=119 /a -> (200, 'A1', 'cache')
t=121 /a -> (200, 'A2', 'network')
t=122 /a -> (200, 'A2', 'cache')
origin saw: /a; /a inm="a-v1"; /a inm="a-v1"
# matches
'"a"' vs '"a"': True
'"a"' vs '"b"': False
'*' vs '"q"': True
'"x", "y" ,W/"z"' vs '"z"': True
'W/"a"' vs '"a"': True
'"a"' vs 'W/"a"': True
'"ab"' vs '"a"': False
'"a", "b"' vs 'W/"c"': False
'  "k"  ' vs '"k"': True
origin saw: -
=== hidden
age
nostore
---
# age
t=0 /b -> (200, 'B1', 'network')
t=9.5 /b -> (200, 'B1', 'cache')
t=10 /b -> (200, 'B1', 'revalidated')
t=15 /b -> (200, 'B1', 'cache')
origin saw: /b; /b inm="b-v1"
# nostore
t=0 /c -> (200, 'C1', 'network')
t=1 /c -> (200, 'C1', 'network')
t=2 /c2 -> (200, 'X1', 'network')
t=3 /c2 -> (200, 'X1', 'cache')
t=200 /c2 -> (200, 'X2', 'network')
t=201 /c2 -> (200, 'X2', 'network')
origin saw: /c; /c; /c2; /c2 inm="c2-v1"; /c2
=== hidden
nocache
validators
---
# nocache
t=0 /d -> (200, 'D1', 'network')
t=1 /d -> (200, 'D1', 'revalidated')
t=2 /d -> (200, 'D2', 'network')
t=3 /d -> (200, 'D2', 'revalidated')
origin saw: /d; /d inm="d-v1"; /d inm="d-v1"; /d inm="d-v2"
# validators
t=0 /e -> (200, 'E1', 'network')
t=0 /f -> (200, 'F1', 'network')
t=11 /e -> (200, 'E1', 'revalidated')
t=11 /f -> (200, 'F1', 'network')
t=12 /f -> (200, 'F1', 'cache')
origin saw: /e; /f; /e ims=Mon, 01 Jan 2024 00:00:00 GMT; /f
=== hidden
error
---
# error
t=0 /g -> (200, 'G1', 'network')
t=0 /h -> (200, 'H1', 'network')
t=20 /g -> (200, 'G1', 'stale')
t=39.9 /g -> (200, 'G1', 'stale')
t=40 /g -> (500, 'origin down', 'network')
t=20 /h -> (500, 'origin down', 'network')
t=41 /g -> (200, 'G1', 'revalidated')
t=42 /g -> (200, 'G1', 'cache')
origin saw: /g; /h; /g inm="g-v1"; /g inm="g-v1"; /g inm="g-v1"; /h inm="h-v1"; /g inm="g-v1"
=== hidden
update304
missing
---
# update304
t=0 /i -> (200, 'I1', 'network')
t=150 /i -> (200, 'I1', 'revalidated')
t=152 /i -> (200, 'I1', 'cache')
t=153 /i -> (200, 'I1', 'revalidated')
origin saw: /i; /i inm="i-v1"; /i inm="i-v1"
# missing
t=0 /zzz -> (404, 'nope', 'network')
t=1 /zzz -> (404, 'nope', 'network')
t=2 /w -> (200, 'W1', 'network')
t=21 /w -> (200, 'W1', 'cache')
t=22 /w -> (200, 'W1', 'revalidated')
origin saw: /zzz; /zzz; /w; /w inm=W/"w-v1"

## Hints
- Store `stored_at = clock()` and the initial `Age` with the entry. Fresh means `age0 + (clock() - stored_at) < max_age` and no `no-cache`.
- Build the conditional headers from the stored `ETag` / `Last-Modified`. On 304, copy every 304 header onto the stored headers and reset the timestamp.
- `httpx.Headers` is case-insensitive, which makes `cache-control` vs `Cache-Control` a non-issue. For `etag_matches`, split on commas, strip, and drop a leading `W/`.

## Solution
**Freshness is arithmetic.** `max-age` says how long the response may be reused. `Age` says how old it already was when it reached us (it may have sat in a CDN). So the current age is `initial_age + time since stored`, and the entry is fresh while that's below the lifetime. Within that window the cache doesn't touch the network at all. That's the biggest win, because no request beats a fast request.

**Revalidation is cheap.** Once stale, the entry isn't thrown away. The client asks "has it changed?" with `If-None-Match: <etag>` (or `If-Modified-Since`). An unchanged resource costs a bodyless **304**, and the 304's headers refresh the entry (a new `max-age` applies from then on). `no-cache` doesn't mean "don't cache". It means "always revalidate before using", whereas `no-store` means "never keep it".

**Weak comparison on the server.** `W/"v1"` marks a weak validator (semantically equivalent, not byte-identical). `If-None-Match` uses weak comparison, so the `W/` prefix is ignored on both sides. Comparing with substring tests would wrongly match `"ab"` against `"a"`.

**`stale-if-error`** lets a cache serve a slightly stale copy when the origin is failing, which turns an outage into degraded freshness instead of errors.

Complexity: O(1) per request plus header parsing.

```python
import httpx


def etag_matches(if_none_match, etag):
    if if_none_match.strip() == "*":
        return True
    strip = lambda t: t.strip().removeprefix("W/")
    return any(strip(t) == strip(etag) for t in if_none_match.split(","))


def directives(headers):
    out = {}
    for part in headers.get("cache-control", "").split(","):
        name, _, value = part.strip().partition("=")
        if name:
            out[name.strip().lower()] = value.strip()
    return out


class CachingClient:
    def __init__(self, client, clock):
        self.client = client
        self.clock = clock
        self.store = {}          # url -> {"body", "headers", "stored_at", "age0"}

    def _lifetime(self, d):
        return int(d["max-age"]) if "max-age" in d else 0

    def _save(self, url, r):
        self.store[url] = {"body": r.text, "headers": httpx.Headers(r.headers),
                           "stored_at": self.clock(), "age0": int(r.headers.get("age", 0))}

    def get(self, url):
        e = self.store.get(url)
        age = d = None
        if e:
            d = directives(e["headers"])
            age = e["age0"] + (self.clock() - e["stored_at"])
            if age < self._lifetime(d) and "no-cache" not in d:
                return 200, e["body"], "cache"
        cond = {}
        if e:
            if "etag" in e["headers"]:
                cond["If-None-Match"] = e["headers"]["etag"]
            if "last-modified" in e["headers"]:
                cond["If-Modified-Since"] = e["headers"]["last-modified"]
        r = self.client.get(url, headers=cond)
        if r.status_code == 304 and e:
            for k, v in r.headers.items():
                e["headers"][k] = v
            e["stored_at"], e["age0"] = self.clock(), int(r.headers.get("age", 0))
            return 200, e["body"], "revalidated"
        if r.status_code == 200:
            if "no-store" in directives(r.headers):
                self.store.pop(url, None)
            else:
                self._save(url, r)
            return 200, r.text, "network"
        if e and "stale-if-error" in d and age < self._lifetime(d) + int(d["stale-if-error"]):
            return 200, e["body"], "stale"
        return r.status_code, r.text, "network"
```
