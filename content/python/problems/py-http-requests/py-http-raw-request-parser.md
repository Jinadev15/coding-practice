---
id: py-http-raw-request-parser
title: Raw HTTP/1.1 Request Parser
difficulty: Easy
order: 2
tags: HTTP, request anatomy, CRLF, headers, Content-Length, request smuggling, parsing
time_limit: 2
---
## Statement
Every web framework starts by turning **bytes from a socket** into a request object. Write that parser.

```python
class BadRequest(Exception):
    def __init__(self, reason: str): ...        # keep .reason

@dataclass
class Request:
    method: str
    path: str                     # the target before '?', NOT percent-decoded
    query: list[tuple[str, str]]  # decoded pairs in order ('+' is a space, blank values kept)
    version: str                  # "HTTP/1.0" or "HTTP/1.1"
    headers: dict[str, str]       # lower-cased names
    body: bytes
    consumed: int                 # bytes of `raw` that belong to this request

def parse_request(raw: bytes) -> Request: ...
```

`raw` holds one request, possibly followed by the start of the next one (pipelining). Decode the head as latin-1. Apply these checks **in this order** and raise `BadRequest` with the exact reason of the first one that fails:

| # | Rule | Reason |
|---|---|---|
| 1 | The head ends at the first `\r\n\r\n`. If there isn't one, the request is not complete yet. | `incomplete headers` |
| 2 | The request line is exactly three parts separated by **single** spaces. | `bad request line` |
| 3 | The method is one or more uppercase letters `A–Z`. | `bad method` |
| 4 | The target starts with `/`. | `bad target` |
| 5 | The version is `HTTP/1.0` or `HTTP/1.1`. | `bad version` |
| 6 | Every header line is `name:value`. The name is non-empty and contains no space or tab (so `Host :x` is invalid). The value is stripped of surrounding spaces and tabs. | `bad header` |
| 7 | An `HTTP/1.1` request has a `Host` header. | `missing host` |
| 8 | `Content-Length`, if present, is all digits. If it appears several times, every copy must be identical (different copies are a classic request-smuggling trick). | `bad content-length` |
| 9 | At least `Content-Length` bytes follow the head. | `incomplete body` |

Header names are case-insensitive, so store them lower-cased. A header that repeats (other than a valid repeated `Content-Length`) is joined with `", "` in arrival order. With no `Content-Length`, the body is empty. `consumed` = length of the head including the blank line, plus the body length. Anything after that belongs to the next request.

**Input / output (handled by the driver):** each line is one raw request written as a Python string literal body (`\r\n` escapes etc.). For each, the driver prints either `400 <reason>`, or the parsed fields:
```
GET /search | q=http basics&page=2 | HTTP/1.1 | accept=*/*;host=example.com | b'' | 77
```
(query pairs joined by `&`, headers sorted by name, body as a bytes repr, then `consumed`).

## Starter
```python
from dataclasses import dataclass, field


class BadRequest(Exception):
    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


@dataclass
class Request:
    method: str
    path: str
    query: list
    version: str
    headers: dict
    body: bytes
    consumed: int


def parse_request(raw: bytes) -> Request:
    # TODO: split the head from the body, validate in the order given, build the Request
    raise BadRequest("not implemented")
```

## Driver
```python
import codecs
import sys

for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    raw = codecs.decode(line, "unicode_escape").encode("latin-1")
    try:
        r = parse_request(raw)
    except BadRequest as e:
        print("400", e.reason)
        continue
    q = "&".join(f"{k}={v}" for k, v in r.query)
    h = ";".join(f"{k}={v}" for k, v in sorted(r.headers.items()))
    print(f"{r.method} {r.path} | {q} | {r.version} | {h} | {r.body!r} | {r.consumed}")
```

