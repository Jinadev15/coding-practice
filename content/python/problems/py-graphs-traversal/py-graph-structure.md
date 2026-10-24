---
id: py-graph-structure
title: "Graph Structure: Islands, Bipartiteness, Bridges"
difficulty: Hard
order: 1
tags: graphs, DFS, BFS, flood fill, bipartite, bridges, Tarjan low-link
time_limit: 3
---
## Statement
A robot fleet's communication network and warehouse map need three structural analyses. Graphs have up to 100 000 vertices, so write **iterative** traversals.

```python
def count_islands(grid):
    """grid: list of strings, '1' land and '0' water, 4-connected. Number of islands."""

def is_bipartite(n, edges):
    """Undirected graph on vertices 0..n-1 (possibly disconnected). True if 2-colourable."""

def bridges(n, edges):
    """Undirected graph without parallel edges. Return all bridges (edges whose removal disconnects
    their component), each as a tuple (min(u, v), max(u, v)), sorted. O(V + E)."""
```

Test lines are `(function_name, args)` literals or `gen NAME SEED N`.

## Starter
```python
def count_islands(grid):
    return 0

def is_bipartite(n, edges):
    return True

def bridges(n, edges):
    def connected_without(skip):
        adj = [[] for _ in range(n)]
        for i, (u, v) in enumerate(edges):
            if i != skip:
                adj[u].append(v); adj[v].append(u)
        seen, st = {edges[skip][0]}, [edges[skip][0]]
        while st:
            x = st.pop()
            for y in adj[x]:
                if y not in seen:
                    seen.add(y); st.append(y)
        return edges[skip][1] in seen
    return sorted(tuple(sorted(edges[i])) for i in range(len(edges)) if not connected_without(i))
```

## Driver
```python
import ast
import random
import sys

FUNCS = {f.__name__: f for f in (count_islands, is_bipartite, bridges)}
for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    if line.startswith("gen "):
        _, name, seed, n = line.split()
        rng = random.Random(int(seed)); n = int(n)
        if name == "count_islands":
            g = ["".join("1" if rng.random() < 0.45 else "0" for _ in range(n)) for _ in range(n)]
            g[0] = "1" * n                                 # a long snake of land
            print(name, n, count_islands(g))
        elif name == "is_bipartite":
            edges = [(i, i + 1) for i in range(n - 1)]     # a long path: bipartite
            even = edges + [(rng.randrange(0, n, 2), rng.randrange(1, n, 2)) for _ in range(n)]
            odd = even + [(0, 2)]
            print(name, n, is_bipartite(n, even), is_bipartite(n, odd))
        else:
            edges = [(i, i + 1) for i in range(n - 1)]     # path = all bridges, then add some cycles
            for _ in range(n // 10):
                a = rng.randrange(n - 5)
                edges.append((a, a + rng.randrange(2, 5)))
            edges = list({tuple(sorted(e)) for e in edges})
            b = bridges(n, edges)
            print(name, n, len(b), b[:3])
        continue
    name, args = ast.literal_eval(line)
    print(name, "->", FUNCS[name](*args))
```

