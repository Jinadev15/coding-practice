---
id: py-npb-axis-reductions
title: Axis Reductions
difficulty: Medium
order: 4
tags: numpy, axis, reductions, keepdims, argmax, 3-d arrays
time_limit: 3
compare: float
---
## Statement
A plant logs sensor readings in a 3-D array `r` of shape `(days, hours, sensors)`. Grading data is a 2-D array `scores` of shape `(students, assignments)`. Implement these using **axis reductions only**, with no Python loops:

```python
def weighted_totals(scores, weights):
    """Per-student weighted total: sum_j scores[i, j] * weights[j]. Returns shape (students,)."""

def column_summary(scores):
    """Array of shape (4, assignments): rows are mean, population std, min, max of each column."""

def row_shares(x):
    """Divide each row by its row sum so that the row sums to 1. Rows whose sum is 0 stay all zeros."""

def daily_peaks(r):
    """Return (peak, peak_hour), both of shape (days, sensors): the maximum over the hours of each
    day/sensor, and the hour at which it first occurs."""

def worst_sensor(r):
    """Index of the sensor with the largest mean reading over all days and hours (ties -> smallest index)."""
```

**Input:** one call per line as a Python tuple `("name", args)`. A line `gen D H S SEED` runs a large check.

**Output:** arrays print as `shape v1 v2 ...` (shape joined by `x`, values to 4 decimals, row-major). `daily_peaks` prints both arrays on one line separated by `|`.

## Starter
```python
import numpy as np

def weighted_totals(scores, weights):
    return scores.sum(axis=0) * 0

def column_summary(scores):
    return np.array([scores.mean(axis=1), scores.std(axis=1), scores.min(axis=1), scores.max(axis=1)])

def row_shares(x):
    return x / x.sum()

def daily_peaks(r):
    return r.max(axis=0), r.argmax(axis=0)

def worst_sensor(r):
    return 0
```

## Driver
```python
import ast
import sys
import numpy as np

def show(a):
    a = np.asarray(a, dtype=float)
    shape = "x".join(map(str, a.shape)) or "scalar"
    return (shape + " " + " ".join(f"{v:.4f}" for v in a.ravel().tolist())).rstrip()

for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    if line.startswith("gen "):
        _, d, h, s, seed = line.split()
        d, h, s, rng = int(d), int(h), int(s), np.random.default_rng(int(seed))
        r = rng.normal(50, 10, size=(d, h, s)).round(1)
        sc = rng.integers(0, 101, size=(d * h, s)).astype(float)
        w = rng.random(s)
        wt = weighted_totals(sc, w)
        cs = column_summary(sc)
        sh = row_shares(sc)
        pk, ph = daily_peaks(r)
        print("gen", wt.shape, f"{wt.sum():.4f}", cs.shape, f"{cs.sum():.4f}", f"{sh.sum():.4f}",
              pk.shape, f"{pk.sum():.4f}", int(np.asarray(ph).sum()), worst_sensor(r))
        continue
    name, args = ast.literal_eval(line)
    if name == "weighted_totals":
        print(show(weighted_totals(np.array(args[0], dtype=float), np.array(args[1], dtype=float))))
    elif name == "column_summary":
        print(show(column_summary(np.array(args[0], dtype=float))))
    elif name == "row_shares":
        print(show(row_shares(np.array(args[0], dtype=float))))
    elif name == "daily_peaks":
        pk, ph = daily_peaks(np.array(args[0], dtype=float))
        print(show(pk), "|", show(ph))
    else:
        print(worst_sensor(np.array(args[0], dtype=float)))
```

