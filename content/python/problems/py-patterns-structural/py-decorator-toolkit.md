---
id: py-decorator-toolkit
title: A Production Decorator Toolkit
difficulty: Hard
order: 1
tags: decorators, closures, functools.wraps, caching, rate limiting, retries, type hints
time_limit: 5
---
## Statement
Write four reusable decorators for a robot's service layer. Time and sleeping are **injected**, so the judge controls them. All decorators must preserve the wrapped function's metadata (`__name__`, `__doc__`, `__wrapped__`).

**1. `retry(times, exceptions=(Exception,), backoff=0.1, sleep=time.sleep)`**
- Call up to `times` attempts. On an exception of one of the listed types, `sleep(backoff * 2**k)` before attempt `k + 2`, and re-raise the last exception when the attempts run out.
- Other exceptions propagate immediately.
- `times < 1` raises `ValueError` **at decoration time**.

**2. `ttl_cache(seconds, clock=time.monotonic)`**
- Caches results keyed by the positional arguments plus the keyword arguments, so `f(1, b=2)` and `f(1, b=2)` share an entry, regardless of keyword order.
- An entry is valid while `clock() - stored_at < seconds`. After that it's recomputed.
- Calls with **unhashable** arguments bypass the cache entirely and aren't counted.
- Adds `wrapper.cache_info()` → `(hits, misses, current_size)` (expired entries still count until replaced or cleared) and `wrapper.cache_clear()`, which empties the cache and resets the counts.

**3. `rate_limit(calls, period, clock=time.monotonic)`**
- Allows at most `calls` successful invocations in any window of length `period`. A call is allowed if fewer than `calls` earlier allowed calls happened at times `t` with `now - t < period`.
- A rejected call raises `RateLimitExceeded` (define it, subclassing `RuntimeError`), doesn't call the function, and doesn't use up quota.

**4. `typed`** checks annotated arguments and the annotated return value at call time:
- Supported annotations: `int`, `float`, `str`, `bool`, `list`, `dict`, and `X | None` unions of those. Others aren't checked.
- `float` accepts `int`, but `int`/`float` never accept `bool`.
- Defaults are checked too (after binding, with defaults applied).
- An argument failure raises `TypeError("<fname>: argument '<p>' must be <ann>, got <type>")`, and a return failure raises `TypeError("<fname>: return value must be <ann>, got <type>")`.
- `<ann>` is the annotation's name (`int`), or the union written as `int | None`. `<type>` is `type(value).__name__`.

## Starter
```python
import functools
import time


class RateLimitExceeded(RuntimeError):
    pass


def retry(times, exceptions=(Exception,), backoff=0.1, sleep=time.sleep):
    def deco(fn):
        def wrapper(*args, **kwargs):
            for _ in range(times):
                try:
                    return fn(*args, **kwargs)
                except exceptions:
                    pass
        return wrapper
    return deco


def ttl_cache(seconds, clock=time.monotonic):
    def deco(fn):
        return functools.lru_cache(maxsize=None)(fn)
    return deco


def rate_limit(calls, period, clock=time.monotonic):
    def deco(fn):
        return fn
    return deco


def typed(fn):
    return fn
```

