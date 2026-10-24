---
id: py-flexible-stats
title: Flexible Stats
difficulty: Easy
order: 1
tags: *args, keyword-only, defaults
---
## Statement
Write `stats(*nums, precision=2, drop_extremes=False)`:

- It accepts **any number** of numbers positionally.
- `precision` and `drop_extremes` must be **keyword-only**.
- If `drop_extremes` is true and there are at least 3 numbers, remove one minimum and one maximum first.
- It returns a tuple `(count, total, mean)`, with `mean` rounded to `precision` decimals (`round(x, precision)`), or `(0, 0, None)` if there are no numbers left.

Each input line looks like `numbers | options`, and the driver turns it into a call.

## Starter
```python
def stats(*nums, precision=2, drop_extremes=False):
    pass
```

## Driver
```python
import inspect
sig = inspect.signature(stats)
assert sig.parameters["precision"].kind == inspect.Parameter.KEYWORD_ONLY, "precision must be keyword-only"
t = int(input())
for _ in range(t):
    left, _, right = input().partition("|")
    nums = [float(x) if "." in x else int(x) for x in left.split()]
    opts = {}
    for item in right.split():
        k, v = item.split("=")
        opts[k] = int(v) if k == "precision" else v == "True"
    print(stats(*nums, **opts))
```

## Tests
=== sample
3
1 2 3 4 |
10 20 |precision=0
5 1 9 3 | drop_extremes=True
---
(4, 10, 2.5)
(2, 30, 15.0)
(2, 8, 4.0)
=== hidden
3
|
7 | drop_extremes=True
1 1 | drop_extremes=True precision=1
---
(0, 0, None)
(1, 7, 7.0)
(2, 2, 1.0)
=== hidden
2
2 3 3 | precision=3
1.5 2.25 | precision=1
---
(3, 8, 2.667)
(2, 3.75, 1.9)

## Hints
- `nums` arrives as a tuple. Convert it to a list if you need to remove items.
- Removing extremes: `vals.remove(min(vals)); vals.remove(max(vals))`.

## Solution
`*nums` gathers the positional arguments; everything after it is automatically keyword-only.

```python
def stats(*nums, precision=2, drop_extremes=False):
    vals = list(nums)
    if drop_extremes and len(vals) >= 3:
        vals.remove(min(vals))
        vals.remove(max(vals))
    if not vals:
        return (0, 0, None)
    total = sum(vals)
    return (len(vals), total, round(total / len(vals), precision))
```

Note that `round(x, 0)` still returns a **float** (`15.0`). Only `round(x)` with no second argument returns an `int`. The driver's `assert` checks that `precision` really is keyword-only, using `inspect.signature`, the same introspection that frameworks like FastAPI use to read your function signatures.
