# Study guide: Special quiz 2

Quiz 2 is about **designing** small systems: choosing data models, keeping state consistent, and handling time and concurrency.

## 1. Event-Sourced Order Book — event sourcing

In an ordinary program you store the **current state** and overwrite it. In **event sourcing** you store the **list of events** (`OrderPlaced`, `OrderCancelled`, `TradeExecuted`). The current state is whatever you get by **replaying** those events from the start.

```python
from dataclasses import dataclass
from enum import Enum

class Side(Enum):
    BUY = "BUY"
    SELL = "SELL"

@dataclass(frozen=True)
class Placed:
    id: int; side: Side; price: int; qty: int

@dataclass(frozen=True)
class Cancelled:
    id: int

def apply(state, event):
    match event:
        case Placed(id=i, side=s, price=p, qty=q):
            state[i] = {"side": s, "price": p, "qty": q}
        case Cancelled(id=i):
            state.pop(i, None)
    return state
```

Why it's useful:

- **Audit:** you know *how* you reached the current state.
- **Time travel:** replay the first N events to get the state at any earlier moment.
- **Bug fixing:** correct `apply` and replay to rebuild the state.

`match` with **class patterns** (`case Placed(id=i, ...)`) checks the type and extracts the fields in one step. `frozen=True` makes events immutable, so history can't be changed afterwards.

Matching rules for an order book: a BUY at price `p` matches resting SELLs with price `<= p`, best (lowest) price first. Among equal prices, the **oldest** order goes first ("price-time priority").

## 2. DAG Job Scheduler — topological sort and discrete-event simulation

Jobs that depend on other jobs form a **directed acyclic graph** (DAG). A job is *ready* when all its dependencies have finished. **Kahn's algorithm** processes the graph in a valid order:

```python
from collections import deque
def topo(n, edges):
    indeg = [0] * n; out = [[] for _ in range(n)]
    for a, b in edges:                # a must finish before b
        out[a].append(b); indeg[b] += 1
    ready = deque(i for i in range(n) if indeg[i] == 0)
    order = []
    while ready:
        u = ready.popleft(); order.append(u)
        for v in out[u]:
            indeg[v] -= 1
            if indeg[v] == 0: ready.append(v)
    if len(order) != n: raise ValueError("cycle")
    return order
```

When jobs take **time** and you have **k workers**, you need a simulation. Instead of ticking a clock one second at a time, jump straight to the **next interesting moment**. That is **discrete-event simulation**. Keep a heap of `(finish_time, job)` for running jobs:

1. While a worker is free and a job is ready, start the job (push `(now + duration, job)`).
2. Pop the earliest finish, set `now` to that time, and release its dependants.
3. Repeat until everything is done.

`heapq` orders tuples by their first element, then the second, so including the job id gives deterministic tie-breaking.

## 3. Thread-Safe LRU Cache with TTL — data structures and locks

**LRU** (least recently used) evicts the entry that hasn't been touched for the longest time. `collections.OrderedDict` gives you this in O(1) per operation:

```python
from collections import OrderedDict
import threading, time

class LRU:
    def __init__(self, cap, ttl):
        self.cap, self.ttl = cap, ttl
        self.d = OrderedDict()          # key -> (value, expires_at)
        self.lock = threading.Lock()
    def get(self, k, now=None):
        now = time.monotonic() if now is None else now
        with self.lock:
            if k not in self.d: return None
            v, exp = self.d[k]
            if now >= exp:
                del self.d[k]; return None
            self.d.move_to_end(k)       # mark as most recently used
            return v
    def put(self, k, v, now=None):
        now = time.monotonic() if now is None else now
        with self.lock:
            self.d[k] = (v, now + self.ttl); self.d.move_to_end(k)
            while len(self.d) > self.cap:
                self.d.popitem(last=False)   # evict least recently used
```

- **Why a lock?** `get` reads, checks and then moves the entry. If two threads interleave between those steps, the dict can be corrupted or return stale data. A `with self.lock:` block makes the whole sequence **atomic**.
- **TTL** (time to live): store the expiry time with each value and check it on read. Use `time.monotonic()`, never `time.time()`, because the wall clock can jump.
- **Decorator form:** `@cached(cap, ttl)` wraps a function and uses `args` (plus sorted `kwargs`) as the key. Use `functools.wraps` to keep the function's name.

> [!TIP]
> Take `now` as an optional parameter so tests can control time without sleeping.
