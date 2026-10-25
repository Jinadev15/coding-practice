---
id: py-range-structures
title: "Range Structures: Inversions, Count Smaller, Range Add/Sum, Range Min"
difficulty: Hard
order: 1
tags: Fenwick tree, segment tree, lazy propagation, coordinate compression
time_limit: 6
---
## Statement
```python
def count_inversions(a):
    """Number of pairs i < j with a[i] > a[j]. O(n log n); values up to 10**9."""

def count_smaller_after(a):
    """For each i, how many j > i have a[j] < a[i]. Return the list. O(n log n)."""

def range_ops(n, ops):
    """Array of n zeros. ops: ("add", l, r, v) adds v to a[l..r-1]; ("sum", l, r) asks for sum a[l..r-1];
    ("min", l, r) asks for min a[l..r-1]. Return the list of answers in order. O(log n) per op."""
```

Test lines are `(function_name, args)` literals or `gen NAME SEED N`.

## Starter
```python
def count_inversions(a):
    n = len(a)
    return sum(1 for i in range(n) for j in range(i + 1, n) if a[i] > a[j])

def count_smaller_after(a):
    return [sum(1 for y in a[i + 1:] if y < x) for i, x in enumerate(a)]

def range_ops(n, ops):
    arr, out = [0] * n, []
    for op in ops:
        if op[0] == "add":
            _, l, r, v = op
            for i in range(l, r): arr[i] += v
        elif op[0] == "sum":
            out.append(sum(arr[op[1]:op[2]]))
        else:
            out.append(min(arr[op[1]:op[2]]))
    return out
```

## Driver
```python
import ast
import random
import sys

FUNCS = {f.__name__: f for f in (count_inversions, count_smaller_after, range_ops)}
for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    if line.startswith("gen "):
        _, name, seed, n = line.split()
        rng = random.Random(int(seed)); n = int(n)
        if name == "count_inversions":
            a = [rng.randrange(10**9) for _ in range(n)]
            print(name, n, count_inversions(a), count_inversions(sorted(a)), count_inversions(sorted(a, reverse=True)))
        elif name == "count_smaller_after":
            a = [rng.randrange(-10**9, 10**9) for _ in range(n)]
            r = count_smaller_after(a)
            print(name, n, sum(r), r[:5])
        else:
            ops = []
            for _ in range(n):
                l = rng.randrange(n); r = rng.randrange(l + 1, n + 1)
                t = rng.random()
                if t < 0.4: ops.append(("add", l, r, rng.randrange(-100, 101)))
                elif t < 0.7: ops.append(("sum", l, r))
                else: ops.append(("min", l, r))
            res = range_ops(n, ops)
            print(name, n, len(res), sum(res), res[:4])
        continue
    name, args = ast.literal_eval(line)
    print(name, "->", FUNCS[name](*args))
```

## Tests
=== sample
("count_inversions", ([2, 4, 1, 3, 5],))
("count_smaller_after", ([5, 2, 6, 1],))
("range_ops", (5, [("add", 1, 4, 3), ("sum", 0, 5), ("min", 0, 5), ("add", 0, 2, -5), ("min", 0, 3), ("sum", 1, 2)]))
---
count_inversions -> 3
count_smaller_after -> [2, 1, 1, 0]
range_ops -> [9, 0, -5, -2]
=== hidden
("count_inversions", ([],))
("count_inversions", ([1, 1, 1],))
("count_inversions", ([3, 2, 1],))
("count_smaller_after", ([],))
("count_smaller_after", ([-1, -1],))
("count_smaller_after", ([1, 9, 7, 8, 5],))
("range_ops", (1, [("sum", 0, 1), ("add", 0, 1, 7), ("min", 0, 1)]))
("range_ops", (4, [("add", 0, 4, 2), ("add", 2, 3, -10), ("min", 0, 2), ("min", 1, 4), ("sum", 0, 4)]))
---
count_inversions -> 0
count_inversions -> 0
count_inversions -> 3
count_smaller_after -> []
count_smaller_after -> [0, 0]
count_smaller_after -> [0, 3, 1, 1, 0]
range_ops -> [0, 7]
range_ops -> [2, -8, -2]
=== hidden
gen count_inversions 1 200000
gen count_smaller_after 2 200000
---
count_inversions 200000 10007393422 0 19999899981
count_smaller_after 200000 9983300843 [185414, 182406, 12074, 19506, 18062]
=== hidden
gen range_ops 3 60000
---
range_ops 60000 35946 540656380261 [0, 0, 83, 1335462]

