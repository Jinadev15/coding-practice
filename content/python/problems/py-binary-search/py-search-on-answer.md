---
id: py-search-on-answer
title: Search on the Answer — Split Array, Koko, K-th in a Table
difficulty: Hard
order: 1
tags: binary search, monotone predicate, greedy check, counting
time_limit: 3
---
## Statement
Each function asks for an optimal number. Find it by binary searching over the **answer** with a monotone feasibility or count check.

```python
def split_array(nums, k):
    """Split nums (non-negative ints) into k non-empty contiguous parts, minimising the largest part sum.
    Return that minimum largest sum. 1 <= k <= len(nums)."""

def min_eating_speed(piles, h):
    """Each hour, eat up to `speed` bananas from ONE pile (finishing a pile ends that hour).
    Return the minimum integer speed to finish all piles within h hours (h >= len(piles))."""

def kth_in_table(m, n, k):
    """The k-th smallest number (1-based) in the m x n multiplication table [i*j for 1<=i<=m, 1<=j<=n].
    m, n up to 3*10**4; O(min(m, n) * log(m*n))."""

def max_min_distance(positions, c):
    """Place c >= 2 robots on distinct given positions maximising the minimum pairwise distance."""
```

Test lines are `(function_name, args)` literals or `gen NAME SEED N`.

## Starter
```python
def split_array(nums, k):
    return max(nums)

def min_eating_speed(piles, h):
    speed = 1
    while sum((p + speed - 1) // speed for p in piles) > h:
        speed += 1
    return speed

def kth_in_table(m, n, k):
    return sorted(i * j for i in range(1, m + 1) for j in range(1, n + 1))[k - 1]

def max_min_distance(positions, c):
    p = sorted(positions)
    return (p[-1] - p[0]) // (c - 1)
```

## Driver
```python
import ast
import random
import sys

FUNCS = {f.__name__: f for f in (split_array, min_eating_speed, kth_in_table, max_min_distance)}
for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    if line.startswith("gen "):
        _, name, seed, n = line.split()
        rng = random.Random(int(seed)); n = int(n)
        if name == "split_array":
            a = [rng.randrange(10**6) for _ in range(n)]
            print(name, n, [split_array(a, k) for k in (1, 7, 500, n)])
        elif name == "min_eating_speed":
            p = [rng.randrange(1, 10**9) for _ in range(n)]
            print(name, n, min_eating_speed(p, n), min_eating_speed(p, 3 * n + 17), min_eating_speed(p, 10**9))
        elif name == "kth_in_table":
            print(name, kth_in_table(30000, 30000, 450000000), kth_in_table(29999, 17, 1), kth_in_table(30000, 30000, 900000000))
        else:
            pos = rng.sample(range(10**9), n)
            print(name, n, max_min_distance(pos, 2), max_min_distance(pos, 1000), max_min_distance(pos, n))
        continue
    name, args = ast.literal_eval(line)
    print(name, "->", FUNCS[name](*args))
```

## Tests
=== sample
("split_array", ([7, 2, 5, 10, 8], 2))
("min_eating_speed", ([3, 6, 7, 11], 8))
("kth_in_table", (3, 3, 5))
("max_min_distance", ([1, 2, 8, 4, 9], 3))
---
split_array -> 18
min_eating_speed -> 4
kth_in_table -> 3
max_min_distance -> 3
=== hidden
("split_array", ([1, 2, 3, 4, 5], 1))
("split_array", ([1, 2, 3, 4, 5], 5))
("split_array", ([0, 0, 0], 2))
("split_array", ([1, 4, 4], 3))
("min_eating_speed", ([30, 11, 23, 4, 20], 5))
("min_eating_speed", ([30, 11, 23, 4, 20], 6))
("min_eating_speed", ([1], 1000))
("kth_in_table", (1, 1, 1))
("kth_in_table", (2, 3, 6))
("kth_in_table", (45, 12, 471))
("max_min_distance", ([5, 1], 2))
("max_min_distance", ([1, 2, 3, 4, 5], 5))
---
split_array -> 15
split_array -> 5
split_array -> 0
split_array -> 4
min_eating_speed -> 30
min_eating_speed -> 23
min_eating_speed -> 1
kth_in_table -> 1
kth_in_table -> 6
kth_in_table -> 312
max_min_distance -> 4
max_min_distance -> 1
=== hidden
gen split_array 1 60000
gen min_eating_speed 2 60000
---
split_array 60000 [29940513224, 4277509986, 60195864, 999993]
min_eating_speed 60000 999998860 200080676 29993
=== hidden
gen kth_in_table 3 0
gen max_min_distance 4 60000
---
kth_in_table 168028638 1 900000000
max_min_distance 60000 999976684 983441 1

## Hints
- `split_array`: the answer lies in `[max(nums), sum(nums)]`. `ok(cap)` greedily fills parts up to `cap` and checks that at most k parts are needed (fewer parts can always be split further, since any part can be cut).
- `min_eating_speed`: `ok(s) = sum(ceil(p / s)) <= h`, searched over `[1, max(piles)]`. Write `ceil` as `(p + s - 1) // s` or `-(-p // s)`.
- `kth_in_table`: the count of entries ≤ x is `sum(min(x // i, n) for i in 1..m)`. Find the smallest x with count ≥ k. That x is always a table entry.
- `max_min_distance`: `ok(d)` greedily places robots left to right. This predicate is True for small d, so search for the *last* True.

## Solution
```python
def _first_true(lo, hi, ok):
    while lo < hi:
        mid = (lo + hi) // 2
        if ok(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo

def split_array(nums, k):
    def ok(cap):
        parts, cur = 1, 0
        for x in nums:
            if cur + x > cap:
                parts += 1
                cur = 0
            cur += x
        return parts <= k
    return _first_true(max(nums), sum(nums), ok)

def min_eating_speed(piles, h):
    return _first_true(1, max(piles), lambda s: sum((p + s - 1) // s for p in piles) <= h)

def kth_in_table(m, n, k):
    if m > n:
        m, n = n, m                                   # iterate over the smaller side
    def ok(x):
        return sum(min(x // i, n) for i in range(1, m + 1)) >= k
    return _first_true(1, m * n, ok)

def max_min_distance(positions, c):
    p = sorted(positions)
    def fits(d):                                      # True for small d: monotone decreasing
        count, last = 1, p[0]
        for x in p[1:]:
            if x - last >= d:
                count += 1
                last = x
                if count >= c:
                    return True
        return count >= c
    # the first d that does NOT fit, minus one
    return _first_true(1, p[-1] - p[0] + 2, lambda d: not fits(d)) - 1
```

All four reduce optimisation to "is value x achievable?", with a predicate that's monotone in x:
- Larger capacities, speeds and thresholds only make the task easier. For the minimum distance, smaller distances are easier, so the predicate is inverted to search for the first infeasible value.
- Each check is a greedy O(n) pass (or an O(min(m, n)) count), and the search adds a log factor over the value range. `kth_in_table` never builds the 9·10⁸-entry table; it only counts how many entries are ≤ x.
- The result is a table entry because the smallest x with count ≥ k must be a value where the count jumps.
