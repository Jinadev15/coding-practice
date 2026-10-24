---
id: py-advanced-dp-suite
title: "Advanced DP: TSP Waypoints, Tree Independent Set, Burst Balloons, Digit DP"
difficulty: Hard
order: 1
tags: bitmask DP, Held-Karp, tree DP, interval DP, digit DP
time_limit: 5
---
## Statement
```python
def waypoint_tour(dist):
    """dist: n x n matrix (n <= 13). Shortest closed tour starting and ending at waypoint 0 that visits
    every waypoint exactly once. O(2^n * n^2) Held-Karp."""

def tree_max_independent(n, edges, values):
    """Tree with n nodes (0..n-1), n-1 edges. Max total value of a set of nodes with no two adjacent.
    n up to 200 000: the tree may be a long path, so don't recurse."""

def burst_balloons(nums):
    """Bursting balloon i earns nums[left] * nums[i] * nums[right] (neighbours at that time; out-of-range
    counts as 1). Return the maximum total over all burst orders. len(nums) <= 120."""

def count_no_adjacent_equal(N):
    """How many integers x with 0 <= x <= N have no two adjacent equal digits (in decimal, no leading zeros)?"""
```

Test lines are `(function_name, args)` literals or `gen NAME SEED N`.

## Starter
```python
from itertools import permutations

def waypoint_tour(dist):
    n = len(dist)
    best = float("inf")
    for p in permutations(range(1, n)):
        route = (0,) + p + (0,)
        best = min(best, sum(dist[a][b] for a, b in zip(route, route[1:])))
    return best if n > 1 else 0

def tree_max_independent(n, edges, values):
    return max(values, default=0)

def burst_balloons(nums):
    return 0

def count_no_adjacent_equal(N):
    return sum(1 for x in range(N + 1) if all(a != b for a, b in zip(str(x), str(x)[1:])))
```

## Driver
```python
import ast
import random
import sys

FUNCS = {f.__name__: f for f in (waypoint_tour, tree_max_independent, burst_balloons, count_no_adjacent_equal)}
for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    if line.startswith("gen "):
        _, name, seed, n = line.split()
        rng = random.Random(int(seed)); n = int(n)
        if name == "waypoint_tour":
            pts = [(rng.randrange(100), rng.randrange(100)) for _ in range(n)]
            d = [[abs(a[0] - b[0]) + abs(a[1] - b[1]) for b in pts] for a in pts]
            print(name, n, waypoint_tour(d))
        elif name == "tree_max_independent":
            edges = [(i, i - 1 if i % 3 else rng.randrange(i)) for i in range(1, n)]   # long paths + branches
            vals = [rng.randrange(1, 100) for _ in range(n)]
            print(name, n, tree_max_independent(n, edges, vals))
        elif name == "burst_balloons":
            print(name, n, burst_balloons([rng.randrange(0, 100) for _ in range(n)]))
        else:
            print(name, [count_no_adjacent_equal(x) for x in (10**18, 987654321987654321, 10**18 - 1)])
        continue
    name, args = ast.literal_eval(line)
    print(name, "->", FUNCS[name](*args))
```

## Tests
=== sample
("waypoint_tour", ([[0, 10, 15, 20], [10, 0, 35, 25], [15, 35, 0, 30], [20, 25, 30, 0]],))
("tree_max_independent", (4, [(0, 1), (0, 2), (1, 3)], [3, 2, 3, 3]))
("burst_balloons", ([3, 1, 5, 8],))
("count_no_adjacent_equal", (100,))
---
waypoint_tour -> 80
tree_max_independent -> 6
burst_balloons -> 167
count_no_adjacent_equal -> 91
=== hidden
("waypoint_tour", ([[0]],))
("waypoint_tour", ([[0, 4], [6, 0]],))
("waypoint_tour", ([[0, 1, 9], [9, 0, 1], [1, 9, 0]],))
("tree_max_independent", (1, [], [7]))
("tree_max_independent", (2, [(0, 1)], [5, 6]))
("tree_max_independent", (5, [(0, 1), (0, 2), (0, 3), (0, 4)], [10, 3, 3, 3, 3]))
("burst_balloons", ([],))
("burst_balloons", ([5],))
("burst_balloons", ([1, 5],))
("count_no_adjacent_equal", (0,))
("count_no_adjacent_equal", (9,))
("count_no_adjacent_equal", (11,))
("count_no_adjacent_equal", (1000,))
---
waypoint_tour -> 0
waypoint_tour -> 10
waypoint_tour -> 3
tree_max_independent -> 7
tree_max_independent -> 6
tree_max_independent -> 12
burst_balloons -> 0
burst_balloons -> 5
burst_balloons -> 10
count_no_adjacent_equal -> 1
count_no_adjacent_equal -> 10
count_no_adjacent_equal -> 11
count_no_adjacent_equal -> 820
=== hidden
gen waypoint_tour 1 13
gen tree_max_independent 2 200000
---
waypoint_tour 13 430
tree_max_independent 200000 6190499
=== hidden
gen burst_balloons 3 120
gen count_no_adjacent_equal 4 0
---
burst_balloons 120 44822385
count_no_adjacent_equal [168856464709124011, 168595884137868051, 168856464709124011]

