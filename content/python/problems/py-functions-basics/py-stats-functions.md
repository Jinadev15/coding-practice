---
id: py-stats-functions
title: Statistics Toolkit
difficulty: Medium
order: 2
tags: functions, decomposition, math
---
## Statement
Write these functions **without** the `statistics` module, `sorted` excepted:

- `mean(xs)`: the arithmetic mean
- `median(xs)`: the middle value of the sorted data (the average of the two middle values for an even count)
- `mode(xs)`: the most frequent value; ties go to the **smallest** value
- `stdev(xs)`: the **population** standard deviation, `sqrt(Σ(x − mean)² / n)`, which must **reuse `mean`**
- `report(xs)`: returns the string `mean=… median=… mode=… stdev=…`, with every number shown to 2 decimals (mode as an integer)

The lists are non-empty integers.

## Starter
```python
import math

def mean(xs):
    pass

def median(xs):
    pass

def mode(xs):
    pass

def stdev(xs):
    pass

def report(xs):
    pass
```

## Driver
```python
input()
xs = list(map(int, input().split()))
print(report(xs))
```

## Tests
=== sample
5
2 4 4 4 5
---
mean=3.80 median=4.00 mode=4 stdev=0.98
=== sample
4
1 2 3 4
---
mean=2.50 median=2.50 mode=1 stdev=1.12
=== hidden
1
7
---
mean=7.00 median=7.00 mode=7 stdev=0.00
=== hidden
6
5 -5 5 -5 3 3
---
mean=1.00 median=3.00 mode=-5 stdev=4.32
=== hidden
8
2 4 4 4 5 5 7 9
---
mean=5.00 median=4.50 mode=4 stdev=2.00

## Hints
- `median`: sort a **copy** with `s = sorted(xs)`; for even `n`, average `s[n//2 - 1]` and `s[n//2]`.
- `mode`: count in a dict, then `min(counts, key=lambda v: (-counts[v], v))`.
- `report` should only *call* the other functions and format the results.

## Solution
Each statistic is one small function, and `report` only composes them. `stdev` reuses `mean` instead of repeating the formula.

```python
import math

def mean(xs):
    return sum(xs) / len(xs)

def median(xs):
    s = sorted(xs)
    n = len(s)
    mid = n // 2
    return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2

def mode(xs):
    counts = {}
    for x in xs:
        counts[x] = counts.get(x, 0) + 1
    return min(counts, key=lambda v: (-counts[v], v))

def stdev(xs):
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / len(xs))

def report(xs):
    return (f"mean={mean(xs):.2f} median={median(xs):.2f} "
            f"mode={mode(xs)} stdev={stdev(xs):.2f}")
```

`median` uses `sorted(xs)`, not `xs.sort()`, so the caller's list isn't mutated. A function shouldn't have surprising side effects on its arguments. The last test is the textbook example where the population standard deviation is exactly 2.
