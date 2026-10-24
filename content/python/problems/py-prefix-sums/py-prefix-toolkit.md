---
id: py-prefix-toolkit
title: "Prefix-Sum Toolkit: Divisible Subarrays, Integral Image, Overlaps"
difficulty: Hard
order: 1
tags: prefix sums, hashing, 2-D prefix sums, difference arrays, sweep line
---
## Statement
Implement four prefix-sum tools, each with the stated complexity:

```python
def count_divisible_subarrays(a, m):
    """Number of non-empty subarrays whose sum is divisible by m (m >= 1, values may be negative). O(n)."""

def longest_zero_sum(a):
    """Length of the longest subarray with sum 0 (0 if none). O(n)."""

def rect_sums(grid, queries):
    """grid: R x C ints. queries: (r1, c1, r2, c2) INCLUSIVE corners. Return the list of sums.
    O(R*C + Q) using a summed-area table (integral image)."""

def max_overlap(intervals):
    """intervals: (start, end) half-open [start, end). Max number covering a single point. O(n log n)."""
```

Test lines are `(function_name, args)` literals or `gen NAME SEED N`.

## Starter
```python
def count_divisible_subarrays(a, m):
    n = len(a)
    return sum(1 for i in range(n) for j in range(i + 1, n + 1) if sum(a[i:j]) % m == 0)

def longest_zero_sum(a):
    n = len(a)
    return max((j - i for i in range(n) for j in range(i + 1, n + 1) if sum(a[i:j]) == 0), default=0)

def rect_sums(grid, queries):
    return [sum(grid[r][c] for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)) for r1, c1, r2, c2 in queries]

def max_overlap(intervals):
    best = 0
    for s, _ in intervals:
        best = max(best, sum(1 for a, b in intervals if a <= s < b))
    return best
```

## Driver
```python
import ast
import random
import sys

FUNCS = {f.__name__: f for f in (count_divisible_subarrays, longest_zero_sum, rect_sums, max_overlap)}
for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    if line.startswith("gen "):
        _, name, seed, n = line.split()
        rng = random.Random(int(seed)); n = int(n)
        if name == "count_divisible_subarrays":
            a = [rng.randrange(-1000, 1000) for _ in range(n)]
            print(name, n, count_divisible_subarrays(a, 7), count_divisible_subarrays(a, 1000))
        elif name == "longest_zero_sum":
            a = [rng.choice((-2, -1, 1, 2)) for _ in range(n)]
            print(name, n, longest_zero_sum(a))
        elif name == "rect_sums":
            R = C = n
            g = [[rng.randrange(-9, 10) for _ in range(C)] for _ in range(R)]
            qs = []
            for _ in range(100000):
                r1, r2 = sorted((rng.randrange(R), rng.randrange(R)))
                c1, c2 = sorted((rng.randrange(C), rng.randrange(C)))
                qs.append((r1, c1, r2, c2))
            res = rect_sums(g, qs)
            print(name, n, len(res), sum(res), res[:4])
        else:
            iv = []
            for _ in range(n):
                s = rng.randrange(10**9)
                iv.append((s, s + rng.randrange(1, 10**7)))
            print(name, n, max_overlap(iv))
        continue
    name, args = ast.literal_eval(line)
    print(name, "->", FUNCS[name](*args))
```

