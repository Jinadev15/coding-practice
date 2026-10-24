---
id: py-m2-ttl-cache
title: Thread-Safe LRU Cache with TTL and a Decorator
difficulty: Hard
order: 1
tags: OrderedDict, decorators, threading, data model, design
time_limit: 3
---
## Statement
Build a production-quality cache component:

```python
class TTLCache:
    def __init__(self, maxsize: int, ttl: float, clock=time.monotonic)
    def get(self, key, default=None)        # a miss if absent OR expired (expired entries are removed); a hit refreshes LRU order
    def set(self, key, value)               # insert/overwrite (resets the expiry); evict the least-recently-used if over maxsize
    def __contains__(self, key) -> bool     # True only for live (non-expired) keys; doesn't count as a hit or miss, and doesn't change LRU order
    def __len__(self) -> int                # number of LIVE entries (purge expired ones first)
    def purge(self) -> int                  # remove all expired entries, return how many
    def stats(self) -> dict                 # {"hits", "misses", "evictions", "expirations"}
    # thread-safe: all operations hold one internal lock

def cached(maxsize=128, ttl=60.0, clock=time.monotonic):
    # decorator factory: memoizes a function with a TTLCache keyed by (args, sorted kwargs);
    # exposes wrapper.cache (the TTLCache) and wrapper.cache_clear(); preserves metadata with functools.wraps
```

Details:
- An entry is expired when `clock() >= expiry`. Every expired entry removed for any reason counts as one **expiration**. Entries removed to make room count as **evictions**.
- `get` on an expired key is a miss (and an expiration).
- The decorator caches only successful results: exceptions propagate and aren't cached.

The driver uses a **fake clock** it controls, a script of operations, and a multi-threaded stress test.

## Starter
```python
import time
import functools
import threading
from collections import OrderedDict

class TTLCache:
    def __init__(self, maxsize, ttl, clock=time.monotonic):
        self.data = {}
    def get(self, key, default=None):
        return self.data.get(key, default)
    def set(self, key, value):
        self.data[key] = value

def cached(maxsize=128, ttl=60.0, clock=time.monotonic):
    def deco(f):
        return f
    return deco
```

## Driver
```python
import sys

class FakeClock:
    def __init__(self): self.t = 0.0
    def __call__(self): return self.t

clock = FakeClock()
calls = []

@cached(maxsize=3, ttl=10, clock=clock)
def slow_square(x, *, scale=1):
    """Square x (slowly)."""
    calls.append(x)
    if x < 0:
        raise ValueError("negative")
    return x * x * scale

def stress():
    c = TTLCache(maxsize=50, ttl=1e9)
    def worker(k):
        for i in range(3000):
            key = (k * 7 + i) % 80
            if c.get(key) is None:
                c.set(key, key * 2)
    ts = [threading.Thread(target=worker, args=(k,)) for k in range(8)]
    for t in ts: t.start()
    for t in ts: t.join()
    s = c.stats()
    print("stress: size<=50", len(c) <= 50, "| hits+misses=", s["hits"] + s["misses"], "| values ok", all(c.get(k, k * 2) == k * 2 for k in range(80)))

cache = TTLCache(maxsize=2, ttl=5, clock=clock)
for line in sys.stdin.read().splitlines():
    p = line.split()
    if not p:
        continue
    cmd = p[0]
    if cmd == "tick": clock.t += float(p[1]); print("t =", clock.t)
    elif cmd == "set": cache.set(p[1], p[2]); print("set", p[1])
    elif cmd == "get": print("get", p[1], "->", cache.get(p[1], "MISS"))
    elif cmd == "has": print("has", p[1], "->", p[1] in cache)
    elif cmd == "len": print("len ->", len(cache))
    elif cmd == "purge": print("purged", cache.purge())
    elif cmd == "stats": print("stats", cache.stats())
    elif cmd == "sq":
        try:
            print("sq", p[1], "->", slow_square(int(p[1]), scale=int(p[2]) if len(p) > 2 else 1), "calls", len(calls))
        except ValueError as e:
            print("sq", p[1], "-> error", e, "calls", len(calls))
    elif cmd == "sqstats": print("sq stats", slow_square.cache.stats(), slow_square.__name__, slow_square.__doc__)
    elif cmd == "sqclear": slow_square.cache_clear(); print("cleared")
    elif cmd == "stress": stress()
```