## Driver
```python
import sys

class Clock:
    def __init__(self): self.t = 0.0
    def __call__(self): return self.t

def attempt(label, fn):
    try:
        print(f"{label}: {fn()!r}")
    except Exception as e:
        print(f"{label}: {type(e).__name__}: {e}")

for cmd in sys.stdin.read().split():
    if cmd == "retry":
        sleeps, calls = [], []
        @retry(4, exceptions=(ConnectionError, TimeoutError), backoff=0.5, sleep=sleeps.append)
        def flaky(n):
            "Fetch something."
            calls.append(n)
            if len(calls) < 3:
                raise ConnectionError("down")
            return n * 10
        attempt("flaky", lambda: flaky(4)); print("sleeps", sleeps, "calls", len(calls), flaky.__name__, flaky.__doc__, flaky.__wrapped__.__name__)
        sleeps.clear(); calls.clear()
        @retry(3, exceptions=(ConnectionError,), backoff=1, sleep=sleeps.append)
        def dead():
            calls.append(1); raise ConnectionError(f"attempt {len(calls)}")
        attempt("dead", dead); print("sleeps", sleeps)
        @retry(5, exceptions=(ConnectionError,), sleep=sleeps.append)
        def wrong():
            raise ValueError("not retried")
        sleeps.clear(); attempt("wrong", wrong); print("sleeps", sleeps)
        attempt("times=0", lambda: retry(0))
    elif cmd == "cache":
        clk = Clock(); log = []
        @ttl_cache(10, clock=clk)
        def plan(start, goal=None, *, speed=1.0):
            "Plan a path."
            log.append((start, goal, speed)); return f"{start}->{goal}@{speed}"
        attempt("a", lambda: plan("A", "B"))
        attempt("a again", lambda: plan("A", "B"))
        attempt("kw", lambda: plan("A", goal="B"))
        attempt("kw order 1", lambda: plan("A", goal="C", speed=2))
        attempt("kw order 2", lambda: plan("A", speed=2, goal="C"))
        clk.t = 9.99; attempt("still fresh", lambda: plan("A", "B"))
        clk.t = 10.0; attempt("expired", lambda: plan("A", "B"))
        attempt("unhashable", lambda: plan(["A"], "B"))
        attempt("unhashable again", lambda: plan(["A"], "B"))
        print("info", plan.cache_info(), "calls", len(log), plan.__name__, plan.__doc__)
        plan.cache_clear(); print("cleared", plan.cache_info()); plan("A", "B"); print("after", plan.cache_info())
    elif cmd == "rate":
        clk = Clock(); hits = []
        @rate_limit(3, 1.0, clock=clk)
        def send(cmd):
            "Send a command."
            hits.append(cmd); return f"sent {cmd}"
        out = []
        for t, c in [(0.0, "a"), (0.1, "b"), (0.2, "c"), (0.5, "d"), (0.99, "e"), (1.0, "f"), (1.05, "g"), (1.15, "h"), (1.2, "i"), (2.5, "j")]:
            clk.t = t
            try:
                out.append(send(c))
            except RateLimitExceeded:
                out.append(f"limited {c}")
        print(out); print("hits", hits, send.__name__, send.__doc__, isinstance(RateLimitExceeded(), RuntimeError))
    elif cmd == "typed":
        @typed
        def move(joint: int, angle: float, label: str = "j", tags: list | None = None, fast: bool = False) -> float:
            "Move a joint."
            return angle * 2 if joint >= 0 else "oops"
        attempt("ok", lambda: move(1, 0.5))
        attempt("int as float", lambda: move(1, 2))
        attempt("bool joint", lambda: move(True, 0.5))
        attempt("str angle", lambda: move(1, "0.5"))
        attempt("bool angle", lambda: move(1, False))
        attempt("label", lambda: move(1, 0.5, label=7))
        attempt("tags none", lambda: move(1, 0.5, tags=None))
        attempt("tags list", lambda: move(1, 0.5, tags=["x"]))
        attempt("tags tuple", lambda: move(1, 0.5, tags=("x",)))
        attempt("fast", lambda: move(1, 0.5, fast=1))
        attempt("return", lambda: move(-1, 0.5))
        attempt("missing arg", lambda: move(1))
        print(move.__name__, move.__doc__)
        @typed
        def bad_default(x: int = "zero", y=None) -> None:
            return None
        attempt("bad default", bad_default)
        attempt("good", lambda: bad_default(3, y=[1]))
        @typed
        def any_obj(x: object, d: dict) -> dict | None:
            return d or None
        attempt("dict", lambda: any_obj(1, {}))
        attempt("dict bad", lambda: any_obj(1, []))
    elif cmd == "stack":
        clk = Clock(); sleeps = []; n = {"calls": 0}
        @ttl_cache(5, clock=clk)
        @retry(3, exceptions=(IOError,), backoff=0.25, sleep=sleeps.append)
        @typed
        def read(sensor: str, scale: float = 1.0) -> float:
            "Read a sensor."
            n["calls"] += 1
            if n["calls"] == 1:
                raise IOError("glitch")
            return 1.5 * scale
        attempt("read", lambda: read("imu", scale=2))
        attempt("cached", lambda: read("imu", scale=2))
        attempt("type error", lambda: read(5))
        print("calls", n["calls"], "sleeps", sleeps, read.__name__, read.__doc__, read.cache_info())
```