## Tests
=== sample
("weighted_totals", ([[80, 90], [60, 100]], [0.25, 0.75]))
("column_summary", ([[1, 10], [3, 20], [5, 60]],))
("row_shares", ([[1, 3], [0, 0], [2, 2]],))
("daily_peaks", ([[[1, 9], [4, 2], [4, 8]], [[0, 0], [5, 5], [3, 7]]],))
("worst_sensor", ([[[1, 9], [4, 2]], [[0, 0], [5, 5]]],))
---
2 87.5000 90.0000
4x2 3.0000 30.0000 1.6330 21.6025 1.0000 10.0000 5.0000 60.0000
3x2 0.2500 0.7500 0.0000 0.0000 0.5000 0.5000
2x2 4.0000 9.0000 5.0000 7.0000 | 2x2 1.0000 0.0000 1.0000 2.0000
1
=== hidden
("weighted_totals", ([[1, 2, 3]], [1, 1, 1]))
("weighted_totals", ([[1], [2], [3]], [2]))
("column_summary", ([[7, 7]],))
("column_summary", ([[-1], [1]],))
("row_shares", ([[0, 0, 0]],))
("row_shares", ([[5], [0], [-2]],))
("row_shares", ([[1, -1, 2], [0.5, 0.5, 0]],))
("daily_peaks", ([[[3]]],))
("daily_peaks", ([[[2, 2], [2, 3], [1, 3]]],))
("worst_sensor", ([[[5, 5, 5]]],))
("worst_sensor", ([[[1, 2, 3]], [[3, 2, 1]], [[0, 9, 0]]],))
---
1 6.0000
3 2.0000 4.0000 6.0000
4x2 7.0000 7.0000 0.0000 0.0000 7.0000 7.0000 7.0000 7.0000
4x1 0.0000 1.0000 -1.0000 1.0000
1x3 0.0000 0.0000 0.0000
3x1 1.0000 0.0000 1.0000
2x3 0.5000 -0.5000 1.0000 0.5000 0.5000 0.0000
1x1 3.0000 | 1x1 0.0000
1x2 2.0000 3.0000 | 1x2 0.0000 1.0000
0
1
=== hidden
gen 400 24 60 3
---
gen (9600,) 13524612.7527 (4, 60) 10749.8395 9600.0000 (400, 60) 1668033.2000 274336 5

## Hints
- `axis=k` is the axis that *disappears*. For `(days, hours, sensors)`, which axis must vanish to get one value per day and sensor?
- A row sum must stay a column, `(rows, 1)`, to broadcast correctly. Look up `keepdims=True`.
- You can reduce several axes at once with a tuple, `axis=(0, 1)`. `argmax` returns the first maximum.

## Solution
**The rule: `axis=k` names the axis that disappears.** For a `(days, hours, sensors)` array:

- `axis=1` collapses hours, giving `(days, sensors)`: one peak per day and sensor.
- `axis=(0, 1)` collapses days and hours together, giving `(sensors,)`.

`argmax` returns the *first* index of the maximum, which is exactly the tie rule required.

- **Weighted totals** are a matrix–vector product. `(scores * weights).sum(axis=1)` is equivalent, because `weights` broadcasts along the rows.
- **Column summaries** reduce `axis=0` (down the rows). `np.std` is the population std (`ddof=0`) by default. `np.stack` then puts the four `(assignments,)` vectors on a new leading axis.
- **Row shares** need `keepdims=True`. Without it, the sums have shape `(rows,)`, which broadcasts against the *last* axis (the columns) and silently divides by the wrong numbers, or raises an error when the shapes differ. `np.divide(..., where=s != 0, out=zeros)` handles the zero rows without warnings.

Complexity: every function is O(total elements).

```python
import numpy as np

def weighted_totals(scores, weights):
    return scores @ weights                      # (students, a) @ (a,) -> (students,)

def column_summary(scores):
    return np.stack([scores.mean(axis=0), scores.std(axis=0),
                     scores.min(axis=0), scores.max(axis=0)])

def row_shares(x):
    s = x.sum(axis=1, keepdims=True)            # (rows, 1) broadcasts against (rows, cols)
    return np.divide(x, s, out=np.zeros_like(x), where=s != 0)

def daily_peaks(r):
    return r.max(axis=1), r.argmax(axis=1)       # axis 1 = hours disappears

def worst_sensor(r):
    return int(r.mean(axis=(0, 1)).argmax())     # reduce days and hours together
```
