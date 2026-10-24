# Topological Sort

A **topological order** of a directed graph lists its vertices so that every edge `u → v` has u before v. It exists **iff the graph is a DAG** (directed acyclic graph). Topological sorting answers "in what order can these tasks run, given their dependencies?". Build systems (`make`, Bazel), package managers, course schedules, spreadsheet recalculation, task graphs in robotics pipelines (launch order of ROS nodes), and neural-network computation graphs (forward order, then backprop in reverse) all rely on it.

## 1. Kahn's algorithm (BFS on in-degrees)

Repeatedly output a vertex with no remaining incoming edges:

```python
from collections import deque

def topo_kahn(n, edges):
    adj = [[] for _ in range(n)]
    indeg = [0] * n
    for u, v in edges:
        adj[u].append(v)
        indeg[v] += 1
    q = deque(u for u in range(n) if indeg[u] == 0)
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return order if len(order) == n else None    # None: a cycle exists
```

> [!KEY]
> If fewer than n vertices are output, the remaining ones all have in-degree ≥ 1 and lie on (or downstream of) a **cycle**. So Kahn's algorithm doubles as cycle detection. Its cost is O(V + E).

### Lexicographically smallest order

Replace the deque with a **min-heap**: `heapq` of the ready vertices. That costs O((V + E) log V). Use it when the order must be deterministic or canonical, e.g. reproducible build logs.

## 2. DFS-based topological sort

A vertex finishes (postorder) only after everything reachable from it has finished, so **reversed finish order** is a topological order:

```python
def topo_dfs(n, adj):
    WHITE, GRAY, BLACK = 0, 1, 2
    color, out = [WHITE] * n, []
    def visit(u):
        color[u] = GRAY
        for v in adj[u]:
            if color[v] == GRAY:
                raise ValueError("cycle")
            if color[v] == WHITE:
                visit(v)
        color[u] = BLACK
        out.append(u)                 # postorder
    for u in range(n):
        if color[u] == WHITE:
            visit(u)
    return out[::-1]
```

Python's standard library has one too: `graphlib.TopologicalSorter` (3.9+), which supports **parallel** scheduling with `get_ready()` and `done()`:

```python
from graphlib import TopologicalSorter

ts = TopologicalSorter({"deploy": {"test", "build"}, "test": {"build"}, "build": set()})
list(ts.static_order())          # ['build', 'test', 'deploy']
```

## 3. Applications beyond ordering

### Longest path / critical path in a DAG

Shortest and longest paths are easy in a DAG: relax edges in topological order, in O(V + E). The **critical path** of a project is the longest chain of dependent task durations, and it's the minimum possible makespan with unlimited workers:

```python
def critical_path(n, edges, dur):
    order = topo_kahn(n, edges)
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
    finish = dur[:]                       # earliest finish time of each task
    for u in order:
        for v in adj[u]:
            finish[v] = max(finish[v], finish[u] + dur[v])
    return max(finish)
```

### Counting paths, DP on DAGs

The number of paths from s to t: `ways[v] = Σ ways[u]` over edges `u → v`, in topological order. Every DP is a DAG of subproblems, and topological order is just "an order where dependencies are computed first".

### Scheduling in parallel levels

Kahn's algorithm processed **level by level** (everything currently ready forms one batch) gives the minimum number of semesters for course scheduling with unlimited parallelism, and it's how build tools run independent jobs concurrently.

### Alien dictionary

Derive letter-order edges from adjacent words in a sorted alien dictionary (the first differing letter gives `a → b`), then topologically sort. Edge cases: a word that is a proper prefix of the word *before* it (`"abc"` before `"ab"`) means the input is invalid, and so does a cycle.

## 4. Strongly connected components (going further)

In a general directed graph, cycles group vertices into **SCCs** (each vertex reaches every other within the group). Contracting each SCC to one node yields a DAG, the **condensation**, which can then be topologically sorted. Kosaraju's (two DFS passes) and Tarjan's (one pass with low-links) algorithms are O(V + E). Applications include 2-SAT, deadlock analysis, and finding the circular-import groups in a codebase.

## 5. Exam-ready answers

> [!EXAM]
> **Topological sorting.** A topological ordering of a directed graph is a linear ordering of its vertices such that for every edge (u, v), u precedes v; it exists exactly when the graph is acyclic. Kahn's algorithm repeatedly removes a vertex of in-degree zero, decrementing its successors' in-degrees; if vertices remain when no vertex of in-degree zero is left, the graph contains a cycle. Alternatively, depth-first search outputs vertices in decreasing order of finishing time. Both run in O(V + E). Topological order enables dependency scheduling and linear-time dynamic programming on DAGs, such as shortest, longest (critical) and path-counting computations.

## 6. Cheat sheet

| Need | Tool |
|---|---|
| any order + cycle check | Kahn (deque) |
| lexicographically smallest | Kahn with `heapq` |
| order via DFS | reversed postorder, GRAY = cycle |
| parallel batches | Kahn level by level / `graphlib.TopologicalSorter` |
| longest/shortest path in a DAG | relax in topological order |
| general digraph structure | SCC condensation |

> [!INTERVIEW]
> **"Course schedule: can all courses be finished?"** Model prerequisites as edges `pre → course` and run Kahn's algorithm. It's possible iff all n courses get output, i.e. there's no cycle. That's O(V + E). The follow-up "return an order" means returning Kahn's output. "Minimum semesters" means counting BFS levels. Mention the DFS three-colour alternative and its recursion-depth caveat in Python.
