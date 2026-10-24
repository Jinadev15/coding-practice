---
id: py-speed-up-slow-code
title: Make It Fast — From O(n²) to O(n)
difficulty: Medium
order: 1
tags: complexity, sets, dicts, hidden costs
time_limit: 2
---
## Statement
The starter code is **correct** but quadratic, and it times out on the hidden tests (n up to 200 000). Rewrite each function so it runs in O(n) or O(n log n) and returns exactly the same results.

```python
def common_items(a, b):
    """Items of a that also occur in b, in a's order, keeping a's duplicates."""

def dedupe_keep_order(a):
    """a without repeated values, keeping each value's first occurrence."""

def count_pairs_with_diff(a, k):
    """Number of index pairs i < j with |a[i] - a[j]| == k (k >= 0)."""

def first_repeat_window(a, d):
    """Smallest index j such that a[j] == a[i] for some i with j - d <= i < j; -1 if none."""
```

Each test line is either a Python literal `(function_name, args)`, or `gen NAME SEED N`, which runs a function on large random data and prints a short summary.

## Starter
```python
def common_items(a, b):
    return [x for x in a if x in b]

def dedupe_keep_order(a):
    out = []
    for x in a:
        if x not in out:
            out.append(x)
    return out

def count_pairs_with_diff(a, k):
    n = len(a)
    return sum(1 for i in range(n) for j in range(i + 1, n) if abs(a[i] - a[j]) == k)

def first_repeat_window(a, d):
    for j in range(len(a)):
        for i in range(max(0, j - d), j):
            if a[i] == a[j]:
                return j
    return -1
```

## Driver
```python
import ast
import random
import sys

FUNCS = {f.__name__: f for f in (common_items, dedupe_keep_order, count_pairs_with_diff, first_repeat_window)}
for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    if line.startswith("gen "):
        _, name, seed, n = line.split()
        rng = random.Random(int(seed))
        n = int(n)
        a = [rng.randrange(n) for _ in range(n)]
        if name == "common_items":
            b = [rng.randrange(n) for _ in range(n)]
            r = common_items(a, b)
            print(name, n, len(r), sum(r) % 1000003)
        elif name == "dedupe_keep_order":
            r = dedupe_keep_order(a)
            print(name, n, len(r), r[:3], r[-3:])
        elif name == "count_pairs_with_diff":
            a = [rng.randrange(n // 10 + 1) for _ in range(n)]
            print(name, n, count_pairs_with_diff(a, 0), count_pairs_with_diff(a, 3))
        elif name == "first_repeat_window":
            a = list(range(n)); rng.shuffle(a); a.append(a[n // 2])
            print(name, n, first_repeat_window(a, n // 3), first_repeat_window(a, n))
        continue
    name, args = ast.literal_eval(line)
    print(name, "->", FUNCS[name](*args))
```

## Tests
=== sample
("common_items", ([3, 1, 3, 2, 5], [3, 5, 7]))
("dedupe_keep_order", ([4, 1, 4, 2, 1, 3],))
("count_pairs_with_diff", ([1, 5, 3, 4, 2], 2))
("count_pairs_with_diff", ([1, 1, 1], 0))
("first_repeat_window", ([1, 2, 3, 1, 2], 2))
("first_repeat_window", ([1, 2, 3, 1, 2], 3))
---
common_items -> [3, 3, 5]
dedupe_keep_order -> [4, 1, 2, 3]
count_pairs_with_diff -> 3
count_pairs_with_diff -> 3
first_repeat_window -> -1
first_repeat_window -> 3
=== hidden
("common_items", ([], [1]))
("common_items", ([1, 2], []))
("common_items", ([2, 2, 2], [2]))
("dedupe_keep_order", ([],))
("dedupe_keep_order", (["b", "a", "b", "c", "a"],))
("count_pairs_with_diff", ([7], 0))
("count_pairs_with_diff", ([1, 2, 2, 3, 3, 3], 1))
("count_pairs_with_diff", ([5, 5, 5, 5], 0))
("first_repeat_window", ([], 3))
("first_repeat_window", ([1, 1], 0))
("first_repeat_window", ([1, 1], 1))
---
common_items -> []
common_items -> []
common_items -> [2, 2, 2]
dedupe_keep_order -> []
dedupe_keep_order -> ['b', 'a', 'c']
count_pairs_with_diff -> 0
count_pairs_with_diff -> 8
count_pairs_with_diff -> 6
first_repeat_window -> -1
first_repeat_window -> -1
first_repeat_window -> 1
=== hidden
gen common_items 1 200000
gen dedupe_keep_order 2 200000
gen count_pairs_with_diff 3 200000
gen first_repeat_window 4 200000
---
common_items 200000 126520 672993
dedupe_keep_order 200000 126308 [14824, 24008, 22248] [67446, 108594, 70388]
count_pairs_with_diff 200000 998545 2000887
first_repeat_window 200000 -1 200000

## Hints
- `common_items`: build `set(b)` once, so each membership test is O(1).
- `dedupe_keep_order`: track a `seen` set, or use `list(dict.fromkeys(a))` (dicts keep insertion order).
- `count_pairs_with_diff`: use a `Counter`. For k = 0, each value with count c contributes c·(c−1)/2 pairs. For k > 0, sum `cnt[v] * cnt[v + k]`.
- `first_repeat_window`: remember the **last index** of each value in a dict. At j, a repeat exists if `last[a[j]] >= j - d`.

## Solution
```python
from collections import Counter

def common_items(a, b):
    bs = set(b)                                  # O(|b|) once, then O(1) lookups
    return [x for x in a if x in bs]

def dedupe_keep_order(a):
    return list(dict.fromkeys(a))                # insertion-ordered keys = first occurrences

def count_pairs_with_diff(a, k):
    cnt = Counter(a)
    if k == 0:
        return sum(c * (c - 1) // 2 for c in cnt.values())
    return sum(c * cnt[v + k] for v, c in cnt.items() if v + k in cnt)

def first_repeat_window(a, d):
    last = {}
    for j, x in enumerate(a):
        if x in last and last[x] >= j - d:
            return j
        last[x] = j
    return -1
```

Each rewrite replaces a **linear search inside a loop** with a constant-time hash lookup:
- `x in b` on a list → a set.
- `x not in out` → a seen-set (here, a dict that also preserves order).
- All pairs → counting: pairs with difference k pair up the count of v with the count of v + k.
- A backwards window scan → "the last index of each value".

All four become O(n). On n = 200 000 that's the difference between about 0.1 s and hours. This "find the hidden O(n) inside the loop" review is the most valuable performance habit in Python.
