---
id: py-debug-telemetry
title: Debug the Telemetry Aggregator
difficulty: Medium
order: 1
tags: debugging, mutable default, late binding, float comparison, off-by-one
---
## Statement
A teammate wrote a telemetry aggregator for a robot fleet. It "mostly works" but production reports are wrong. The starter code contains **six independent bugs**, each a classic Python pitfall. Find and fix them all; keep the public API identical.

The intended behaviour:
- `Aggregator()` creates an aggregator. Each instance has its **own** readings.
- `add(robot, value, tags=None)` stores a reading. `tags` defaults to an empty list, and **each reading has its own tag list**.
- `moving_average(robot, window)` returns the average of the **last `window`** readings of that robot (all of them if fewer), or `None` if it has none. `window` ≥ 1.
- `within(robot, target, tol=1e-9)` returns `True` if the latest reading is within `tol` of `target` (absolute difference ≤ `tol`). Use this, never `==`, for floats.
- `thresholds(levels)` returns a list of functions; the `i`-th function `f(x)` returns `x > levels[i]`.
- `summary()` returns robots sorted by name, each with its count and max, as `"name:count:max"` strings joined by `", "`.

The driver exercises everything and prints the results. Use the failing output to locate each bug, the way you would with a debugger or print statements: narrow down, form a hypothesis, test it.

## Starter
```python
class Aggregator:
    readings = {}

    def add(self, robot, value, tags=[]):
        tags.append(robot)
        self.readings.setdefault(robot, []).append((value, tags))

    def moving_average(self, robot, window):
        vals = [v for v, _ in self.readings.get(robot, [])]
        if not vals:
            return None
        recent = vals[-window - 1:]
        return sum(recent) / len(recent)

    def within(self, robot, target, tol=1e-9):
        latest = self.readings[robot][-1][0]
        return latest == target

    def thresholds(self, levels):
        return [lambda x: x > levels[i] for i in range(len(levels))]

    def summary(self):
        parts = []
        for name, rs in self.readings.items():
            parts.append(f"{name}:{len(rs)}:{max(rs)}")
        return ", ".join(parts)
```

## Driver
```python
a = Aggregator()
b = Aggregator()
a.add("rover", 0.1)
a.add("rover", 0.2)
a.add("arm", 5)
a.add("rover", 0.3)
print("b has its own readings:", b.readings == {} if isinstance(b.readings, dict) else b.readings)
print("tags of first reading:", a.readings["rover"][0][1])
print("avg last 2:", round(a.moving_average("rover", 2), 6))
print("avg last 1:", a.moving_average("rover", 1))
print("avg last 10:", round(a.moving_average("rover", 10), 6))
print("avg unknown:", a.moving_average("drone", 3))
b.add("probe", 0.1 + 0.2)
print("0.1+0.2 within 0.3:", b.within("probe", 0.3))
print("within loose tol:", b.within("probe", 0.31, tol=0.02))
print("within tight tol:", b.within("probe", 0.31, tol=0.001))
fs = a.thresholds([1, 5, 10])
print("thresholds at 6:", [f(6) for f in fs])
a.add("arm", 2, tags=["calibration"])
a.add("zeta", -1)
a.add("arm", 9)
print("summary:", a.summary())
```

## Tests
=== sample
---
b has its own readings: True
tags of first reading: ['rover']
avg last 2: 0.25
avg last 1: 0.3
avg last 10: 0.2
avg unknown: None
0.1+0.2 within 0.3: True
within loose tol: True
within tight tol: False
thresholds at 6: [True, True, False]
summary: arm:3:9, rover:3:0.3, zeta:1:-1

## Hints
- **Class attribute** `readings = {}` is shared by every instance. Create it in `__init__`.
- **Mutable default** `tags=[]` is created once, at `def` time. Use `None` and create a new list.
- **Off-by-one**: `vals[-window:]` takes exactly the last `window` items.
- **Float equality**: `0.1 + 0.2 != 0.3`. Compare `abs(a - b) <= tol` (or `math.isclose`).
- **Late binding**: lambdas in a comprehension look up `i` when they're *called*, after the loop finished. Bind it now with a default argument: `lambda x, i=i: ...`.
- **Summary**: `max(rs)` compares `(value, tags)` tuples, and the order isn't sorted by name. Use `max(v for v, _ in rs)` and `sorted(...)`.

## Solution
```python
class Aggregator:
    def __init__(self):
        self.readings = {}                       # bug 1: per-instance state, not a shared class attribute

    def add(self, robot, value, tags=None):
        tags = [] if tags is None else list(tags)  # bug 2: a fresh list per call
        tags.append(robot)
        self.readings.setdefault(robot, []).append((value, tags))

    def moving_average(self, robot, window):
        vals = [v for v, _ in self.readings.get(robot, [])]
        if not vals:
            return None
        recent = vals[-window:]                  # bug 3: exactly the last `window` values
        return sum(recent) / len(recent)

    def within(self, robot, target, tol=1e-9):
        latest = self.readings[robot][-1][0]
        return abs(latest - target) <= tol       # bug 4: tolerance, not ==

    def thresholds(self, levels):
        return [lambda x, lv=lv: x > lv for lv in levels]   # bug 5: bind each level now

    def summary(self):
        return ", ".join(f"{name}:{len(rs)}:{max(v for v, _ in rs)}"   # bug 6: max of values, sorted names
                         for name, rs in sorted(self.readings.items()))
```

The six bugs, and how each shows up in the output:
1. **Shared class attribute.** `b` sees `a`'s robots. Mutable class attributes are shared by every instance.
2. **Mutable default argument.** The first reading's tags grow to `['rover', 'rover', 'arm', 'rover']`, because one list object is reused across calls.
3. **Off-by-one slice.** "avg last 1" averages two values.
4. **Float equality.** `0.1 + 0.2 == 0.3` is `False` in IEEE-754 binary floating point.
5. **Late-binding closures.** Every threshold compares against the last level (10).
6. **Wrong `max` and order.** `max` of tuples only works by accident, and dict order is insertion order, not sorted.

Debugging method: reproduce, then isolate (print or `breakpoint()` at the first wrong line of output), hypothesise, and verify with a minimal experiment. Finally, add a regression test so each bug stays fixed.