## Tests
=== sample
retry
cache
---
flaky: 40
sleeps [0.5, 1.0] calls 3 flaky Fetch something. flaky
dead: ConnectionError: attempt 3
sleeps [1, 2]
wrong: ValueError: not retried
sleeps []
times=0: ValueError: times must be >= 1
a: 'A->B@1.0'
a again: 'A->B@1.0'
kw: 'A->B@1.0'
kw order 1: 'A->C@2'
kw order 2: 'A->C@2'
still fresh: 'A->B@1.0'
expired: 'A->B@1.0'
unhashable: "['A']->B@1.0"
unhashable again: "['A']->B@1.0"
info (3, 4, 3) calls 6 plan Plan a path.
cleared (0, 0, 0)
after (0, 1, 1)
=== hidden
rate
---
['sent a', 'sent b', 'sent c', 'limited d', 'limited e', 'sent f', 'limited g', 'sent h', 'sent i', 'sent j']
hits ['a', 'b', 'c', 'f', 'h', 'i', 'j'] send Send a command. True
=== hidden
typed
---
ok: 1.0
int as float: 4
bool joint: TypeError: move: argument 'joint' must be int, got bool
str angle: TypeError: move: argument 'angle' must be float, got str
bool angle: TypeError: move: argument 'angle' must be float, got bool
label: TypeError: move: argument 'label' must be str, got int
tags none: 1.0
tags list: 1.0
tags tuple: TypeError: move: argument 'tags' must be list | None, got tuple
fast: TypeError: move: argument 'fast' must be bool, got int
return: TypeError: move: return value must be float, got str
missing arg: TypeError: missing a required argument: 'angle'
move Move a joint.
bad default: TypeError: bad_default: argument 'x' must be int, got str
good: None
dict: None
dict bad: TypeError: any_obj: argument 'd' must be dict, got list
=== hidden
stack
---
read: 3.0
cached: 3.0
type error: TypeError: read: argument 'sensor' must be str, got int
calls 2 sleeps [0.25] read Read a sensor. (1, 2, 1)

## Hints
- The three-layer shape: `def retry(...): def decorator(fn): @functools.wraps(fn) def wrapper(*a, **kw): ...`. Validate `times` in the outer function.
- Cache key: `(args, tuple(sorted(kwargs.items())))`. Computing `hash(key)` raises `TypeError` for unhashable parts, so catch it and call through.
- Rate limit: keep a `collections.deque` of allowed timestamps. Pop from the left while `now - dq[0] >= period`.
- `typed`: `typing.get_type_hints(fn)` resolves annotations. `inspect.signature(fn).bind(*a, **kw)` followed by `.apply_defaults()` gives every argument value. A union `int | None` is a `types.UnionType`, and `typing.get_args` gives its members.
- Function attributes: `wrapper.cache_info = ...` works because functions are objects.

