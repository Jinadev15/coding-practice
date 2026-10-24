# Shortest Paths

Finding the cheapest route through a weighted graph is one of the most applied problems in computer science. It shows up in GPS navigation, network routing (OSPF uses Dijkstra), robot path planning on costmaps (Dijkstra and A*), currency arbitrage detection (Bellman–Ford on log rates), and game AI. The right algorithm depends on the edge weights: unweighted, non-negative, possibly negative, or all pairs.

## 1. Choosing the algorithm

| Graph | Algorithm | Time |
|---|---|---|
| unweighted | BFS | O(V + E) |
| weights 0/1 | 0-1 BFS (deque) | O(V + E) |
| non-negative weights | **Dijkstra** (binary heap) | O((V + E) log V) |
| non-negative + a good heuristic, single goal | **A\*** | often far less than Dijkstra |
| negative weights, single source | **Bellman–Ford** (detects negative cycles) | O(V·E) |
| DAG, any weights | relax in topological order | O(V + E) |
| all pairs, small V | **Floyd–Warshall** | O(V³) |

## 2. Relaxation: the common core

Every algorithm repeatedly **relaxes** edges: if going through u improves v, update it.

```python
if dist[u] + w < dist[v]:
    dist[v] = dist[u] + w
    parent[v] = u
```

The algorithms differ only in the **order** in which they relax edges.

## 3. Dijkstra

```python
import heapq

def dijkstra(adj, src):
    """adj[u] = [(v, w)], with w >= 0. Returns (dist, parent)."""
    dist = {src: 0}
    parent = {src: None}
    pq = [(0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue                          # stale entry (lazy deletion)
        for v, w in adj[u]:
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                parent[v] = u
                heapq.heappush(pq, (nd, v))
    return dist, parent

def path_to(parent, t):
    out = []
    while t is not None:
        out.append(t)
        t = parent[t]
    return out[::-1]
```

> [!KEY]
> **Why it's correct**: when a vertex u is popped with the smallest tentative distance, no other path can reach u more cheaply. Any alternative would leave the settled set through some vertex already in the queue with distance ≥ d, and continuing along **non-negative** edges can't make it smaller. With a negative edge, that argument fails and Dijkstra can return wrong answers.

**Early exit**: when finding a path to a single target, stop as soon as the target is popped.

## 4. A*: Dijkstra with a sense of direction

A* orders the queue by `f(v) = g(v) + h(v)`, where g is the cost so far and h a **heuristic** estimate of the remaining cost:

```python
def astar(grid, start, goal):
    R, C = len(grid), len(grid[0])
    h = lambda p: abs(p[0] - goal[0]) + abs(p[1] - goal[1])     # Manhattan: admissible for 4-moves, unit cost
    g = {start: 0}
    pq = [(h(start), 0, start)]
    while pq:
        f, d, u = heapq.heappop(pq)
        if u == goal:
            return d
        if d > g[u]:
            continue
        r, c = u
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < R and 0 <= nc < C and grid[nr][nc] != "#":
                nd = d + 1
                if nd < g.get((nr, nc), float("inf")):
                    g[(nr, nc)] = nd
                    heapq.heappush(pq, (nd + h((nr, nc)), nd, (nr, nc)))
    return -1
```

| Heuristic property | Consequence |
|---|---|
| **admissible**: never overestimates | the returned path is optimal |
| **consistent**: h(u) ≤ w(u,v) + h(v) | each vertex is expanded at most once (like Dijkstra) |
| h = 0 | A* becomes Dijkstra |
| overestimating (weighted A*, ε > 1) | faster, but suboptimal by at most a factor of ε |

Grid heuristics: Manhattan for 4-connected moves, octile distance for 8-connected moves with √2 diagonals, Euclidean for any-angle motion. This is what ROS navigation's global planners do on costmaps.

## 5. Bellman–Ford: negative weights and cycle detection

Relax **every** edge V − 1 times. A shortest simple path has at most V − 1 edges. If a V-th round still improves something, there's a negative cycle reachable from the source:

```python
def bellman_ford(n, edges, src):
    INF = float("inf")
    dist = [INF] * n
    dist[src] = 0
    for _ in range(n - 1):
        changed = False
        for u, v, w in edges:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                changed = True
        if not changed:
            break                             # early exit: already converged
    for u, v, w in edges:
        if dist[u] != INF and dist[u] + w < dist[v]:
            return None                       # negative cycle
    return dist
```

**Arbitrage**: with exchange rates r, use weights `-log(r)`. A cycle with a product of rates > 1 becomes a negative cycle.

**At most k edges** ("cheapest flight with ≤ k stops"): run k + 1 rounds, and relax from a **copy** of the previous round's distances so that one round can't chain several edges.

## 6. Floyd–Warshall: all pairs

```python
def floyd_warshall(n, edges):
    INF = float("inf")
    d = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    for u, v, w in edges:
        d[u][v] = min(d[u][v], w)
    for k in range(n):                        # k must be the OUTER loop
        dk = d[k]
        for i in range(n):
            dik = d[i][k]
            if dik == INF:
                continue
            di = d[i]
            for j in range(n):
                if dik + dk[j] < di[j]:
                    di[j] = dik + dk[j]
    return d                                  # d[i][i] < 0 means i is on a negative cycle
```

It's a DP: after iteration k, `d[i][j]` is the shortest path using only intermediate vertices from {0..k}. It's O(V³), which suits V up to a few hundred in Python. It also gives transitive closure (reachability), and minimax paths with `max` in place of `+`.

## 7. Variations worth knowing

- **Multiple sources**: push all of them at distance 0.
- **Shortest path in a state space**: the vertex is (position, extra state), e.g. fuel left, keys held, or heading.
- **K shortest paths**: allow each vertex to be popped k times (Eppstein's or Yen's algorithm for simple paths).
- **Bidirectional Dijkstra/BFS**: search from both ends and meet in the middle, roughly halving the explored radius.
- **Minimax / widest path** (maximise the bottleneck capacity): Dijkstra with `min`/`max` in place of `+`, or a maximum spanning tree.

## 8. Exam-ready answers

> [!EXAM]
> **Dijkstra's algorithm.** Dijkstra's algorithm computes single-source shortest paths in a graph with non-negative edge weights. It maintains tentative distances and a priority queue of vertices keyed by distance; it repeatedly extracts the vertex with the smallest tentative distance, which is then final, and relaxes its outgoing edges. With a binary heap, it runs in O((V + E) log V). Correctness relies on non-negative weights: when a vertex is extracted, no unexplored path can be shorter. For negative weights, Bellman–Ford relaxes all edges V − 1 times in O(VE) and detects negative cycles; A* adds an admissible heuristic to focus the search towards a goal while preserving optimality.

## 9. Cheat sheet

| Need | Code idea |
|---|---|
| Dijkstra in Python | heap of (dist, node), skip stale entries |
| path reconstruction | a parent dict, walk back from the target |
| single goal on a grid | A* with Manhattan/octile h |
| negative edges | Bellman–Ford (V−1 rounds + one check) |
| ≤ k edges | k+1 Bellman–Ford rounds on copies |
| all pairs, V ≤ 400 | Floyd–Warshall (k outermost) |
| DAG | topological order relaxation |

> [!INTERVIEW]
> **"Why can't Dijkstra handle negative edges, even without negative cycles?"** Because it finalises a vertex when it's popped. A later path through a negative edge could still make that vertex cheaper, but it's never revisited. Small counterexample: s→a (2), s→b (3), b→a (−2). Dijkstra finalises a at 2, while the true cost is 1. Use Bellman–Ford, or Johnson's algorithm (reweighting) for all pairs.