## Tests
=== sample
GET /search?q=http+basics&page=2 HTTP/1.1\r\nHost: example.com\r\nAccept: */*\r\n\r\n
POST /api/items HTTP/1.1\r\nHost: api.test\r\nContent-Type: application/json\r\nContent-Length: 14\r\n\r\n{"name":"pen"}
GET /a HTTP/1.1\r\nHost: x\r\n
---
GET /search | q=http basics&page=2 | HTTP/1.1 | accept=*/*;host=example.com | b'' | 77
POST /api/items |  | HTTP/1.1 | content-length=14;content-type=application/json;host=api.test | b'{"name":"pen"}' | 110
400 incomplete headers
=== hidden
GET /  HTTP/1.1\r\nHost: x\r\n\r\n
get / HTTP/1.1\r\nHost: x\r\n\r\n
GET index.html HTTP/1.1\r\nHost: x\r\n\r\n
GET / HTTP/2.0\r\nHost: x\r\n\r\n
GET / HTTP/1.1\r\nHost :x\r\n\r\n
GET / HTTP/1.1\r\nNoColonHere\r\n\r\n
GET / HTTP/1.1\r\n: empty\r\n\r\n
GET / HTTP/1.1\r\nAccept: text/html\r\n\r\n
---
400 bad request line
400 bad method
400 bad target
400 bad version
400 bad header
400 bad header
400 bad header
400 missing host
=== hidden
GET /old HTTP/1.0\r\n\r\n
POST /p HTTP/1.1\r\nHost: x\r\nContent-Length: -3\r\n\r\n
POST /p HTTP/1.1\r\nHost: x\r\nContent-Length: 5\r\nContent-Length: 6\r\n\r\nhello!
POST /p HTTP/1.1\r\nHost: x\r\nContent-Length: 5\r\ncontent-length: 5\r\n\r\nhello
POST /p HTTP/1.1\r\nHost: x\r\nContent-Length: 10\r\n\r\nshort
---
GET /old |  | HTTP/1.0 |  | b'' | 21
400 bad content-length
400 bad content-length
POST /p |  | HTTP/1.1 | content-length=5;host=x | b'hello' | 72
400 incomplete body
=== hidden
POST /p HTTP/1.1\r\nHost: x\r\nContent-Length: 2\r\n\r\nhiGET /next HTTP/1.1\r\nHost: x\r\n\r\n
GET /f?a=1&a=2&empty=&sp=a%20b%2Bc&k HTTP/1.1\r\nHost: shop.example:8080\r\nCookie: a=1\r\nCookie: b=2\r\nX-Trace:   abc \t\r\n\r\n
DELETE /items/7 HTTP/1.1\r\nHOST: X\r\nAuthorization: Bearer t0k3n\r\n\r\n
GET /x?a=%41%42 HTTP/1.1\r\nHost: x\r\nContent-Length: 0\r\n\r\n
GET / HTTP/1.1 extra\r\nHost: x\r\n\r\n
PATCH /p HTTP/1.1\r\nHost: x\r\nContent-Length: 1x\r\n\r\nab
GET /\r\n\r\n
---
POST /p |  | HTTP/1.1 | content-length=2;host=x | b'hi' | 50
GET /f | a=1&a=2&empty=&sp=a b+c&k= | HTTP/1.1 | cookie=a=1, b=2;host=shop.example:8080;x-trace=abc | b'' | 118
DELETE /items/7 |  | HTTP/1.1 | authorization=Bearer t0k3n;host=X | b'' | 66
GET /x | a=AB | HTTP/1.1 | content-length=0;host=x | b'' | 56
400 bad request line
400 bad content-length
400 bad request line

## Hints
- `raw.find(b"\r\n\r\n")` gives the end of the head. Decode only the head, and keep the body as bytes.
- `line.partition(":")` splits at the first colon. Check the name for spaces *before* lower-casing and stripping.
- `urllib.parse.parse_qsl(qs, keep_blank_values=True)` decodes the query. `consumed` is `end + 4 + content_length`.

## Solution
**Find the boundary first.** The head (request line plus headers) always ends with an empty line, so the first `\r\n\r\n` splits head from body. If it isn't there yet, a real server would keep reading from the socket. That is why the first error is "incomplete", not "bad".

**Validate from the outside in.** The request line is checked part by part with exact rules (`split(" ")` keeps empty parts, so a double space becomes an empty string and fails rule 2). Each header line is split at the first colon only, because values like `Host: example.com:8080` contain colons themselves.

**The body is framed by `Content-Length`.** HTTP/1.1 runs many requests over one connection, so the server must know exactly where this request stops. `consumed = head + 4 + length` tells the caller where the next pipelined request begins. Conflicting `Content-Length` values are rejected because a proxy and a server that pick different copies disagree about where requests end. That's HTTP request smuggling.

**Query strings** use `application/x-www-form-urlencoded` rules: `parse_qsl(qs, keep_blank_values=True)` decodes `%XX`, turns `+` into a space, and keeps `flag=` pairs.

Complexity: O(n) in the size of the request.

```python
import re
from dataclasses import dataclass
from urllib.parse import parse_qsl


class BadRequest(Exception):
    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


@dataclass
class Request:
    method: str
    path: str
    query: list
    version: str
    headers: dict
    body: bytes
    consumed: int


def parse_request(raw: bytes) -> Request:
    end = raw.find(b"\r\n\r\n")
    if end < 0:
        raise BadRequest("incomplete headers")
    head = raw[:end].decode("latin-1")
    lines = head.split("\r\n")

    parts = lines[0].split(" ")
    if len(parts) != 3 or not all(parts):
        raise BadRequest("bad request line")
    method, target, version = parts
    if not re.fullmatch(r"[A-Z]+", method):
        raise BadRequest("bad method")
    if not target.startswith("/"):
        raise BadRequest("bad target")
    if version not in ("HTTP/1.0", "HTTP/1.1"):
        raise BadRequest("bad version")

    headers: dict[str, str] = {}
    lengths: list[str] = []
    for line in lines[1:]:
        name, sep, value = line.partition(":")
        if not sep or not name or " " in name or "\t" in name:
            raise BadRequest("bad header")
        name, value = name.lower(), value.strip(" \t")
        if name == "content-length":
            lengths.append(value)
            headers[name] = value
        elif name in headers:
            headers[name] += ", " + value
        else:
            headers[name] = value

    if version == "HTTP/1.1" and "host" not in headers:
        raise BadRequest("missing host")
    length = 0
    if lengths:
        if not all(v.isdigit() and v.isascii() for v in lengths) or len(set(lengths)) != 1:
            raise BadRequest("bad content-length")
        length = int(lengths[0])
    start = end + 4
    if len(raw) - start < length:
        raise BadRequest("incomplete body")

    path, _, qs = target.partition("?")
    return Request(method, path, parse_qsl(qs, keep_blank_values=True), version, headers,
                   raw[start:start + length], start + length)
```
