---
id: py-http-status-decider
title: Status Code Decision Table
difficulty: Easy
order: 3
tags: HTTP, status codes, decision table, idempotency, conditional requests, headers
time_limit: 2
---
## Statement
Real servers decide a response status by running a request through a fixed sequence of checks (Erlang's webmachine popularised this as an HTTP "decision diagram"). Implement one.

```python
def decide(req: dict[str, str]) -> tuple[int, list[str]]:
    """Return (status, extra header lines) for a request described by facts."""
```

`req` holds these facts. A missing key takes the default shown.

| Key | Values | Default | Meaning |
|---|---|---|---|
| `method` | any uppercase word | — | the HTTP method |
| `allow` | comma list, e.g. `GET,PUT` | `GET` | methods this resource implements |
| `maint` | `0` / `1` | `0` | server is in maintenance |
| `rate` | `0` / `1` | `0` | the client exceeded its rate limit |
| `auth` | `ok` / `none` / `bad` | `ok` | credentials: valid, absent, invalid |
| `perm` | `0` / `1` | `1` | authenticated user may perform this action |
| `accept` | `json` / `xml` / `any` | `any` | the client's `Accept` (the server produces JSON only) |
| `ctype` | `json` / `xml` / `none` | `json` | request body content type |
| `body` | `ok` / `malformed` / `invalid` | `ok` | body parses and validates / is not parseable / parses but breaks rules |
| `exists` | `0` / `1` | `1` | the target resource exists |
| `inm` | `match` / `nomatch` / `none` | `none` | `If-None-Match` result against the current ETag |
| `im` | `match` / `mismatch` / `none` | `none` | `If-Match` result |
| `conflict` | `0` / `1` | `0` | the change conflicts with the resource's state |
| `upstream` | `ok` / `bad` / `timeout` | `ok` | a backend this request needs |

The **effective allow set** is `allow` plus `HEAD` if `GET` is in it, plus `OPTIONS` always. The standard methods are `GET HEAD POST PUT PATCH DELETE OPTIONS`. Body methods are `POST PUT PATCH`.

Run the checks **in this order**. The first that applies decides:

1. `maint=1` → **503**, header `Retry-After`.
2. Method not standard → **501**.
3. Method not in the effective allow set → **405**, header `Allow: <effective set, sorted, ", "-joined>`.
4. `rate=1` → **429**, header `Retry-After`.
5. `auth` is `none` or `bad` → **401**, header `WWW-Authenticate`. Then `perm=0` → **403**.
6. `accept=xml` → **406**.
7. Body methods only: `ctype` not `json` → **415**; `body=malformed` → **400**; `body=invalid` → **422**.
8. Preconditions: `im=mismatch` with `PUT`/`PATCH`/`DELETE` → **412**. `inm=match` with `GET`/`HEAD` and `exists=1` → **304**, header `ETag`.
9. `exists=0`: `PUT` continues (it will create the resource), `OPTIONS` continues; every other method → **404**.
10. `conflict=1` with `POST`/`PUT`/`PATCH`/`DELETE` → **409**.
11. `upstream=bad` → **502**; `upstream=timeout` → **504**.
12. Success: `GET`/`HEAD` → **200** with `ETag`; `POST` → **201** with `Location`; `PUT` → **200** if it existed, else **201** with `Location`; `PATCH` → **200**; `DELETE` → **204**; `OPTIONS` → **204** with `Allow: …` (as in step 3).

Header lines are returned as just the header name (`"Retry-After"`, `"ETag"`, …), except `Allow`, which carries its value.

**Input:** one request per line as `key=value` tokens. **Output:** the status, then the header lines separated by single spaces.

## Starter
```python
def decide(req):
    method = req["method"]
    if method == "POST":
        return 201, ["Location"]
    if method == "DELETE":
        return 204, []
    return 200, []
```

## Driver
```python
import sys

for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    req = dict(tok.split("=", 1) for tok in line.split())
    status, headers = decide(req)
    print(" ".join([str(status)] + list(headers)))
```

## Tests
=== sample
method=GET
method=POST allow=GET,POST
method=DELETE allow=GET,PUT
method=BREW
method=PUT allow=GET,PUT exists=0
method=GET auth=none
method=PATCH allow=PATCH ctype=xml
---
200 ETag
201 Location
405 Allow: GET, HEAD, OPTIONS, PUT
501
201 Location
401 WWW-Authenticate
415
=== hidden
method=BREW maint=1
method=GET allow=POST
method=OPTIONS allow=GET,DELETE
method=HEAD allow=GET
method=HEAD allow=POST
method=GET rate=1 auth=none
method=GET perm=0
method=GET auth=bad perm=0
method=GET accept=xml
method=POST allow=POST body=malformed
method=POST allow=POST body=invalid ctype=none
method=POST allow=POST body=invalid
method=GET accept=xml rate=1
---
503 Retry-After
405 Allow: OPTIONS, POST
204 Allow: DELETE, GET, HEAD, OPTIONS
200 ETag
405 Allow: OPTIONS, POST
429 Retry-After
403
401 WWW-Authenticate
406
400
415
422
429 Retry-After
=== hidden
method=PUT allow=PUT im=mismatch exists=0
method=PATCH allow=PATCH im=match
method=GET inm=match
method=GET inm=match exists=0
method=GET inm=nomatch
method=DELETE allow=DELETE exists=0
method=DELETE allow=DELETE conflict=1
method=PUT allow=PUT exists=0 conflict=1
method=OPTIONS allow=GET exists=0
method=GET upstream=bad
method=POST allow=POST upstream=timeout
method=GET conflict=1
method=PUT allow=PUT
method=GET im=mismatch
method=DELETE allow=DELETE im=mismatch body=malformed
---
412
200
304 ETag
404
200 ETag
404
409
409
204 Allow: GET, HEAD, OPTIONS
502
504
200 ETag
200
200 ETag
412
=== hidden
method=PATCH allow=DELETE,GET,PATCH,POST auth=ok ctype=json exists=0 upstream=bad
method=DELETE allow=GET,PUT maint=0 accept=json ctype=xml inm=nomatch conflict=0
method=TRACE allow=GET,HEAD,PATCH,POST rate=0 auth=ok perm=1 accept=json body=ok conflict=0
method=HEAD allow=DELETE,HEAD,PATCH ctype=none body=ok inm=none
method=DELETE allow=DELETE,GET maint=0 body=ok im=none upstream=timeout
method=DELETE allow=DELETE,PATCH,PUT accept=json body=invalid exists=1 conflict=0 upstream=ok
method=DELETE allow=DELETE,GET,PATCH rate=0 auth=ok accept=json body=ok exists=0 im=none conflict=1
method=PATCH allow=GET,PATCH,POST,PUT maint=0 auth=ok accept=json ctype=json body=invalid exists=1 im=mismatch conflict=0
method=GET allow=DELETE,GET,HEAD,PATCH im=none
method=POST allow=DELETE,HEAD,POST,PUT auth=ok exists=1 upstream=ok
method=GET allow=DELETE,GET maint=0 rate=0 perm=1 accept=xml body=invalid upstream=ok
method=OPTIONS allow=DELETE,PATCH,PUT rate=0 auth=ok accept=json ctype=json exists=1 inm=match im=match
method=PUT allow=DELETE,PUT maint=0 auth=none body=ok exists=0 inm=none upstream=ok
method=PUT allow=DELETE,PATCH,POST,PUT ctype=json exists=0 inm=match conflict=0 upstream=ok
method=GET allow=GET,HEAD,PATCH auth=bad perm=1 accept=json body=ok exists=0 inm=match im=mismatch upstream=ok
method=DELETE allow=DELETE,GET,HEAD,PATCH maint=1 perm=1 ctype=json inm=nomatch conflict=1
method=GET allow=GET,HEAD auth=ok accept=json ctype=none body=malformed exists=1 inm=match im=match upstream=timeout
method=PUT allow=DELETE maint=0 rate=0 accept=json inm=none im=none
method=DELETE allow=DELETE,GET,PATCH,PUT maint=0 rate=0 accept=json exists=1 inm=none
method=PATCH allow=DELETE,HEAD,PATCH,PUT maint=0 rate=0 perm=1 body=ok inm=none im=match
method=POST allow=DELETE,GET,POST,PUT perm=1 exists=1 inm=none upstream=ok
method=OPTIONS allow=DELETE,PATCH,POST,PUT maint=0 auth=bad body=ok exists=1 im=none conflict=1
method=HEAD allow=HEAD,PATCH,PUT auth=ok perm=1 ctype=json inm=none im=none conflict=1
method=GET allow=DELETE,PATCH,PUT maint=0 body=ok exists=1 upstream=timeout
method=POST allow=GET,POST,PUT maint=0 perm=1 accept=json exists=1 im=none
method=BREW allow=DELETE,POST maint=0 rate=0 auth=ok perm=1 ctype=json inm=none im=mismatch upstream=ok
method=DELETE allow=DELETE,GET,HEAD,PUT perm=1 im=match conflict=0
method=TRACE allow=DELETE,HEAD,POST,PUT rate=0 auth=none perm=1 inm=match
method=DELETE allow=DELETE,PATCH,PUT maint=0 auth=bad perm=0 accept=json ctype=none exists=1 im=match upstream=bad
method=GET allow=GET,POST accept=json exists=0 im=none conflict=0 upstream=timeout
---
404
405 Allow: GET, HEAD, OPTIONS, PUT
501
200 ETag
504
204
404
422
200 ETag
201 Location
406
204 Allow: DELETE, OPTIONS, PATCH, PUT
401 WWW-Authenticate
201 Location
401 WWW-Authenticate
503 Retry-After
304 ETag
405 Allow: DELETE, OPTIONS
204
200
201 Location
401 WWW-Authenticate
200 ETag
405 Allow: DELETE, OPTIONS, PATCH, PUT
201 Location
501
204
501
401 WWW-Authenticate
404
=== hidden
method=GET allow=GET maint=0 exists=1 upstream=ok
method=OPTIONS allow=DELETE,POST,PUT maint=0 rate=0 auth=ok exists=0 inm=nomatch conflict=0
method=OPTIONS allow=PATCH,POST maint=0 rate=0 auth=ok accept=json ctype=json body=invalid im=mismatch
method=GET allow=GET,PATCH maint=0 exists=0
method=BREW allow=POST rate=0 auth=none ctype=json im=match upstream=ok
method=POST allow=PATCH,POST maint=0 rate=0 accept=json ctype=json body=invalid inm=match conflict=1
method=PUT allow=HEAD,POST,PUT auth=none accept=json upstream=timeout
method=POST allow=DELETE,PATCH,POST rate=0 perm=1 accept=any ctype=xml exists=1 conflict=0 upstream=timeout
method=OPTIONS allow=DELETE,GET,HEAD auth=bad accept=any body=malformed exists=1 im=mismatch conflict=0
method=GET allow=GET,HEAD rate=0 accept=xml ctype=none body=ok im=mismatch conflict=0 upstream=ok
method=HEAD allow=DELETE,HEAD,POST,PUT perm=1 accept=json ctype=json body=ok exists=0 im=mismatch conflict=1 upstream=ok
method=PATCH allow=GET,HEAD,PATCH rate=0 perm=1 ctype=json body=ok exists=0 upstream=bad
method=PATCH allow=DELETE,GET,PATCH,PUT rate=0 perm=0 exists=1 conflict=0
method=PUT allow=GET,HEAD,PUT im=mismatch conflict=1
method=OPTIONS allow=DELETE perm=1 accept=xml body=ok im=match
method=DELETE allow=DELETE,GET,HEAD,PUT rate=0 auth=ok exists=1 inm=none upstream=timeout
method=TRACE allow=GET,HEAD,POST,PUT rate=0 auth=ok perm=1 exists=1 inm=nomatch
method=BREW allow=DELETE,GET,HEAD maint=0 auth=ok exists=1 inm=nomatch conflict=0
method=PUT allow=DELETE,GET,HEAD,PUT rate=0 auth=bad perm=1 accept=xml ctype=json body=ok
method=GET allow=GET,HEAD rate=0 accept=json exists=0 conflict=0 upstream=ok
method=TRACE allow=PATCH,PUT rate=0 auth=ok perm=1 accept=json ctype=xml upstream=ok
method=DELETE allow=DELETE,HEAD,PATCH,POST ctype=json body=ok exists=1 conflict=1 upstream=ok
method=POST allow=GET,HEAD,PATCH,PUT maint=0 perm=1 accept=json ctype=json im=mismatch
method=BREW allow=HEAD,POST perm=1 ctype=json exists=1 inm=none upstream=bad
method=POST allow=DELETE,PATCH maint=0 rate=0 perm=1 ctype=json exists=1 im=mismatch conflict=0 upstream=ok
method=POST allow=GET rate=0 auth=ok perm=0 ctype=json inm=nomatch upstream=timeout
method=DELETE allow=DELETE,GET,PATCH,POST,PUT maint=0 rate=0 perm=0 exists=0 inm=match upstream=ok
method=DELETE allow=DELETE maint=0 auth=ok perm=1 accept=json body=ok conflict=0
method=OPTIONS allow=DELETE,GET,HEAD,POST auth=ok perm=1 accept=json ctype=json exists=0 upstream=bad
method=TRACE allow=DELETE,HEAD,PATCH auth=ok perm=1 ctype=json body=malformed exists=1 inm=match
---
200 ETag
204 Allow: DELETE, OPTIONS, POST, PUT
204 Allow: OPTIONS, PATCH, POST
404
501
422
401 WWW-Authenticate
415
401 WWW-Authenticate
406
404
404
403
412
406
504
501
501
401 WWW-Authenticate
404
501
409
405 Allow: GET, HEAD, OPTIONS, PATCH, PUT
501
405 Allow: DELETE, OPTIONS, PATCH
405 Allow: GET, HEAD, OPTIONS
403
204
502
501
=== hidden
method=BREW allow=GET auth=bad ctype=none exists=0 inm=match
method=TRACE allow=PATCH,POST rate=0 auth=ok accept=json ctype=json inm=match im=none conflict=1 upstream=timeout
method=HEAD allow=HEAD,PATCH,POST,PUT accept=json ctype=none exists=1 im=mismatch upstream=ok
method=DELETE allow=DELETE,HEAD rate=0 perm=1 accept=any conflict=0
method=POST allow=DELETE,HEAD,PATCH,POST,PUT maint=0 auth=ok accept=any body=invalid inm=nomatch im=match
method=TRACE allow=GET,HEAD,PATCH,POST auth=ok perm=1 ctype=none body=invalid exists=1
method=TRACE allow=GET,PUT maint=0 im=none conflict=0
method=HEAD allow=POST rate=0 auth=bad ctype=json body=invalid conflict=0
method=DELETE allow=DELETE,HEAD accept=xml ctype=json conflict=0 upstream=bad
method=DELETE allow=GET,PATCH perm=1 inm=nomatch im=mismatch conflict=1
method=DELETE allow=DELETE,GET,PUT ctype=json exists=0 im=mismatch conflict=0
method=PUT allow=HEAD,POST,PUT accept=json exists=1
method=OPTIONS allow=DELETE,GET,PATCH,POST auth=ok inm=match im=match conflict=1
method=HEAD allow=DELETE,HEAD maint=0 body=malformed exists=1 conflict=0 upstream=ok
method=TRACE allow=DELETE,POST maint=0 accept=any ctype=none body=malformed exists=1 inm=match conflict=0
method=BREW allow=DELETE,HEAD,POST maint=1 rate=0 auth=ok accept=any ctype=json body=ok im=mismatch
method=OPTIONS allow=DELETE,POST maint=1 accept=any ctype=json im=match conflict=1
method=HEAD allow=DELETE,HEAD ctype=none inm=none im=match
method=GET allow=DELETE,GET,POST,PUT auth=ok conflict=0 upstream=ok
method=HEAD allow=DELETE,HEAD,POST,PUT rate=0 auth=ok perm=1 accept=json inm=none im=none upstream=ok
method=GET allow=DELETE,GET,HEAD,PATCH,PUT rate=0 accept=xml body=invalid upstream=ok
method=GET allow=GET,HEAD,PATCH body=ok exists=1 conflict=1 upstream=ok
method=POST allow=POST,PUT auth=none accept=xml body=malformed exists=0 conflict=0 upstream=ok
method=BREW allow=GET,HEAD,POST,PUT auth=ok perm=1 body=ok im=match conflict=1 upstream=ok
method=HEAD allow=HEAD,PATCH,PUT perm=1 body=ok exists=1 inm=none upstream=ok
method=GET allow=DELETE,GET,HEAD auth=ok accept=any body=ok exists=0 inm=none conflict=0
method=PUT allow=GET,HEAD,POST,PUT maint=0 rate=0 perm=1 accept=xml exists=1 inm=match im=match
method=DELETE allow=DELETE,POST maint=0 rate=0 accept=json inm=none im=match
method=HEAD allow=DELETE,GET,HEAD,PATCH,PUT maint=1 rate=0 auth=ok accept=json ctype=json exists=0 inm=nomatch im=match
method=DELETE allow=DELETE,GET,PATCH maint=0 accept=any ctype=json body=invalid exists=0 conflict=0 upstream=timeout
---
501
501
200 ETag
204
422
501
501
405 Allow: OPTIONS, POST
406
405 Allow: GET, HEAD, OPTIONS, PATCH
412
200
204 Allow: DELETE, GET, HEAD, OPTIONS, PATCH, POST
200 ETag
501
503 Retry-After
503 Retry-After
200 ETag
200 ETag
200 ETag
406
200 ETag
401 WWW-Authenticate
501
200 ETag
404
406
204
503 Retry-After
404
=== hidden
@gen 2642054186 big
=== hidden
@gen 2642054187 big
=== hidden
@gen 2642054188 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
n = 30 if sys.argv[2] == "small" else 400
methods = ["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "BREW", "TRACE"]
std = methods[:7]
for _ in range(n):
    f = {"method": r.choice(methods)}
    al = set(r.sample(std[:6], r.randint(1, 4)))
    if f["method"] in std[:6] and r.random() < 0.8:
        al.add(f["method"])
    f["allow"] = ",".join(sorted(al))
    opts = {"maint": ["0"] * 9 + ["1"], "rate": ["0"] * 6 + ["1"], "auth": ["ok"] * 6 + ["none", "bad"],
            "perm": ["1"] * 6 + ["0"], "accept": ["any", "json", "json", "xml"], "ctype": ["json"] * 4 + ["xml", "none"],
            "body": ["ok"] * 4 + ["malformed", "invalid"], "exists": ["1", "1", "0"], "inm": ["none", "match", "nomatch"],
            "im": ["none", "match", "mismatch"], "conflict": ["0", "0", "1"], "upstream": ["ok"] * 4 + ["bad", "timeout"]}
    for k, vals in opts.items():
        if r.random() < 0.45:
            f[k] = r.choice(vals)
    print(" ".join(f"{k}={v}" for k, v in f.items()))
```

## Hints
- Compute the effective allow set first: `set(allow.split(",")) | {"OPTIONS"}`, adding `HEAD` when `GET` is present.
- Write the checks as a straight sequence of `if … return`. The first match wins, so the order in the statement *is* the algorithm.
- Watch the special cases: `PUT` and `OPTIONS` don't 404 on a missing resource, and `304` needs both `inm=match` and an existing resource.

## Solution
The order is the whole point. Each step encodes *why* a status exists:

- **503 before everything:** a server in maintenance can't evaluate anything else. `Retry-After` tells well-behaved clients when to come back.
- **501 vs 405:** 501 means "this server doesn't know that method at all". 405 means "this resource doesn't support it", and the response **must** list what it does support in `Allow`.
- **401 vs 403:** 401 is about *identity* (no or bad credentials; `WWW-Authenticate` says how to authenticate). 403 is about *permission* (we know who you are, and the answer is no).
- **406 / 415 / 400 / 422:** content negotiation failed on the response side (406) or the request side (415). Then the body can't be parsed (400), or it parses but breaks business rules (422).
- **Preconditions** come before existence and conflict checks, so `If-Match` protects updates from lost writes (412), and `If-None-Match` lets caches skip a download (304).
- **PUT creates** at a client-chosen URL, so a missing resource isn't an error for it: the answer is 201.
- **5xx from upstream:** 502 means a backend gave a bad answer, and 504 means it didn't answer in time.

A `dict.get` with defaults keeps each check one line. Complexity: O(1) per request.

```python
STANDARD = {"GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"}
BODY_METHODS = {"POST", "PUT", "PATCH"}


def decide(req):
    g = lambda k, d: req.get(k, d)
    m = req["method"]
    allowed = set(g("allow", "GET").split(",")) | {"OPTIONS"}
    if "GET" in allowed:
        allowed.add("HEAD")
    allow_line = "Allow: " + ", ".join(sorted(allowed))
    exists = g("exists", "1") == "1"

    if g("maint", "0") == "1":
        return 503, ["Retry-After"]
    if m not in STANDARD:
        return 501, []
    if m not in allowed:
        return 405, [allow_line]
    if g("rate", "0") == "1":
        return 429, ["Retry-After"]
    if g("auth", "ok") != "ok":
        return 401, ["WWW-Authenticate"]
    if g("perm", "1") == "0":
        return 403, []
    if g("accept", "any") == "xml":
        return 406, []
    if m in BODY_METHODS:
        if g("ctype", "json") != "json":
            return 415, []
        if g("body", "ok") == "malformed":
            return 400, []
        if g("body", "ok") == "invalid":
            return 422, []
    if g("im", "none") == "mismatch" and m in {"PUT", "PATCH", "DELETE"}:
        return 412, []
    if g("inm", "none") == "match" and m in {"GET", "HEAD"} and exists:
        return 304, ["ETag"]
    if not exists and m not in {"PUT", "OPTIONS"}:
        return 404, []
    if g("conflict", "0") == "1" and m in {"POST", "PUT", "PATCH", "DELETE"}:
        return 409, []
    up = g("upstream", "ok")
    if up == "bad":
        return 502, []
    if up == "timeout":
        return 504, []
    if m in {"GET", "HEAD"}:
        return 200, ["ETag"]
    if m == "POST":
        return 201, ["Location"]
    if m == "PUT":
        return (200, []) if exists else (201, ["Location"])
    if m == "PATCH":
        return 200, []
    if m == "DELETE":
        return 204, []
    return 204, [allow_line]
```
