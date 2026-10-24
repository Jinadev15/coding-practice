---
id: py-route-planner
title: "Route Planner: Dijkstra, Path Counting, K-Stop Fares, Floyd–Warshall"
difficulty: Hard
order: 1
tags: Dijkstra, Bellman–Ford, Floyd–Warshall, path counting, heapq
time_limit: 3
---
## Statement
A delivery-robot route planner needs four shortest-path engines. Edges are directed `(u, v, w)` unless stated otherwise, and vertices are `0..n-1`.

```python
def dijkstra(n, edges, src):
    """Shortest distances from src (w >= 0). Unreachable vertices get -1. O((V + E) log V)."""

def count_shortest(n, edges, src, dst):
    """Number of distinct shortest src->dst paths, modulo 1_000_000_007 (w >= 1). 0 if unreachable."""

def cheapest_k_stops(n, edges, src, dst, k):
    """Cheapest cost from src to dst using at most k INTERMEDIATE vertices (at most k + 1 edges);
    -1 if none. Weights may be negative but there are no negative cycles."""

def best_city(n, edges, threshold):
    """UNDIRECTED edges. For each city, count the other cities within distance <= threshold.
    Return the city with the fewest such neighbours; ties go to the LARGEST index. n <= 150."""
```

Test lines are `(function_name, args)` literals or `gen NAME SEED N`.

## Starter
```python
def dijkstra(n, edges, src):
    INF = float("inf")
    dist = [INF] * n
    dist[src] = 0
    for _ in range(n):
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    return [d if d < INF else -1 for d in dist]

def count_shortest(n, edges, src, dst):
    return 0

def cheapest_k_stops(n, edges, src, dst, k):
    return -1

def best_city(n, edges, threshold):
    return n - 1
```

## Driver
```python
import ast
import random
import sys

FUNCS = {f.__name__: f for f in (dijkstra, count_shortest, cheapest_k_stops, best_city)}
for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    if line.startswith("gen "):
        _, name, seed, n = line.split()
        rng = random.Random(int(seed)); n = int(n)
        if name == "dijkstra":
            edges = [(rng.randrange(n), rng.randrange(n), rng.randrange(1, 1000)) for _ in range(4 * n)]
            d = dijkstra(n, edges, 0)
            print(name, n, sum(d), d.count(-1), max(d))
        elif name == "count_shortest":
            edges = []
            for i in range(n - 1):                     # a lattice-like DAG with many equal paths
                edges.append((i, i + 1, 1))
                if i + 2 < n:
                    edges.append((i, i + 2, 2))
            print(name, n, count_shortest(n, edges, 0, n - 1), count_shortest(n, edges, n - 1, 0))
        elif name == "cheapest_k_stops":
            edges = [(rng.randrange(n), rng.randrange(n), rng.randrange(-5, 100)) for _ in range(5 * n)]
            edges = [(u, v, w if w >= 0 or u < v else -w) for u, v, w in edges]   # negatives only forward: no cycles
            print(name, n, [cheapest_k_stops(n, edges, 0, n - 1, k) for k in (0, 2, 10, 50)])
        else:
            edges = [(rng.randrange(n), rng.randrange(n), rng.randrange(1, 50)) for _ in range(3 * n)]
            edges = [(u, v, w) for u, v, w in edges if u != v]
            print(name, n, best_city(n, edges, 40), best_city(n, edges, 5))
        continue
    name, args = ast.literal_eval(line)
    print(name, "->", FUNCS[name](*args))
```