## Tests
=== sample
set a 1
set b 2
get a
set c 3
get b
has a
tick 4
get a
tick 1
get a
get c
len
stats
sq 3
sq 3
sq 3 2
sq -1
sq -1
tick 10
sq 3
sqstats
---
set a
set b
get a -> 1
set c
get b -> MISS
has a -> True
t = 4.0
get a -> 1
t = 5.0
get a -> MISS
get c -> MISS
len -> 0
stats {'hits': 2, 'misses': 3, 'evictions': 1, 'expirations': 2}
sq 3 -> 9 calls 1
sq 3 -> 9 calls 1
sq 3 -> 18 calls 2
sq -1 -> error negative calls 3
sq -1 -> error negative calls 4
t = 15.0
sq 3 -> 9 calls 5
sq stats {'hits': 1, 'misses': 5, 'evictions': 0, 'expirations': 1} slow_square Square x (slowly).
=== hidden
set k v
set k w
get k
tick 4.9
has k
tick 0.1
has k
len
purge
stats
set x 1
set y 2
set z 3
get x
get y
get z
tick 100
purge
stats
sq 1
sq 2
sq 3
sq 4
sq 1
sqstats
sqclear
sq 4
sqstats
stress
---
set k
set k
get k -> w
t = 4.9
has k -> True
t = 5.0
has k -> False
len -> 0
purged 0
stats {'hits': 1, 'misses': 0, 'evictions': 0, 'expirations': 1}
set x
set y
set z
get x -> MISS
get y -> 2
get z -> 3
t = 105.0
purged 2
stats {'hits': 3, 'misses': 1, 'evictions': 1, 'expirations': 3}
sq 1 -> 1 calls 1
sq 2 -> 4 calls 2
sq 3 -> 9 calls 3
sq 4 -> 16 calls 4
sq 1 -> 1 calls 5
sq stats {'hits': 0, 'misses': 5, 'evictions': 2, 'expirations': 0} slow_square Square x (slowly).
cleared
sq 4 -> 16 calls 6
sq stats {'hits': 0, 'misses': 6, 'evictions': 2, 'expirations': 0} slow_square Square x (slowly).
stress: size<=50 True | hits+misses= 24000 | values ok True

## Hints
- Store `key -> (expiry, value)` in an `OrderedDict`. `move_to_end(key)` on a hit and `popitem(last=False)` to evict the LRU entry.
- Write `_expired(key)` / `_purge_expired()` helpers that assume the lock is held. Use one `threading.RLock` (or `Lock`) and `with self._lock:` in every public method.
- The decorator's key is `(args, tuple(sorted(kwargs.items())))`, with a sentinel object to distinguish "missing" from a cached `None`.
- `functools.wraps(func)` preserves `__name__` and `__doc__`.

## Solution
```python
import time
import functools
import threading
from collections import OrderedDict

class TTLCache:
    _MISSING = object()

    def __init__(self, maxsize, ttl, clock=time.monotonic):
        self.maxsize, self.ttl, self.clock = maxsize, ttl, clock
        self._data = OrderedDict()                      # key -> (expiry, value); oldest first
        self._lock = threading.RLock()
        self._stats = {"hits": 0, "misses": 0, "evictions": 0, "expirations": 0}

    def _alive(self, key, now):                         # caller holds the lock
        entry = self._data.get(key)
        if entry is None:
            return False
        if now >= entry[0]:
            del self._data[key]
            self._stats["expirations"] += 1
            return False
        return True

    def get(self, key, default=None):
        with self._lock:
            if self._alive(key, self.clock()):
                self._data.move_to_end(key)             # most recently used
                self._stats["hits"] += 1
                return self._data[key][1]
            self._stats["misses"] += 1
            return default

    def set(self, key, value):
        with self._lock:
            self._data[key] = (self.clock() + self.ttl, value)
            self._data.move_to_end(key)
            while len(self._data) > self.maxsize:
                self._data.popitem(last=False)          # evict least recently used
                self._stats["evictions"] += 1

    def __contains__(self, key):
        with self._lock:
            return self._alive(key, self.clock())

    def purge(self):
        with self._lock:
            now = self.clock()
            dead = [k for k, (exp, _) in self._data.items() if now >= exp]
            for k in dead:
                del self._data[k]
            self._stats["expirations"] += len(dead)
            return len(dead)

    def __len__(self):
        with self._lock:
            self.purge()
            return len(self._data)

    def stats(self):
        with self._lock:
            return dict(self._stats)

    def clear(self):
        with self._lock:
            self._data.clear()


def cached(maxsize=128, ttl=60.0, clock=time.monotonic):
    def deco(func):
        cache = TTLCache(maxsize, ttl, clock)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            hit = cache.get(key, TTLCache._MISSING)
            if hit is not TTLCache._MISSING:
                return hit
            result = func(*args, **kwargs)              # exceptions propagate and aren't cached
            cache.set(key, result)
            return result

        wrapper.cache = cache
        wrapper.cache_clear = cache.clear
        return wrapper
    return deco
```

**Milestone review:**
- **Data structures (modules 2, 8):** an `OrderedDict` gives O(1) LRU operations (`move_to_end`, `popitem(last=False)`), exactly like the hash map + doubly linked list from interviews.
- **The data model (module 9):** `__contains__` and `__len__` make the cache feel like a built-in container.
- **Decorators and closures (modules 3, 9):** a decorator factory with configuration, `functools.wraps`, and attributes attached to the wrapper, the same shape as `functools.lru_cache`.
- **Testable time:** injecting `clock` makes expiry deterministic in tests, a standard design technique (dependency injection) for anything time-based in robotics and distributed systems.
- **Concurrency (module 11):** one lock guards every operation, private helpers assume it's held, and the stress test checks that the invariants survive 8 threads.