## Solution
```python
import collections
import functools
import inspect
import time
import types
import typing


class RateLimitExceeded(RuntimeError):
    pass


def retry(times, exceptions=(Exception,), backoff=0.1, sleep=time.sleep):
    if times < 1:
        raise ValueError("times must be >= 1")
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(times):
                try:
                    return fn(*args, **kwargs)
                except exceptions:
                    if attempt == times - 1:
                        raise
                    sleep(backoff * 2 ** attempt)
        return wrapper
    return decorator


def ttl_cache(seconds, clock=time.monotonic):
    def decorator(fn):
        store = {}
        stats = {"hits": 0, "misses": 0}

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            try:
                hash(key)
            except TypeError:
                return fn(*args, **kwargs)                   # unhashable: bypass the cache
            now = clock()
            entry = store.get(key)
            if entry is not None and now - entry[1] < seconds:
                stats["hits"] += 1
                return entry[0]
            stats["misses"] += 1
            value = fn(*args, **kwargs)
            store[key] = (value, now)
            return value

        def cache_info():
            return (stats["hits"], stats["misses"], len(store))

        def cache_clear():
            store.clear()
            stats.update(hits=0, misses=0)

        wrapper.cache_info = cache_info
        wrapper.cache_clear = cache_clear
        return wrapper
    return decorator


def rate_limit(calls, period, clock=time.monotonic):
    def decorator(fn):
        allowed = collections.deque()

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            now = clock()
            while allowed and now - allowed[0] >= period:
                allowed.popleft()
            if len(allowed) >= calls:
                raise RateLimitExceeded(f"{fn.__name__}: more than {calls} calls per {period}s")
            allowed.append(now)
            return fn(*args, **kwargs)
        return wrapper
    return decorator


_SIMPLE = (int, float, str, bool, list, dict)


def _members(ann):
    """Return the tuple of allowed types, or None if the annotation is not checked."""
    if ann in _SIMPLE:
        return (ann,)
    if isinstance(ann, types.UnionType) or typing.get_origin(ann) is typing.Union:
        args = typing.get_args(ann)
        if all(a in _SIMPLE or a is type(None) for a in args):
            return args
    return None


def _matches(value, allowed):
    for t in allowed:
        if t is type(None):
            if value is None:
                return True
        elif t in (int, float):
            if isinstance(value, bool):
                continue
            if isinstance(value, int) or (t is float and isinstance(value, float)):
                return True
        elif isinstance(value, t):
            return True
    return False


def _ann_name(allowed):
    return " | ".join("None" if t is type(None) else t.__name__ for t in allowed)


def typed(fn):
    hints = typing.get_type_hints(fn)
    sig = inspect.signature(fn)
    checks = {name: m for name, ann in hints.items() if (m := _members(ann)) is not None}

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        for name, value in bound.arguments.items():
            allowed = checks.get(name)
            if allowed is not None and not _matches(value, allowed):
                raise TypeError(f"{fn.__name__}: argument '{name}' must be {_ann_name(allowed)}, "
                                f"got {type(value).__name__}")
        result = fn(*bound.args, **bound.kwargs)
        allowed = checks.get("return")
        if allowed is not None and not _matches(result, allowed):
            raise TypeError(f"{fn.__name__}: return value must be {_ann_name(allowed)}, got {type(result).__name__}")
        return result
    return wrapper
```

- **Three layers**: the factory (options, validated once at decoration time), the decorator (receives `fn`, sets up per-function state like the cache dict or deque), and the wrapper (runs per call). State lives in closures, so each decorated function gets its own.
- **`functools.wraps`** copies the name and docstring and sets `__wrapped__`, so stacked decorators, debuggers, pytest and documentation tools still see the real function. The stack test checks that metadata survives three layers.
- **Injected `clock` and `sleep`** make TTL expiry, sliding windows and backoff fully deterministic to test, which is exactly the clean-architecture idea applied to tiny utilities.
- **Sliding-window rate limiting** with a deque of timestamps is O(1) amortised. Rejected calls don't consume quota, so a client that backs off recovers.
- **Runtime type checks** resolve annotations with `get_type_hints`, bind arguments the way Python itself does (defaults included), and handle the classic trap: `bool` is a subclass of `int`. Libraries like pydantic's `validate_call` and beartype do this at production scale.