## Tests
=== sample
("dijkstra", (4, [(0, 1, 4), (0, 2, 1), (2, 1, 2), (1, 3, 1)], 0))
("count_shortest", (4, [(0, 1, 1), (0, 2, 1), (1, 3, 1), (2, 3, 1)], 0, 3))
("cheapest_k_stops", (4, [(0, 1, 100), (1, 2, 100), (2, 3, 100), (0, 2, 500)], 0, 3, 1))
("best_city", (4, [(0, 1, 3), (1, 2, 1), (1, 3, 4), (2, 3, 1)], 4))
---
dijkstra -> [0, 3, 1, 4]
count_shortest -> 2
cheapest_k_stops -> 600
best_city -> 3
=== hidden
("dijkstra", (1, [], 0))
("dijkstra", (3, [(1, 2, 5)], 0))
("dijkstra", (3, [(0, 1, 0), (1, 2, 0)], 0))
("count_shortest", (2, [], 0, 1))
("count_shortest", (1, [], 0, 0))
("count_shortest", (5, [(0, 1, 2), (0, 2, 1), (2, 1, 1), (1, 4, 1), (0, 3, 3), (3, 4, 0)], 0, 4))
("cheapest_k_stops", (3, [(0, 1, 1), (1, 2, 1), (0, 2, 5)], 0, 2, 0))
("cheapest_k_stops", (3, [(0, 1, 1), (1, 2, 1), (0, 2, 5)], 0, 2, 1))
("cheapest_k_stops", (3, [(0, 1, 5), (1, 2, -4)], 0, 2, 1))
("cheapest_k_stops", (2, [], 0, 1, 3))
("best_city", (2, [], 1))
("best_city", (5, [(0, 1, 2), (0, 4, 8), (1, 2, 3), (1, 4, 2), (2, 3, 1), (3, 4, 1)], 2))
---
dijkstra -> [0]
dijkstra -> [0, -1, -1]
dijkstra -> [0, 0, 0]
count_shortest -> 0
count_shortest -> 1
count_shortest -> 3
cheapest_k_stops -> 5
cheapest_k_stops -> 2
cheapest_k_stops -> 1
cheapest_k_stops -> -1
best_city -> 1
best_city -> 0
=== hidden
gen dijkstra 1 100000
gen count_shortest 2 100000
---
dijkstra 100000 263121711 1937 5691
count_shortest 100000 911435502 0
=== hidden
gen cheapest_k_stops 3 2000
gen best_city 4 150
---
cheapest_k_stops 2000 [-1, -1, 80, 80]
best_city 150 58 149

## Hints
- **dijkstra**: a heap of `(dist, vertex)`; skip popped entries where `d > dist[u]`.
- **count_shortest**: run Dijkstra and also keep `ways`. On a strictly better distance, `ways[v] = ways[u]`; on an equal distance, `ways[v] += ways[u]`. Positive weights make this correct, because a vertex's count is final when it's popped. (The hidden test with a zero-weight edge is still fine: that edge leads into the target, which is never expanded further.)
- **cheapest_k_stops**: Bellman–Ford for k + 1 rounds, relaxing from a **copy** of the previous round's distances, so each round extends paths by exactly one edge.
- **best_city**: Floyd–Warshall (n ≤ 150), then count per row.

## Solution
```python
import heapq

MOD = 1_000_000_007

def _adj(n, edges):
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((v, w))
    return adj

def dijkstra(n, edges, src):
    adj = _adj(n, edges)
    INF = float("inf")
    dist = [INF] * n
    dist[src] = 0
    pq = [(0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return [d if d < INF else -1 for d in dist]

def count_shortest(n, edges, src, dst):
    adj = _adj(n, edges)
    INF = float("inf")
    dist, ways = [INF] * n, [0] * n
    dist[src], ways[src] = 0, 1
    pq = [(0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v], ways[v] = nd, ways[u]
                heapq.heappush(pq, (nd, v))
            elif nd == dist[v]:
                ways[v] = (ways[v] + ways[u]) % MOD
    return ways[dst] % MOD

def cheapest_k_stops(n, edges, src, dst, k):
    INF = float("inf")
    dist = [INF] * n
    dist[src] = 0
    for _ in range(k + 1):
        nxt = dist[:]                              # paths with one more edge, built from the last round only
        for u, v, w in edges:
            if dist[u] + w < nxt[v]:
                nxt[v] = dist[u] + w
        dist = nxt
    return dist[dst] if dist[dst] < INF else -1

def best_city(n, edges, threshold):
    INF = float("inf")
    d = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    for u, v, w in edges:
        if w < d[u][v]:
            d[u][v] = d[v][u] = w
    for k in range(n):
        dk = d[k]
        for i in range(n):
            dik = d[i][k]
            if dik == INF:
                continue
            di = d[i]
            for j in range(n):
                if dik + dk[j] < di[j]:
                    di[j] = dik + dk[j]
    best, best_count = -1, INF
    for i in range(n):
        c = sum(1 for j in range(n) if j != i and d[i][j] <= threshold)
        if c <= best_count:                        # <= : ties go to the larger index
            best, best_count = i, c
    return best
```

The four engines differ only in the **order** in which they relax edges:
- **Dijkstra** relaxes from the vertex with the smallest distance, which is safe only with non-negative weights. The stale-entry check replaces decrease-key.
- **Path counting** rides on Dijkstra: when vertices are settled in distance order, every shortest path into v comes through an already-settled predecessor, so counts accumulate correctly.
- **Bounded-edge Bellman–Ford** uses round-by-round copies. Relaxing in place would let one round chain several edges and break the k-stop limit. It also handles negative edges.
- **Floyd–Warshall** gives all pairs in O(n³), which suits n ≤ 150. Hoisting the rows `dk`/`di` into local variables is the standard CPython speed-up for the triple loop.
