---
id: m3-task-allocation
title: Optimal Multi-Robot Task Allocation
difficulty: Expert
order: 2
tags: assignment problem, Hungarian algorithm, bipartite matching, Hopcroft-Karp, binary search, optimization
time_limit: 10
---
## Statement
A fleet manager must assign **n robots to m tasks** (each robot does at most one task, each task gets at most one robot). Implement both classic objectives **without** SciPy or NumPy. The judge compares your results with brute force and with `scipy.optimize.linear_sum_assignment`.

1. **`min_cost_assignment(cost: list[list[int]]) -> tuple[int, list[int]]`**: an `n×m` matrix with `n <= m`. Assign every robot to a distinct task, minimizing the **total cost**. Return `(total, assignment)`, where `assignment[i]` is robot i's task. Implement the **Hungarian algorithm** (Kuhn-Munkres with potentials) in O(n²·m). The hidden tests include 300×300.
2. **`bottleneck_assignment(cost) -> tuple[int, list[int]]`**: assign every robot to a distinct task, minimizing the **maximum** single cost (the makespan when robots work in parallel). Return the bottleneck value and **any** assignment achieving it. Use binary search over the sorted distinct costs, plus a maximum bipartite matching (**Hopcroft-Karp**).
3. **`max_tasks_within(cost, budget) -> int`**: the maximum number of robot-task pairs (a matching) using only pairs with `cost <= budget`.

Costs are non-negative integers. If several assignments are optimal, any is accepted. The judge checks the value and the validity.

## Starter
```python
from itertools import permutations


def min_cost_assignment(cost):
    n, m = len(cost), len(cost[0])
    best = None
    for perm in permutations(range(m), n):          # brute force: n! (fine for 6, hopeless for 300)
        total = sum(cost[i][perm[i]] for i in range(n))
        if best is None or total < best[0]:
            best = (total, list(perm))
    return best


def bottleneck_assignment(cost):
    total, assign = min_cost_assignment(cost)
    return max(cost[i][assign[i]] for i in range(len(cost))), assign


def max_tasks_within(cost, budget):
    return sum(1 for row in cost if min(row) <= budget)
```

## Driver
```python
import sys
from itertools import permutations
from scipy.optimize import linear_sum_assignment
import numpy as np

def gen(n, m, seed, hi=1000):
    x = seed; out = []
    for i in range(n):
        row = []
        for j in range(m):
            x = (x * 1103515245 + 12345) % (1 << 31)
            row.append(x % hi)
        out.append(row)
    return out

def check(cost, assign):
    return len(assign) == len(cost) and len(set(assign)) == len(assign) and all(0 <= a < len(cost[0]) for a in assign)

for line in sys.stdin.read().splitlines():
    p = line.split()
    if not p: continue
    if p[0] == "small":
        c = [[4, 1, 3], [2, 0, 5], [3, 2, 2]]
        t, a = min_cost_assignment(c); print("min", t, check(c, a), sum(c[i][a[i]] for i in range(3)) == t)
        b, a = bottleneck_assignment(c); print("bottleneck", b, check(c, a), max(c[i][a[i]] for i in range(3)) == b)
        print("within 1:", max_tasks_within(c, 1), "within 2:", max_tasks_within(c, 2), "within 0:", max_tasks_within(c, 0))
        rect = [[7, 2, 9, 4], [3, 8, 1, 6]]
        t, a = min_cost_assignment(rect); print("rect", t, a if check(rect, a) else "invalid")
        print("single", min_cost_assignment([[5, 3, 8]]), bottleneck_assignment([[5, 3, 8]])[0])
    elif p[0] == "brute":
        ok = True
        for seed in range(1, 60):
            n = 1 + seed % 6; m = n + seed % 3
            c = gen(n, m, seed, hi=50)
            best = min(sum(c[i][q[i]] for i in range(n)) for q in permutations(range(m), n))
            bott = min(max(c[i][q[i]] for i in range(n)) for q in permutations(range(m), n))
            t, a = min_cost_assignment(c); b, a2 = bottleneck_assignment(c)
            ok &= t == best and check(c, a) and sum(c[i][a[i]] for i in range(n)) == t
            ok &= b == bott and check(c, a2) and max(c[i][a2[i]] for i in range(n)) == b
        print("brute force agreement:", ok)
    elif p[0] == "big":
        n, m, seed = map(int, p[1:4])
        c = gen(n, m, seed)
        t, a = min_cost_assignment(c)
        r, k = linear_sum_assignment(np.array(c))
        b, a2 = bottleneck_assignment(c)
        print("total", t, "scipy", int(np.array(c)[r, k].sum()), "valid", check(c, a), "bottleneck", b, "valid", check(c, a2) and max(c[i][a2[i]] for i in range(n)) == b)
        print("pairs within 50:", max_tasks_within(c, 50), "within 10:", max_tasks_within(c, 10))
```

## Tests
=== sample
small
---
min 5 True True
bottleneck 2 True True
within 1: 1 within 2: 3 within 0: 1
rect 3 [1, 2]
single (3, [1]) 3
=== hidden
brute
---
brute force agreement: True
=== hidden
big 120 150 7
---
total 938 scipy 938 valid True bottleneck 32 valid True
pairs within 50: 120 within 10: 96
=== hidden
big 300 300 42
---
total 1542 scipy 1542 valid True bottleneck 27 valid True
pairs within 50: 300 within 10: 282

