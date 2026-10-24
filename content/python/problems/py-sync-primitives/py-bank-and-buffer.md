---
id: py-bank-and-buffer
title: Deadlock-Free Transfers and a Bounded Buffer
difficulty: Hard
order: 1
tags: threading, Lock, Condition, deadlock prevention, lock ordering
time_limit: 4
---
## Statement
Implement two classic concurrent components, which the driver stress-tests with many threads:

**1. `Bank`**: accounts each have their **own** `threading.Lock` (no single global lock).

```python
class Bank:
    def __init__(self, balances: dict[str, int])
    def transfer(self, src: str, dst: str, amount: int) -> bool
        # atomically move money if src has enough (False otherwise); src == dst returns False
    def total(self) -> int                     # sum of balances (callable at any time, consistent snapshot)
    def balance(self, name: str) -> int
```

Thousands of transfers run concurrently in both directions (A→B and B→A at once). A naive implementation that locks `src` and then `dst` **deadlocks**. Prevent it with a **global lock ordering**. `total()` must never observe money "in flight" (lock all accounts in the same order).

**2. `BoundedBuffer(capacity)`**: `put(item)` blocks while the buffer is full, `get()` blocks while it's empty, and `close()` makes `get()` return `None` once the buffer is drained (and makes `put` raise `RuntimeError`). Implement it with **one `threading.Condition`**, not `queue.Queue`.

## Starter
```python
import threading

class Bank:
    def __init__(self, balances):
        self.balances = dict(balances)
        self.locks = {k: threading.Lock() for k in balances}

    def transfer(self, src, dst, amount):
        with self.locks[src]:
            with self.locks[dst]:
                if src == dst or self.balances[src] < amount:
                    return False
                self.balances[src] -= amount
                self.balances[dst] += amount
                return True

    def total(self):
        return sum(self.balances.values())

    def balance(self, name):
        return self.balances[name]

class BoundedBuffer:
    def __init__(self, capacity):
        self.items = []
    def put(self, item):
        self.items.append(item)
    def get(self):
        return self.items.pop(0) if self.items else None
    def close(self):
        pass
```

## Driver
```python
import sys
import random

def stress_bank(n_accounts, n_threads, n_ops, seed):
    names = [f"acct{i}" for i in range(n_accounts)]
    bank = Bank({n: 1000 for n in names})
    expected = bank.total()
    snapshots_ok = []
    def worker(k):
        rng = random.Random(seed * 1000 + k)
        for _ in range(n_ops):
            a, b = rng.choice(names), rng.choice(names)
            bank.transfer(a, b, rng.randint(1, 300))
            if rng.random() < 0.02:
                snapshots_ok.append(bank.total() == expected)
    ts = [threading.Thread(target=worker, args=(k,)) for k in range(n_threads)]
    for t in ts: t.start()
    for t in ts: t.join()
    print(f"bank: total preserved={bank.total() == expected} snapshots consistent={all(snapshots_ok)} "
          f"no negatives={all(bank.balance(n) >= 0 for n in names)} self-transfer={bank.transfer(names[0], names[0], 1)}")

def stress_buffer(capacity, producers, items_each):
    buf = BoundedBuffer(capacity)
    got = []
    lock = threading.Lock()
    max_seen = [0]
    def producer(p):
        for i in range(items_each):
            buf.put((p, i))
    def consumer():
        while (item := buf.get()) is not None:
            with lock:
                got.append(item)
    cons = [threading.Thread(target=consumer) for _ in range(3)]
    prods = [threading.Thread(target=producer, args=(p,)) for p in range(producers)]
    for t in cons + prods: t.start()
    for t in prods: t.join()
    buf.close()
    for t in cons: t.join()
    try:
        buf.put("late")
        late = "accepted"
    except RuntimeError:
        late = "rejected"
    per_producer_ordered = all(
        [i for p2, i in got if p2 == p] == sorted(i for p2, i in got if p2 == p) for p in range(producers))
    print(f"buffer: received={len(got)} unique={len(set(got))} expected={producers * items_each} "
          f"put after close {late}")

for line in sys.stdin.read().splitlines():
    kind, *args = line.split()
    args = list(map(int, args))
    if kind == "bank":
        stress_bank(*args)
    elif kind == "buffer":
        stress_buffer(*args)
```