## Hints
- **Coordinate compression**: `ranks = {v: i for i, v in enumerate(sorted(set(a)))}`.
- **Inversions**: scan left to right with a Fenwick tree of counts. Element x adds `seen_so_far − (count of values ≤ x)`.
- **Count smaller after**: scan right to left; the answer is `prefix(rank[x])`, the count of strictly smaller values already inserted.
- **range_ops**: a segment tree with lazy "add" tags, where each node stores the segment's sum **and** min. An add of v to a full segment raises the sum by `v·len` and the min by `v`.

## Solution
```python
def _compress(a):
    return {v: i for i, v in enumerate(sorted(set(a)))}

def count_inversions(a):
    rank = _compress(a)
    n = len(rank)
    tree = [0] * (n + 1)
    inv = 0
    for seen, x in enumerate(a):
        i = rank[x] + 1
        s, j = 0, i                      # count of values <= x seen so far
        while j:
            s += tree[j]; j -= j & -j
        inv += seen - s
        while i <= n:
            tree[i] += 1; i += i & -i
    return inv

def count_smaller_after(a):
    rank = _compress(a)
    n = len(rank)
    tree = [0] * (n + 1)
    out = [0] * len(a)
    for idx in range(len(a) - 1, -1, -1):
        r = rank[a[idx]]
        s, j = 0, r                      # ranks < r: strictly smaller
        while j:
            s += tree[j]; j -= j & -j
        out[idx] = s
        i = r + 1
        while i <= n:
            tree[i] += 1; i += i & -i
    return out

def range_ops(n, ops):
    size = 1
    while size < n:
        size *= 2
    INF = float("inf")
    sm = [0] * (2 * size)
    mn = [0] * size + [0] * n + [INF] * (size - n)   # padding leaves never win a min
    for i in range(size - 1, 0, -1):
        mn[i] = min(mn[2 * i], mn[2 * i + 1])
    lz = [0] * (2 * size)

    def apply(node, length, v):
        sm[node] += v * length
        mn[node] += v
        lz[node] += v

    def push(node, length):
        if lz[node]:
            half = length // 2
            apply(2 * node, half, lz[node])
            apply(2 * node + 1, half, lz[node])
            lz[node] = 0

    def add(l, r, v, node, lo, hi):
        if r <= lo or hi <= l:
            return
        if l <= lo and hi <= r:
            apply(node, hi - lo, v)             # fully covered nodes lie inside [0, n): r <= n
            return
        push(node, hi - lo)
        mid = (lo + hi) // 2
        add(l, r, v, 2 * node, lo, mid)
        add(l, r, v, 2 * node + 1, mid, hi)
        sm[node] = sm[2 * node] + sm[2 * node + 1]
        mn[node] = min(mn[2 * node], mn[2 * node + 1])

    def query(l, r, node, lo, hi):
        if r <= lo or hi <= l:
            return 0, INF
        if l <= lo and hi <= r:
            return sm[node], mn[node]
        push(node, hi - lo)
        mid = (lo + hi) // 2
        s1, m1 = query(l, r, 2 * node, lo, mid)
        s2, m2 = query(l, r, 2 * node + 1, mid, hi)
        return s1 + s2, min(m1, m2)

    out = []
    for op in ops:
        if op[0] == "add":
            add(op[1], op[2], op[3], 1, 0, size)
        else:
            s, m = query(op[1], op[2], 1, 0, size)
            out.append(s if op[0] == "sum" else m)
    return out
```

- **Inversions and count-smaller** turn a pairwise comparison into prefix counting over value ranks. A Fenwick tree answers "how many of the values seen so far are ≤ x" in O(log n), so the total is O(n log n). Coordinate compression maps values up to 10⁹ to ranks 0..n−1.
- **range_ops** needs range updates *and* two different aggregates. One lazy tag ("add v to everything below") updates both: the sum grows by v × (the number of real elements) and the min by v. Tags are pushed to the children only when a later operation needs to look inside a node, which keeps every operation O(log n).
- The tree is padded to a power of two, and the padding leaves hold `inf` for the min. Since every range ends at r ≤ n, a fully covered node never contains padding, so lazy tags never touch it.