## Hints
- **Hungarian with potentials** (the e-maxx formulation, 1-indexed): keep potentials `u[0..n]` and `v[0..m]`, `p[j]` (the robot matched to task j) and `way[j]`. For each robot, run a Dijkstra-like scan over the tasks using the reduced costs `cost[i][j] − u[i] − v[j]`, then augment along `way`. It's O(n²m) overall.
- **Bottleneck**: sort the distinct costs. For a threshold T, a perfect assignment exists exactly when the bipartite graph of edges with `cost ≤ T` has a matching of size n. Binary search for the smallest such T.
- **Hopcroft-Karp**: alternate a BFS that builds layers from the free robots with a DFS that finds vertex-disjoint shortest augmenting paths. It's O(E√V). An iterative DFS avoids recursion limits at 300 robots.

## Solution
```python
from collections import deque

INF = float("inf")


def min_cost_assignment(cost):
    n, m = len(cost), len(cost[0])
    u, v = [0] * (n + 1), [0] * (m + 1)
    p, way = [0] * (m + 1), [0] * (m + 1)          # p[j]: robot matched to task j (1-based, 0 = free)
    for i in range(1, n + 1):
        p[0] = i
        j0 = 0
        minv = [INF] * (m + 1)
        used = [False] * (m + 1)
        while True:
            used[j0] = True
            i0, delta, j1 = p[j0], INF, 0
            row = cost[i0 - 1]
            ui0 = u[i0]
            for j in range(1, m + 1):
                if not used[j]:
                    cur = row[j - 1] - ui0 - v[j]
                    if cur < minv[j]:
                        minv[j], way[j] = cur, j0
                    if minv[j] < delta:
                        delta, j1 = minv[j], j
            for j in range(m + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        while j0:                                    # augment along the alternating path
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
    assign = [0] * n
    for j in range(1, m + 1):
        if p[j]:
            assign[p[j] - 1] = j - 1
    return sum(cost[i][assign[i]] for i in range(n)), assign


def _max_matching(n, m, adj):
    """Hopcroft-Karp. adj[i] = list of tasks for robot i. Returns (size, match_robot)."""
    match_l, match_r = [-1] * n, [-1] * m
    dist = [0] * n
    def bfs():
        q = deque()
        found = False
        for i in range(n):
            if match_l[i] == -1:
                dist[i] = 0
                q.append(i)
            else:
                dist[i] = -1
        while q:
            i = q.popleft()
            for j in adj[i]:
                k = match_r[j]
                if k == -1:
                    found = True
                elif dist[k] == -1:
                    dist[k] = dist[i] + 1
                    q.append(k)
        return found
    def dfs(root):                                   # iterative DFS along BFS layers
        stack = [(root, iter(adj[root]))]
        path = []
        while stack:
            i, it = stack[-1]
            advanced = False
            for j in it:
                k = match_r[j]
                if k == -1:
                    path.append((i, j))
                    for a, b in path:                # flip the augmenting path
                        match_l[a], match_r[b] = b, a
                    return True
                if dist[k] == dist[i] + 1:
                    path.append((i, j))
                    stack.append((k, iter(adj[k])))
                    advanced = True
                    break
            if not advanced:
                dist[i] = -1                         # dead end for this phase
                stack.pop()
                if path:
                    path.pop()
        return False
    size = 0
    while bfs():
        for i in range(n):
            if match_l[i] == -1 and dfs(i):
                size += 1
    return size, match_l


def max_tasks_within(cost, budget):
    n, m = len(cost), len(cost[0])
    adj = [[j for j in range(m) if cost[i][j] <= budget] for i in range(n)]
    return _max_matching(n, m, adj)[0]


def bottleneck_assignment(cost):
    n, m = len(cost), len(cost[0])
    values = sorted({c for row in cost for c in row})
    lo, hi = 0, len(values) - 1
    best = None
    while lo <= hi:
        mid = (lo + hi) // 2
        t = values[mid]
        size, match = _max_matching(n, m, [[j for j in range(m) if cost[i][j] <= t] for i in range(n)])
        if size == n:
            best, hi = (t, match), mid - 1
        else:
            lo = mid + 1
    return best[0], list(best[1])
```

- **The assignment problem** is linear programming with a special structure. The Hungarian algorithm keeps **dual potentials** `u`, `v` so that the reduced costs stay non-negative, and grows the matching robot by robot along shortest augmenting paths. That gives O(n²m) instead of the n! of brute force (300! is beyond astronomical).
- **The bottleneck objective is different**: minimizing the *maximum* cost is a feasibility question ("can everyone be served within T?"). It's monotone in T, so binary search over the distinct cost values combined with a maximum-matching test solves it.
- **Hopcroft-Karp** finds a maximum bipartite matching in O(E√V) by augmenting along many vertex-disjoint shortest paths per phase. The DFS is iterative, so 300-robot instances don't hit Python's recursion limit.
- **Validation against independent oracles**: brute force on small instances and SciPy's `linear_sum_assignment` on large ones. That's how you test an optimization algorithm.