## Tests
=== sample
bank 3 4 2000 1
buffer 2 3 200
---
bank: total preserved=True snapshots consistent=True no negatives=True self-transfer=False
buffer: received=600 unique=600 expected=600 put after close rejected
=== hidden
bank 2 8 5000 7
bank 50 8 3000 9
buffer 1 5 400
buffer 64 2 2000
---
bank: total preserved=True snapshots consistent=True no negatives=True self-transfer=False
bank: total preserved=True snapshots consistent=True no negatives=True self-transfer=False
buffer: received=2000 unique=2000 expected=2000 put after close rejected
buffer: received=4000 unique=4000 expected=4000 put after close rejected

## Hints
- Lock ordering: `first, second = sorted((src, dst))`, then `with self.locks[first], self.locks[second]:`. Every thread acquires any pair of locks in the same global (alphabetical) order, so a waits-for cycle can't form.
- Check `src == dst` **before** locking (locking the same `Lock` twice deadlocks).
- `total()`: acquire **all** locks in sorted order (with `contextlib.ExitStack`), sum, then release.
- Buffer: `self.cond = threading.Condition()`. In `put`: `with self.cond: while len(items) >= cap and not closed: self.cond.wait()`, append, `notify_all()`. In `get`: `while not items and not closed: wait()`; if it's empty and closed, return `None`.

## Solution
```python
import threading
from collections import deque
from contextlib import ExitStack

class Bank:
    def __init__(self, balances):
        self.balances = dict(balances)
        self.locks = {k: threading.Lock() for k in balances}

    def transfer(self, src, dst, amount):
        if src == dst:
            return False
        first, second = sorted((src, dst))             # global order: no circular wait possible
        with self.locks[first], self.locks[second]:
            if self.balances[src] < amount:
                return False
            self.balances[src] -= amount
            self.balances[dst] += amount
            return True

    def total(self):
        with ExitStack() as stack:
            for name in sorted(self.locks):            # same order as transfer
                stack.enter_context(self.locks[name])
            return sum(self.balances.values())

    def balance(self, name):
        with self.locks[name]:
            return self.balances[name]


class BoundedBuffer:
    def __init__(self, capacity):
        self.items = deque()
        self.capacity = capacity
        self.closed = False
        self.cond = threading.Condition()

    def put(self, item):
        with self.cond:
            while len(self.items) >= self.capacity and not self.closed:
                self.cond.wait()
            if self.closed:
                raise RuntimeError("buffer closed")
            self.items.append(item)
            self.cond.notify_all()

    def get(self):
        with self.cond:
            while not self.items and not self.closed:
                self.cond.wait()
            if not self.items:                          # closed and drained
                return None
            item = self.items.popleft()
            self.cond.notify_all()                      # wake producers waiting for space
            return item

    def close(self):
        with self.cond:
            self.closed = True
            self.cond.notify_all()                      # wake everyone so they can see `closed`
```

- **Deadlock prevention by lock ordering:** the starter locks `src` then `dst`, so concurrent A→B and B→A transfers each grab one lock and wait forever for the other (a circular wait). Sorting the two names imposes a global order that breaks the cycle, which is the standard fix (and what `std::scoped_lock` does in C++). The same ordering in `total()` gives a consistent snapshot: no transfer can be half-done while it holds every lock.
- **Per-account locks** allow transfers between disjoint pairs to run in parallel. A single global lock would be correct, but would serialise everything.
- **Condition variables:** `wait()` atomically releases the lock and sleeps, and waiters re-check their predicate in a `while` loop, because wake-ups can be spurious and another thread may have taken the item first. `notify_all` after every state change, including `close()`, guarantees that nobody sleeps through the change they're waiting for.