## Tests
=== sample
("count_islands", (["11000", "11000", "00100", "00011"],))
("is_bipartite", (4, [(0, 1), (1, 2), (2, 3), (3, 0)]))
("is_bipartite", (3, [(0, 1), (1, 2), (2, 0)]))
("bridges", (4, [(0, 1), (1, 2), (2, 0), (1, 3)]))
---
count_islands -> 3
is_bipartite -> True
is_bipartite -> False
bridges -> [(1, 3)]
=== hidden
("count_islands", ([],))
("count_islands", (["0"],))
("count_islands", (["1"],))
("count_islands", (["101", "010", "101"],))
("count_islands", (["111", "101", "111"],))
("is_bipartite", (1, []))
("is_bipartite", (5, [(0, 1), (2, 3), (3, 4), (4, 2)]))
("is_bipartite", (6, [(0, 1), (2, 3), (4, 5)]))
("bridges", (1, []))
("bridges", (2, [(0, 1)]))
("bridges", (5, [(0, 1), (1, 2), (2, 0), (3, 4)]))
("bridges", (6, [(0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (4, 5), (5, 3)]))
---
count_islands -> 0
count_islands -> 0
count_islands -> 1
count_islands -> 5
count_islands -> 1
is_bipartite -> True
is_bipartite -> False
is_bipartite -> True
bridges -> []
bridges -> [(0, 1)]
bridges -> [(3, 4)]
bridges -> [(2, 3)]
=== hidden
gen count_islands 1 400
gen is_bipartite 2 100000
gen bridges 3 100000
---
count_islands 400 14211
is_bipartite 100000 True False
bridges 100000 74233 [(0, 1), (1, 2), (2, 3)]

## Hints
- **Islands**: scan every cell; on unvisited land, count it and flood-fill with an explicit stack, marking cells as visited.
- **Bipartite**: BFS from every uncoloured vertex, giving neighbours the opposite colour. A neighbour with the same colour means it isn't bipartite.
- **Bridges**: Tarjan low-link. `tin[u]` is the discovery time; `low[u]` is the earliest `tin` reachable from u's subtree using at most one back edge. A tree edge `(p, u)` is a bridge iff `low[u] > tin[p]`. Iteratively, push `(u, parent, neighbour_iterator)` frames and update `low[parent]` when a child's frame finishes.
- Skip the edge back to the parent by its **edge id**, not by the vertex.

## Solution
```python
from collections import deque

def count_islands(grid):
    R = len(grid)
    C = len(grid[0]) if R else 0
    seen = [[False] * C for _ in range(R)]
    count = 0
    for r in range(R):
        for c in range(C):
            if grid[r][c] == "1" and not seen[r][c]:
                count += 1
                seen[r][c] = True
                st = [(r, c)]
                while st:
                    x, y = st.pop()
                    for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                        if 0 <= nx < R and 0 <= ny < C and grid[nx][ny] == "1" and not seen[nx][ny]:
                            seen[nx][ny] = True
                            st.append((nx, ny))
    return count

def is_bipartite(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    color = [-1] * n
    for s in range(n):
        if color[s] != -1:
            continue
        color[s] = 0
        q = deque([s])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if color[v] == -1:
                    color[v] = color[u] ^ 1
                    q.append(v)
                elif color[v] == color[u]:
                    return False
    return True

def bridges(n, edges):
    adj = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        adj[u].append((v, i))
        adj[v].append((u, i))
    tin, low = [-1] * n, [0] * n
    timer, out = 0, []
    for root in range(n):
        if tin[root] != -1:
            continue
        tin[root] = low[root] = timer; timer += 1
        stack = [(root, -1, iter(adj[root]))]      # (vertex, edge id to its parent, neighbours)
        while stack:
            u, pe, it = stack[-1]
            advanced = False
            for v, eid in it:
                if eid == pe:
                    continue                        # don't reuse the tree edge to the parent
                if tin[v] == -1:
                    tin[v] = low[v] = timer; timer += 1
                    stack.append((v, eid, iter(adj[v])))
                    advanced = True
                    break
                low[u] = min(low[u], tin[v])        # back edge
            if not advanced:
                stack.pop()
                if stack:
                    p = stack[-1][0]
                    low[p] = min(low[p], low[u])
                    if low[u] > tin[p]:
                        out.append((min(p, u), max(p, u)))
    return sorted(out)
```

- **Flood fill and 2-colouring** are plain traversals, each O(V + E). Writing them with an explicit stack or queue makes them safe on 160 000-cell grids and 100 000-vertex paths.
- **Bridges** use DFS timestamps. `low[u]` records how far back up the DFS tree u's subtree can climb through back edges. If even the best climb can't reach above u (`low[u] > tin[parent]`), the tree edge to the parent is the only connection, so it's a bridge. In a robot network, bridges are the single links whose failure partitions the fleet.
- The iterative version keeps each vertex's neighbour iterator in its stack frame. That's exactly what the call stack would hold in the recursive version.