## Hints
- **Held–Karp**: `dp[mask][v]` = the shortest path from 0 through exactly the set `mask` (which always contains 0), ending at v. The answer is `min(dp[full][v] + dist[v][0])`. For n = 1, the tour length is 0.
- **Tree DP without recursion**: get a DFS order with a stack, then process it in reverse. Keep `take[u] = value[u] + Σ skip[child]` and `skip[u] = Σ max(take[child], skip[child])`.
- **Burst balloons**: pad with 1s at both ends. `dp[i][j]` = the best for the open interval (i, j). Choose k as the **last** balloon to burst in it: `dp[i][k] + dp[k][j] + a[i]·a[k]·a[j]`.
- **Digit DP**: count the numbers ≤ N by digit position with states `(pos, prev_digit, tight, started)`. `started` handles the leading zeros, which don't count as digits.

## Solution
```python
from functools import lru_cache

def waypoint_tour(dist):
    n = len(dist)
    if n == 1:
        return 0
    INF = float("inf")
    full = 1 << n
    dp = [[INF] * n for _ in range(full)]
    dp[1][0] = 0
    for mask in range(1, full, 2):                  # odd masks: 0 is always visited
        row = dp[mask]
        for v in range(n):
            cur = row[v]
            if cur == INF:
                continue
            dv = dist[v]
            for u in range(1, n):
                if not mask >> u & 1:
                    nm = mask | 1 << u
                    if cur + dv[u] < dp[nm][u]:
                        dp[nm][u] = cur + dv[u]
    return min(dp[full - 1][v] + dist[v][0] for v in range(1, n))

def tree_max_independent(n, edges, values):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    parent = [-1] * n
    order, stack = [], [0]
    seen = [False] * n
    seen[0] = True
    while stack:
        u = stack.pop()
        order.append(u)
        for v in adj[u]:
            if not seen[v]:
                seen[v] = True
                parent[v] = u
                stack.append(v)
    take = list(values)
    skip = [0] * n
    for u in reversed(order):                        # children are processed before parents
        p = parent[u]
        if p >= 0:
            take[p] += skip[u]
            skip[p] += max(take[u], skip[u])
    return max(take[0], skip[0])

def burst_balloons(nums):
    a = [1] + list(nums) + [1]
    m = len(a)
    dp = [[0] * m for _ in range(m)]
    for length in range(2, m):                       # j - i
        for i in range(0, m - length):
            j = i + length
            ai_aj = a[i] * a[j]
            best = 0
            for k in range(i + 1, j):                # k: the last balloon burst in (i, j)
                v = dp[i][k] + dp[k][j] + ai_aj * a[k]
                if v > best:
                    best = v
            dp[i][j] = best
    return dp[0][m - 1]

def count_no_adjacent_equal(N):
    digits = list(map(int, str(N)))

    @lru_cache(maxsize=None)
    def go(pos, prev, tight, started):
        if pos == len(digits):
            return 1                                 # counts 0 too (no digits started)
        limit = digits[pos] if tight else 9
        total = 0
        for d in range(limit + 1):
            if started and d == prev:
                continue
            now_started = started or d != 0
            total += go(pos + 1, d if now_started else -1, tight and d == limit, now_started)
        return total

    return go(0, -1, True, False)
```

- **Held–Karp** replaces the (n−1)! orderings with 2ⁿ·n states. For n = 13, that's about 1.4 million transitions instead of 479 million permutations. Robots use it for exact visiting orders of small sets of inspection points.
- **Tree DP** in reverse DFS order guarantees children before parents, without recursion. That matters because a 200 000-node path would overflow the call stack.
- **Burst balloons** is interval DP where choosing the *last* balloon makes the subproblems independent: while the others burst, k stays as the fixed boundary between the two sides.
- **Digit DP** counts numbers up to 10¹⁸ in a few hundred states. The `tight` flag remembers whether the prefix still equals N's prefix, and `started` stops leading zeros from being treated as repeated digits.
