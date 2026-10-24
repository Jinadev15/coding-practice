# Graphs: Representation and BFS/DFS

A **graph** G = (V, E) is a set of vertices joined by edges. Graphs model road networks and robot roadmaps, task dependencies, social networks, the web, state spaces of puzzles and planners, circuits and molecules. Two traversals, **breadth-first** and **depth-first search**, are the foundation of almost every graph algorithm: connectivity, components, cycle detection, bipartiteness, topological order, and shortest paths in unweighted graphs.

## 1. Kinds of graphs

| Property | Options |
|---|---|
| direction | undirected (`u — v`) / directed (`u → v`) |
| weights | unweighted / weighted (costs, distances, capacities) |
| cycles | cyclic / acyclic (a **DAG** if directed and acyclic) |
| density | sparse (E ≈ V) / dense (E ≈ V²) |
| implicit | neighbours generated on the fly (grids, puzzle states) |

## 2. Representations

```python
from collections import defaultdict

edges = [(0, 1), (0, 2), (1, 2), (2, 3)]

# adjacency list: the default for sparse graphs. O(V + E) memory
adj = defaultdict(list)
for u, v in edges:
    adj[u].append(v)
    adj[v].append(u)          # omit for directed graphs

# adjacency matrix: O(V²) memory, O(1) edge test, good for dense graphs and Floyd–Warshall
n = 4
mat = [[0] * n for _ in range(n)]
for u, v in edges:
    mat[u][v] = mat[v][u] = 1

# weighted adjacency list
wadj = defaultdict(list)
for u, v, w in [(0, 1, 4.0), (1, 2, 1.5)]:
    wadj[u].append((v, w))
```

| Operation | List | Matrix |
|---|---|---|
| memory | O(V + E) | O(V²) |
| is there an edge u–v? | O(deg u) (O(1) with sets) | O(1) |
| iterate over neighbours | O(deg u) | O(V) |
| BFS/DFS | O(V + E) | O(V²) |

**Grids** are implicit graphs: cell (r, c) has neighbours `(r±1, c)` and `(r, c±1)` (4-connected) or 8 with diagonals. Never build an adjacency list for a grid. Generate the neighbours instead.

## 3. BFS (recap)

BFS uses a queue and visits vertices in order of distance, so it computes **shortest paths in unweighted graphs**. Mark vertices on enqueue. It's O(V + E). (Full treatment in the Queues lesson.)

## 4. DFS

DFS goes as deep as possible before backtracking:

```python
def dfs(adj, start):
    seen, order = set(), []
    def go(u):
        seen.add(u)
        order.append(u)                 # "preorder" visit
        for v in adj[u]:
            if v not in seen:
                go(v)
    go(start)
    return order
```

For big graphs, use the iterative version with an explicit stack (the Stacks lesson) or raise the recursion limit carefully.

### Connected components (undirected)

```python
def components(n, adj):
    comp = [-1] * n
    c = 0
    for s in range(n):
        if comp[s] == -1:
            stack = [s]
            comp[s] = c
            while stack:
                u = stack.pop()
                for v in adj[u]:
                    if comp[v] == -1:
                        comp[v] = c
                        stack.append(v)
            c += 1
    return c, comp
```

The same "flood fill" counts islands in a grid, finds connected free regions in an occupancy map, and labels blobs in a binary image.

### Cycle detection

- **Undirected**: during DFS, finding an already-visited neighbour that isn't your parent means a cycle. (Union-find also works.)
- **Directed**: use three colours. WHITE (unvisited), GRAY (on the current recursion stack), BLACK (finished). An edge to a **GRAY** vertex is a back edge, so there's a cycle.

```python
def has_cycle_directed(n, adj):
    WHITE, GRAY, BLACK = 0, 1, 2
    color = [WHITE] * n
    def visit(u):
        color[u] = GRAY
        for v in adj[u]:
            if color[v] == GRAY:
                return True                   # back edge
            if color[v] == WHITE and visit(v):
                return True
        color[u] = BLACK
        return False
    return any(color[u] == WHITE and visit(u) for u in range(n))
```

### Bipartite check (2-colouring)

A graph is bipartite iff it has no odd cycle. BFS/DFS assigns alternating colours, and an edge between same-coloured vertices means it isn't bipartite. Applications include scheduling with conflicts, matching robots to tasks, and the "possible bipartition" problem.

## 5. DFS edge classification and timestamps

Recording `tin[u]` (discovery) and `tout[u]` (finish) during DFS:
- **Ancestor test**: u is an ancestor of v iff `tin[u] < tin[v]` and `tout[v] < tout[u]`.
- **Topological order** = vertices sorted by decreasing finish time (next lesson).
- Low-link values (`low[u]`) find **bridges** and **articulation points** (single points of failure in a network) and **strongly connected components** (Tarjan's algorithm) in O(V + E).

## 6. Choosing BFS or DFS

| Need | Use |
|---|---|
| shortest path (unweighted) | BFS |
| any path / reachability | either (DFS is simpler) |
| components, flood fill | either |
| cycle detection (directed) | DFS with colours |
| topological sort | DFS finish order, or Kahn's BFS |
| bridges, SCCs | DFS with low-links |
| shortest path (weighted) | Dijkstra / Bellman–Ford (Shortest Paths lesson) |
| huge or infinite state space with a goal | BFS (or iterative deepening DFS for memory) |

## 7. Exam-ready answers

> [!EXAM]
> **Graph representations and traversal.** A graph may be stored as an adjacency matrix, using O(V²) space with O(1) edge queries, suited to dense graphs, or as adjacency lists, using O(V + E) space with efficient neighbour iteration, suited to sparse graphs. Breadth-first search explores vertices in order of distance from the source using a queue and yields shortest paths in unweighted graphs; depth-first search explores as far as possible along each branch using recursion or a stack, and its discovery and finishing times support cycle detection, topological sorting and finding strongly connected components. Both visit each vertex and edge once, in O(V + E) time with adjacency lists.

## 8. Cheat sheet

| Task | Code idea |
|---|---|
| build | `adj = defaultdict(list)` |
| grid neighbours | `for dr, dc in ((1,0),(-1,0),(0,1),(0,-1))` |
| components | flood fill from each unvisited vertex |
| directed cycle | WHITE/GRAY/BLACK DFS |
| bipartite | 2-colour BFS |
| avoid recursion limits | iterative stack |

> [!INTERVIEW]
> **"Number of islands."** Scan the grid. On each unvisited land cell, increment the count and flood-fill its island (BFS/DFS, marking visited, or sinking the cells in place if mutation is allowed). That's O(R·C) time. Mention the recursion-depth risk on big grids (prefer an explicit stack), and offer union-find as an alternative that supports islands being *added* over time ("number of islands II").
