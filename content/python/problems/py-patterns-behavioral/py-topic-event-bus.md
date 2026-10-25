---
id: py-topic-event-bus
title: A Topic-Based Event Bus with Weak Subscriptions
difficulty: Hard
order: 1
tags: observer, publish/subscribe, wildcards, weakref, priorities, run-to-completion, error isolation
time_limit: 5
---
## Statement
Build the in-process event bus a robot application uses to connect its components (an in-process cousin of ROS topics and MQTT).

**Topics** are dot-separated segments, such as `robot.r1.battery`. A topic is valid when every segment is non-empty and contains no `*`, `#` or whitespace. An invalid topic raises `ValueError`.

**Patterns** may use wildcards, as in MQTT and AMQP:
- `*` matches exactly one segment.
- `#` matches zero or more segments, and is only allowed as the **last** segment.

Other segments follow the topic rules. An invalid pattern raises `ValueError`.

**`EventBus`**
- `subscribe(pattern, handler, *, priority=0) -> Subscription`.
  - Handlers are called as `handler(topic, payload)`.
  - **Bound methods are held weakly** (`weakref.WeakMethod`). When their object is garbage-collected, the subscription silently disappears. Plain functions and lambdas are held strongly.
- `publish(topic, payload) -> int` delivers to every live matching subscription, in order of **priority descending, then subscription order**, and returns how many handlers were called.
  - If a handler raises, the exception is caught and appended to `bus.errors` as `(topic, handler_name, repr(exc))`, and delivery continues. `handler_name` is the handler's `__qualname__`.
  - **Run-to-completion**: a `publish` made *from inside a handler* is queued and delivered after the current delivery finishes (FIFO), and that inner call returns 0. The outer `publish` returns only its own count.
- `subscription_count()`: the number of live subscriptions.
- `Subscription.cancel()` is idempotent. `Subscription.active` is True until it's cancelled or its weak target dies. A subscription cancelled during a delivery, before its turn, is not called.

## Starter
```python
class Subscription:
    def __init__(self, bus, pattern, handler):
        self.bus, self.pattern, self.handler = bus, pattern, handler
        self.active = True

    def cancel(self):
        self.bus.subs.remove(self)


class EventBus:
    def __init__(self):
        self.subs = []
        self.errors = []

    def subscribe(self, pattern, handler, *, priority=0):
        s = Subscription(self, pattern, handler)
        self.subs.append(s)
        return s

    def publish(self, topic, payload):
        n = 0
        for s in self.subs:
            if s.pattern == topic:
                s.handler(topic, payload)
                n += 1
        return n

    def subscription_count(self):
        return len(self.subs)
```