## Tests
=== sample
("count_divisible_subarrays", ([4, 5, 0, -2, -3, 1], 5))
("longest_zero_sum", ([15, -2, 2, -8, 1, 7, 10, 23],))
("rect_sums", ([[3, 0, 1], [5, 6, 3], [1, 2, 0]], [(0, 0, 2, 2), (1, 1, 2, 2), (0, 2, 0, 2)]))
("max_overlap", ([(1, 4), (2, 5), (4, 6), (5, 7)],))
---
count_divisible_subarrays -> 7
longest_zero_sum -> 5
rect_sums -> [21, 11, 1]
max_overlap -> 2
=== hidden
("count_divisible_subarrays", ([], 3))
("count_divisible_subarrays", ([0, 0, 0], 4))
("count_divisible_subarrays", ([-1, 2, 9], 2))
("count_divisible_subarrays", ([5], 1))
("longest_zero_sum", ([],))
("longest_zero_sum", ([1, 2, 3],))
("longest_zero_sum", ([0],))
("longest_zero_sum", ([1, -1, 1, -1],))
("rect_sums", ([[7]], [(0, 0, 0, 0)]))
("rect_sums", ([[1, 2], [3, 4]], [(0, 1, 1, 1), (1, 0, 1, 1), (0, 0, 1, 1)]))
("max_overlap", ([],))
("max_overlap", ([(1, 2), (2, 3), (3, 4)],))
("max_overlap", ([(0, 10), (0, 10), (5, 6)],))
---
count_divisible_subarrays -> 0
count_divisible_subarrays -> 6
count_divisible_subarrays -> 2
count_divisible_subarrays -> 1
longest_zero_sum -> 0
longest_zero_sum -> 0
longest_zero_sum -> 1
longest_zero_sum -> 4
rect_sums -> [7]
rect_sums -> [6, 7, 10]
max_overlap -> 0
max_overlap -> 1
max_overlap -> 3
=== hidden
gen count_divisible_subarrays 1 200000
gen longest_zero_sum 2 200000
gen rect_sums 3 600
gen max_overlap 4 200000
---
count_divisible_subarrays 200000 2857193345 20004749
longest_zero_sum 200000 141181
rect_sums 600 100000 79067836 [3123, 2793, -162, 2580]
max_overlap 200000 1122

## Hints
- **Divisible**: two prefixes with the same remainder `P % m` bound a divisible subarray. Count remainders in a dict starting with `{0: 1}`. Python's `%` is always non-negative for positive m, so negatives just work. (In C/Java you'd need `((x % m) + m) % m`.)
- **Longest zero sum**: store the **first** index of each prefix value (starting with `{0: -1}`). When a prefix repeats at i, the candidate length is `i - first[P]`.
- **rect_sums**: build `S` of size (R+1)×(C+1), then answer with `S[r2+1][c2+1] - S[r1][c2+1] - S[r2+1][c1] + S[r1][c1]`.
- **max_overlap**: create events `(start, +1)` and `(end, -1)`, and sort so that at equal coordinates the `-1` comes first, because half-open intervals don't overlap at their endpoints.

## Solution
```python
from collections import defaultdict

def count_divisible_subarrays(a, m):
    seen = defaultdict(int)
    seen[0] = 1
    total = p = 0
    for x in a:
        p = (p + x) % m
        total += seen[p]
        seen[p] += 1
    return total

def longest_zero_sum(a):
    first = {0: -1}
    p = best = 0
    for i, x in enumerate(a):
        p += x
        if p in first:
            best = max(best, i - first[p])
        else:
            first[p] = i                      # keep the FIRST index: it gives the longest span
    return best

def rect_sums(grid, queries):
    R = len(grid)
    C = len(grid[0]) if R else 0
    S = [[0] * (C + 1) for _ in range(R + 1)]
    for i in range(R):
        row, Si, Sp = 0, S[i + 1], S[i]
        gi = grid[i]
        for j in range(C):
            row += gi[j]
            Si[j + 1] = Sp[j + 1] + row
    return [S[r2 + 1][c2 + 1] - S[r1][c2 + 1] - S[r2 + 1][c1] + S[r1][c1] for r1, c1, r2, c2 in queries]

def max_overlap(intervals):
    events = []
    for s, e in intervals:
        events.append((s, 1))
        events.append((e, -1))
    events.sort()                             # (x, -1) sorts before (x, 1): ends close before starts open
    cur = best = 0
    for _, d in events:
        cur += d
        best = max(best, cur)
    return best
```

The one idea behind all four is to **turn range questions into differences of prefixes**:
- A subarray sum is `P[r] − P[l]`, so "divisible by m" means equal remainders, and "zero" means equal prefix values. Hash maps find the matching earlier prefixes in O(1).
- The summed-area table answers any rectangle in four lookups via inclusion–exclusion. That's the integral image used for box filters and Haar features in vision, and for footprint checks on occupancy grids.
- The sweep line is a difference array over sorted coordinates. The event tie-break encodes the half-open semantics: an interval ending at x and another starting at x don't overlap.
