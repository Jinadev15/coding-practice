---
id: py-tdd-token-bucket
title: Spec-Driven Token-Bucket Rate Limiter
difficulty: Medium
order: 1
tags: TDD, dependency injection, clock, specification, edge cases
---
## Statement
Practise **test-driven development** from a written specification. Implement a token-bucket rate limiter for robot command APIs. Time is **injected** (a `clock` callable returning seconds as a float), so the behaviour is deterministic and testable. Never call `time.time()` yourself.

```python
class TokenBucket:
    def __init__(self, rate: float, capacity: int, clock): ...
    def allow(self, cost: int = 1) -> bool: ...
    def tokens(self) -> float: ...
    def wait_time(self, cost: int = 1) -> float: ...
```

Specification:
1. `rate` > 0 (tokens per second) and `capacity` ≥ 1, otherwise `ValueError`. The bucket starts **full**.
2. Tokens refill continuously at `rate` per second, never exceeding `capacity`. Refill is computed lazily from the clock whenever any method is called.
3. `allow(cost)` consumes `cost` tokens and returns `True` if at least `cost` are available; otherwise it consumes nothing and returns `False`.
4. `cost` must be an integer ≥ 1, else `ValueError`; a cost above `capacity` can never succeed and raises `ValueError`.
5. `tokens()` returns the current token count (after refill).
6. `wait_time(cost)` returns how many seconds until `allow(cost)` would succeed (`0.0` if it would now). It doesn't consume. Same `cost` validation as `allow`.
7. If the clock goes **backwards** (e.g. an NTP adjustment), treat elapsed time as 0. Never remove tokens because of it.

The driver reads commands (one per line):
- `new RATE CAP` creates a bucket. The fake clock restarts at 0.
- `t SECONDS` sets the fake clock.
- `allow [COST]`, `tokens` and `wait [COST]` call the matching method.

Each command prints its result (floats rounded to 3 decimals) or `ValueError`.

## Starter
```python
class TokenBucket:
    def __init__(self, rate, capacity, clock):
        self.rate, self.capacity, self.clock = rate, capacity, clock
        self._tokens = capacity

    def allow(self, cost=1):
        if self._tokens >= cost:
            self._tokens -= cost
            return True
        return False

    def tokens(self):
        return self._tokens

    def wait_time(self, cost=1):
        return 0.0
```

## Driver
```python
import sys

now = [0.0]
clock = lambda: now[0]
bucket = None
for line in sys.stdin.read().splitlines():
    parts = line.split()
    if not parts:
        continue
    cmd, args = parts[0], parts[1:]
    try:
        if cmd == "new":
            now[0] = 0.0
            bucket = TokenBucket(float(args[0]), int(args[1]), clock)
            out = "ok"
        elif cmd == "t":
            now[0] = float(args[0])
            continue
        elif cmd == "allow":
            out = bucket.allow(*(int(a) if a.lstrip("-").isdigit() else float(a) for a in args))
        elif cmd == "tokens":
            out = round(float(bucket.tokens()), 3)
        elif cmd == "wait":
            out = round(float(bucket.wait_time(*(int(a) if a.lstrip("-").isdigit() else float(a) for a in args))), 3)
        print(line, "->", out)
    except ValueError:
        print(line, "-> ValueError")
```