## Driver
```python
import gc
import sys

def attempt(label, fn):
    try:
        print(f"{label}: {fn()!r}")
    except ValueError as e:
        print(f"{label}: ValueError")

for cmd in sys.stdin.read().split():
    bus = EventBus()
    log = []
    if cmd == "match":
        pats = ["robot.r1.battery", "robot.*.battery", "robot.#", "#", "robot.*", "*.*.*", "robot.r1.#", "fleet.#"]
        for p in pats:
            bus.subscribe(p, lambda t, d, p=p: log.append(p))
        for topic in ["robot.r1.battery", "robot.r2", "robot", "fleet", "robot.r1.arm.joint3", "map"]:
            log.clear()
            n = bus.publish(topic, None)
            print(f"{topic}: {n} {log}")
        for bad in ["", "robot..x", "robot.#.x", "ro#bot", "a.b c", "#.#"]:
            attempt(f"pattern {bad!r}", lambda: bus.subscribe(bad, print))
        for bad in ["", "robot.*", "robot.#", "a..b", "x y"]:
            attempt(f"topic {bad!r}", lambda: bus.publish(bad, 1))
    elif cmd == "order":
        for name, pr in [("low", -1), ("a", 0), ("high", 5), ("b", 0), ("mid", 2)]:
            bus.subscribe("t.#", lambda t, d, name=name: log.append(name), priority=pr)
        bus.publish("t.x", 1); print(log)
        def boom(t, d): raise RuntimeError(f"bad payload {d}")
        bus.subscribe("t.x", boom, priority=3)
        log.clear(); print("count", bus.publish("t.x", 7), log)
        print("errors", bus.errors)
    elif cmd == "cancel":
        subs = {}
        def killer(t, d):
            log.append("killer"); subs["victim"].cancel(); subs["self"].cancel()
        subs["k"] = bus.subscribe("x", killer, priority=10)
        subs["victim"] = bus.subscribe("x", lambda t, d: log.append("victim"))
        subs["self"] = bus.subscribe("x", lambda t, d: log.append("self"), priority=20)
        print(bus.publish("x", 0), log, bus.subscription_count())
        subs["victim"].cancel(); subs["victim"].cancel()
        print("actives", subs["k"].active, subs["victim"].active, subs["self"].active)
    elif cmd == "weak":
        class Widget:
            def __init__(self, name): self.name = name
            def on_event(self, t, d): log.append((self.name, d))
        w1, w2 = Widget("w1"), Widget("w2")
        s1 = bus.subscribe("ui.#", w1.on_event)
        s2 = bus.subscribe("ui.#", w2.on_event)
        bus.subscribe("ui.#", lambda t, d: log.append(("lambda", d)))
        print(bus.publish("ui.refresh", 1), log, bus.subscription_count())
        del w1; gc.collect(); log.clear()
        print(bus.publish("ui.refresh", 2), log, bus.subscription_count(), s1.active, s2.active)
    elif cmd == "nested":
        def on_cmd(t, d):
            log.append(f"cmd:{d}")
            log.append(f"inner returns {bus.publish('robot.status', 'moving')}")
            log.append(f"inner2 returns {bus.publish('robot.log', 'cmd ' + d)}")
            log.append(f"end cmd:{d}")
        bus.subscribe("robot.cmd", on_cmd)
        bus.subscribe("robot.#", lambda t, d: log.append(f"any {t}={d}"))
        print("outer", bus.publish("robot.cmd", "go"))
        for line in log: print(" ", line)
        def chain(t, d):
            if d < 3:
                bus.publish("chain", d + 1)
            log.append(d)
        log.clear(); bus.subscribe("chain", chain); print("chain", bus.publish("chain", 0), log)
    elif cmd == "load":
        counts = {}
        for i in range(300):
            pat = ["sensor.*.range", "sensor.#", f"sensor.s{i % 10}.range", "#"][i % 4]
            bus.subscribe(pat, lambda t, d, i=i: counts.__setitem__(i, counts.get(i, 0) + 1), priority=i % 7)
        total = sum(bus.publish(f"sensor.s{k % 25}.range", k) for k in range(2000))
        print("total", total, "subs", len(counts), "max", max(counts.values()), "min", min(counts.values()))
```

## Tests
=== sample
match
order
---
robot.r1.battery: 6 ['robot.r1.battery', 'robot.*.battery', 'robot.#', '#', '*.*.*', 'robot.r1.#']
robot.r2: 3 ['robot.#', '#', 'robot.*']
robot: 2 ['robot.#', '#']
fleet: 2 ['#', 'fleet.#']
robot.r1.arm.joint3: 3 ['robot.#', '#', 'robot.r1.#']
map: 1 ['#']
pattern '': ValueError
pattern 'robot..x': ValueError
pattern 'robot.#.x': ValueError
pattern 'ro#bot': ValueError
pattern 'a.b c': ValueError
pattern '#.#': ValueError
topic '': ValueError
topic 'robot.*': ValueError
topic 'robot.#': ValueError
topic 'a..b': ValueError
topic 'x y': ValueError
['high', 'mid', 'a', 'b', 'low']
count 6 ['high', 'mid', 'a', 'b', 'low']
errors [('t.x', 'boom', "RuntimeError('bad payload 7')")]
=== hidden
cancel
---
2 ['self', 'killer'] 1
actives True False False
=== hidden
weak
---
3 [('w1', 1), ('w2', 1), ('lambda', 1)] 3
2 [('w2', 2), ('lambda', 2)] 2 False True
=== hidden
nested
---
outer 2
  cmd:go
  inner returns 0
  inner2 returns 0
  end cmd:go
  any robot.cmd=go
  any robot.status=moving
  any robot.log=cmd go
chain 1 [0, 1, 2, 3]
=== hidden
load
---
total 456000 subs 300 max 2000 min 80

