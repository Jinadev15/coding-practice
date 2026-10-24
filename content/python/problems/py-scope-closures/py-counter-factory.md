---
id: py-counter-factory
title: Counter Factory
difficulty: Easy
order: 1
tags: closures, nonlocal
---
## Statement
Write `make_counter(start=0, step=1)` that returns **three functions** sharing private state (no globals, no classes):

- `inc()`: adds `step` to the count and returns the new value
- `get()`: returns the current value
- `reset()`: restores the count to `start` and returns it

Several counters must be independent. The driver creates counters by name and runs commands.

## Starter
```python
def make_counter(start=0, step=1):
    # return inc, get, reset
    pass
```

## Driver
```python
counters = {}
q = int(input())
for _ in range(q):
    parts = input().split()
    if parts[0] == "new":
        name, start, step = parts[1], int(parts[2]), int(parts[3])
        counters[name] = make_counter(start, step)
    else:
        name, op = parts
        inc, get, reset = counters[name]
        print({"inc": inc, "get": get, "reset": reset}[op]())
```

## Tests
=== sample
6
new a 0 1
a inc
a inc
a get
a reset
a get
---
1
2
2
0
0
=== hidden
7
new x 10 5
new y 0 -1
x inc
y inc
x inc
y get
x get
---
15
-1
20
-1
20
=== hidden
4
new z 3 0
z inc
z reset
z get
---
3
3
3

## Hints
- Store `count` in `make_counter`'s scope. Inner functions that **rebind** it need `nonlocal count`.
- `get` only reads `count`, so it needs no declaration.

## Solution
All three inner functions close over the same `count` cell. `inc` and `reset` rebind it, so they declare `nonlocal`.

```python
def make_counter(start=0, step=1):
    count = start

    def inc():
        nonlocal count
        count += step
        return count

    def get():
        return count

    def reset():
        nonlocal count
        count = start
        return count

    return inc, get, reset
```

Each call to `make_counter` creates a new `count`, so the counters `x` and `y` don't interfere. This is encapsulation without a class: the state is reachable **only** through the three functions. In the OOP module you'll write the same thing as a `Counter` class and compare the two designs.