## Tests
=== sample
new 2 5
allow 3
tokens
allow 3
wait 3
t 0.5
tokens
allow 3
t 10
tokens
---
new 2 5 -> ok
allow 3 -> True
tokens -> 2.0
allow 3 -> False
wait 3 -> 0.5
tokens -> 3.0
allow 3 -> True
tokens -> 5.0
=== hidden
new 0 5
new 1 0
new -1 3
new 1 3
allow 0
allow -1
allow 4
allow 1.5
wait 4
wait 3
allow 3
wait 1
t 0.25
tokens
wait 1
t 1
allow 1
tokens
t 0.5
tokens
allow 1
t 100
tokens
wait 2
---
new 0 5 -> ValueError
new 1 0 -> ValueError
new -1 3 -> ValueError
new 1 3 -> ok
allow 0 -> ValueError
allow -1 -> ValueError
allow 4 -> ValueError
allow 1.5 -> ValueError
wait 4 -> ValueError
wait 3 -> 0.0
allow 3 -> True
wait 1 -> 1.0
tokens -> 0.25
wait 1 -> 0.75
allow 1 -> True
tokens -> 0.0
tokens -> 0.0
allow 1 -> False
tokens -> 3.0
wait 2 -> 0.0
=== hidden
new 0.5 2
allow 2
allow
wait
t 1
wait
t 1.999
allow
t 2
allow
t 3
tokens
wait 2
t 4
allow 2
---
new 0.5 2 -> ok
allow 2 -> True
allow -> False
wait -> 2.0
wait -> 1.0
allow -> False
allow -> True
tokens -> 0.5
wait 2 -> 3.0
allow 2 -> False
=== hidden
new 10 100
allow 60
allow 50
wait 50
t 0.9
allow 50
tokens
t 1
allow 50
t 1.05
tokens
t 0.5
tokens
t 2
tokens
---
new 10 100 -> ok
allow 60 -> True
allow 50 -> False
wait 50 -> 1.0
allow 50 -> False
tokens -> 49.0
allow 50 -> True
tokens -> 0.5
tokens -> 0.5
tokens -> 15.5

## Hints
- Store `self._last = clock()` in `__init__`, and write a private `_refill()` that every public method calls first: `now = self.clock(); elapsed = max(0.0, now - self._last); self._tokens = min(capacity, self._tokens + elapsed * rate); self._last = now`.
- `wait_time` is `max(0, (cost - tokens) / rate)`.
- Type check: `isinstance(cost, int) and not isinstance(cost, bool)`; `allow 1.5` must raise.
- The clock-goes-backwards case: after `t 0.5` following `t 1`, the elapsed time is negative. Clamp it to 0 **and** set `_last` to the new (earlier) time, so refill resumes from there: after `t 0.5` then `t 2`, 1.5 s of refill is credited.

## Solution
```python
class TokenBucket:
    def __init__(self, rate, capacity, clock):
        if not rate > 0:
            raise ValueError("rate must be positive")
        if not isinstance(capacity, int) or capacity < 1:
            raise ValueError("capacity must be an integer >= 1")
        self.rate = float(rate)
        self.capacity = capacity
        self.clock = clock
        self._tokens = float(capacity)
        self._last = clock()

    def _refill(self):
        now = self.clock()
        elapsed = max(0.0, now - self._last)       # a clock jump backwards adds nothing
        self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)
        self._last = now

    def _check_cost(self, cost):
        if not isinstance(cost, int) or isinstance(cost, bool) or cost < 1:
            raise ValueError("cost must be an integer >= 1")
        if cost > self.capacity:
            raise ValueError("cost exceeds capacity")

    def allow(self, cost=1):
        self._check_cost(cost)
        self._refill()
        if self._tokens >= cost:
            self._tokens -= cost
            return True
        return False

    def tokens(self):
        self._refill()
        return self._tokens

    def wait_time(self, cost=1):
        self._check_cost(cost)
        self._refill()
        return max(0.0, (cost - self._tokens) / self.rate)
```

The TDD cycle for a spec like this is **red → green → refactor**, one rule at a time: write a failing test for rule 1 (validation), make it pass, then rule 2 (refill), and so on. Two design decisions make the class testable at all:
- **Injected time.** With `time.time()` inside, every test would need `sleep` or patching. With a `clock` parameter, a test is just "set t = 0.5, then ask". That's the same reason ROS 2 nodes take a clock that can run in simulation time.
- **Lazy refill** computed on each call means there's no background thread, so behaviour is a pure function of the call sequence and the clock values.

Note rule 7: monotonic-clock bugs are a real production issue. This is why Python offers `time.monotonic()`, which you'd pass as the clock in real code.