## Hints
- Matching: split both on `.`, then a small recursive function `m(i, j)` over pattern index `i` and topic index `j`. `#` matches when it's the last pattern segment, whatever remains.
- Store each subscription's handler as a callable *reference*: `weakref.WeakMethod(h)` if `inspect.ismethod(h)`, else `lambda: h`. Calling the reference gives the handler, or None if it's dead.
- Delivery: pick the matching subscriptions, sort by `(-priority, seq)` (a stable key), then check `sub.active` again just before each call.
- Run-to-completion: keep a `self._delivering` flag and a `deque` of pending `(topic, payload)`. The outermost publish drains the queue after its own delivery.

## Solution
```python
import inspect
import itertools
import weakref
from collections import deque


def _check_segments(parts, allow_wild):
    for i, seg in enumerate(parts):
        if allow_wild and seg == "*":
            continue
        if allow_wild and seg == "#":
            if i != len(parts) - 1:
                return False
            continue
        if not seg or any(c in seg for c in "*#") or any(c.isspace() for c in seg):
            return False
    return True


def _match(pat, top, i=0, j=0):
    if i == len(pat):
        return j == len(top)
    if pat[i] == "#":
        return True                                   # only ever last: matches the rest
    if j == len(top):
        return False
    return (pat[i] == "*" or pat[i] == top[j]) and _match(pat, top, i + 1, j + 1)


class Subscription:
    def __init__(self, bus, parts, handler, priority, seq):
        self._bus = bus
        self.parts = parts
        self.priority = priority
        self.seq = seq
        self.name = getattr(handler, "__qualname__", repr(handler))
        self._ref = weakref.WeakMethod(handler) if inspect.ismethod(handler) else (lambda h=handler: h)
        self._cancelled = False

    def handler(self):
        return None if self._cancelled else self._ref()

    @property
    def active(self):
        return self.handler() is not None

    def cancel(self):
        if not self._cancelled:
            self._cancelled = True
            self._bus._remove(self)


class EventBus:
    def __init__(self):
        self._subs = []
        self._seq = itertools.count()
        self._pending = deque()
        self._delivering = False
        self.errors = []

    def subscribe(self, pattern, handler, *, priority=0):
        parts = pattern.split(".")
        if not _check_segments(parts, allow_wild=True):
            raise ValueError(f"invalid pattern {pattern!r}")
        sub = Subscription(self, parts, handler, priority, next(self._seq))
        self._subs.append(sub)
        return sub

    def _remove(self, sub):
        if sub in self._subs:
            self._subs.remove(sub)

    def _prune(self):
        self._subs = [s for s in self._subs if s.active]

    def subscription_count(self):
        self._prune()
        return len(self._subs)

    def _deliver(self, topic, payload):
        parts = topic.split(".")
        targets = sorted((s for s in self._subs if _match(s.parts, parts)), key=lambda s: (-s.priority, s.seq))
        called = 0
        for sub in targets:
            fn = sub.handler()                         # re-check: cancelled or collected meanwhile?
            if fn is None:
                continue
            called += 1
            try:
                fn(topic, payload)
            except Exception as exc:                   # isolate failing subscribers
                self.errors.append((topic, sub.name, repr(exc)))
        self._prune()
        return called

    def publish(self, topic, payload):
        if not _check_segments(topic.split("."), allow_wild=False):
            raise ValueError(f"invalid topic {topic!r}")
        if self._delivering:                           # run-to-completion: queue nested events
            self._pending.append((topic, payload))
            return 0
        self._delivering = True
        try:
            count = self._deliver(topic, payload)
            while self._pending:
                self._deliver(*self._pending.popleft())
        finally:
            self._delivering = False
        return count
```

- **Wildcard matching** follows MQTT/AMQP semantics. `#` may match zero segments, so `robot.#` matches `robot` itself. Validating patterns up front stops typos like `robot.#.x` from silently never matching.
- **Weak subscriptions**: holding bound methods through `WeakMethod` means a destroyed widget or node unsubscribes automatically, which removes the most common observer memory leak. Lambdas and plain functions have no owner object, so they're kept strongly.
- **Deterministic ordering**: priority first, then subscription order (a sequence number keeps the sort stable and explicit). Safety handlers can always run before loggers.
- **Error isolation** records each failure with its topic and handler name, then carries on. One buggy subscriber can't silence the battery alarm.
- **Run-to-completion** queues events published during delivery and processes them FIFO afterwards. Every handler finishes before the next event starts, so handlers never see half-updated state and recursion depth stays flat (the `chain` test publishes from inside itself). It's the same model as an actor mailbox or the ROS single-threaded executor.
