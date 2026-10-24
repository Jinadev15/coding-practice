# Queues and Deques

A **queue** is first-in, first-out: items leave in arrival order. It models waiting lines, message buffers between a sensor thread and a controller, task schedulers, and above all **breadth-first search**, which explores a graph level by level and therefore finds shortest paths in unweighted graphs. Python's `collections.deque` gives O(1) operations at both ends, `heapq` gives priority queues, and `queue.Queue` gives thread-safe queues.

## 1. `collections.deque`

```python
from collections import deque

q = deque()
q.append("a")          # enqueue at the right
q.append("b")
q.popleft()            # "a": dequeue from the left, O(1)
q.appendleft("z")      # push at the front
q.pop()                # remove from the right
q[0], q[-1]            # peek at both ends: O(1) (indexing the middle is O(n))

recent = deque(maxlen=3)      # bounded: the oldest item drops automatically
for x in range(5):
    recent.append(x)
recent                         # deque([2, 3, 4], maxlen=3)
```

> [!WARNING]
> `list.pop(0)` is O(n) because every element shifts. A BFS written with `list.pop(0)` on a million-node graph is quadratic. Always use `deque.popleft()`.

A bounded deque is the natural **ring buffer** for "last N sensor readings", moving averages and log tails.

## 2. BFS: shortest paths in unweighted graphs

```python
from collections import deque

def bfs_dist(graph, src):
    dist = {src: 0}
    q = deque([src])
    while q:
        u = q.popleft()
        for v in graph[u]:
            if v not in dist:            # mark when ENQUEUED, not when dequeued
                dist[v] = dist[u] + 1
                q.append(v)
    return dist
```

> [!KEY]
> BFS dequeues vertices in non-decreasing distance order, so the first time a vertex is discovered, it's via a shortest path. Mark vertices as visited **when you enqueue them**. Marking on dequeue lets the same vertex enter the queue many times, which can blow up to exponential time on dense graphs.

### Grid BFS (the robotics workhorse)

```python
def shortest_path_grid(grid, start, goal):
    R, C = len(grid), len(grid[0])
    q = deque([start])
    dist = {start: 0}
    while q:
        r, c = q.popleft()
        if (r, c) == goal:
            return dist[(r, c)]
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C and grid[nr][nc] != "#" and (nr, nc) not in dist:
                dist[(nr, nc)] = dist[(r, c)] + 1
                q.append((nr, nc))
    return -1
```

To recover the path, store `parent[(nr, nc)] = (r, c)` and walk back from the goal.

### Multi-source BFS

Put **all** sources in the queue at distance 0. Then one BFS gives each cell's distance to the *nearest* source in O(R·C). Examples include "rotting oranges", "distance to the nearest charger", and distance transforms for obstacle inflation in robot costmaps.

### Level-order processing

```python
def levels(graph, src):
    out, q, seen = [], deque([src]), {src}
    while q:
        level = []
        for _ in range(len(q)):          # exactly the nodes of the current level
            u = q.popleft()
            level.append(u)
            for v in graph[u]:
                if v not in seen:
                    seen.add(v); q.append(v)
        out.append(level)
    return out
```

## 3. 0-1 BFS: a deque for 0/1 edge weights

When edges cost 0 or 1, push 0-edges to the **front** and 1-edges to the back. The deque stays sorted by distance, which gives shortest paths in O(V + E) without Dijkstra's heap:

```python
def zero_one_bfs(n, adj, src):          # adj[u] = [(v, w)] with w in {0, 1}
    INF = float("inf")
    dist = [INF] * n
    dist[src] = 0
    dq = deque([src])
    while dq:
        u = dq.popleft()
        for v, w in adj[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                (dq.appendleft if w == 0 else dq.append)(v)
    return dist
```

Use it for "minimum walls to remove", "minimum direction changes", or "minimum cost where some moves are free".

## 4. Queue implemented with two stacks

```python
class StackQueue:
    def __init__(self):
        self.inbox, self.outbox = [], []
    def push(self, x):
        self.inbox.append(x)
    def pop(self):
        if not self.outbox:
            while self.inbox:
                self.outbox.append(self.inbox.pop())   # reverse once
        return self.outbox.pop()
```

Each element is moved at most once, so it's amortised O(1). It's a classic interview question and the basis of purely functional queues.

## 5. The monotonic deque (recap)

The sliding-window maximum keeps a deque of indices with decreasing values: pop smaller values from the back, and pop expired indices from the front. It's O(n) for all windows (see the Sliding Window lesson). It also optimises some DP transitions, such as `dp[i] = max(dp[j]) + cost` over a window of j.

## 6. Other queues in Python

| Need | Tool | Notes |
|---|---|---|
| FIFO in one thread | `collections.deque` | O(1) both ends |
| priority (smallest first) | `heapq` on a list | O(log n) push/pop (Heaps lesson) |
| between threads | `queue.Queue`, `LifoQueue`, `PriorityQueue` | blocking `get`/`put`, `maxsize` gives backpressure |
| between processes | `multiprocessing.Queue` | items are pickled |
| asyncio tasks | `asyncio.Queue` | `await q.get()` |

Producer–consumer with a bounded `queue.Queue(maxsize=N)` is the standard decoupling between a fast sensor driver and a slower processing stage. The producer blocks instead of exhausting memory.

## 7. Exam-ready answers

> [!EXAM]
> **Breadth-first search.** BFS explores a graph from a source using a FIFO queue: the source is enqueued and marked, then each dequeued vertex's unmarked neighbours are marked and enqueued. Vertices are therefore processed in non-decreasing order of edge distance from the source, so BFS computes shortest path lengths in unweighted graphs, and parent pointers recorded at discovery reconstruct the paths. Each vertex and edge is processed once, giving O(V + E) time and O(V) space. Variants include multi-source BFS, which initialises the queue with several sources, and 0-1 BFS, which uses a deque to handle edge weights of 0 and 1.

## 8. Cheat sheet

| Need | Code |
|---|---|
| queue | `q = deque(); q.append(x); q.popleft()` |
| last N items | `deque(maxlen=N)` |
| shortest path, unweighted | BFS, mark on enqueue |
| distance to the nearest of many sources | multi-source BFS |
| 0/1 weights | 0-1 BFS with `appendleft` |
| level by level | `for _ in range(len(q))` |
| thread-safe | `queue.Queue(maxsize=...)` |

> [!INTERVIEW]
> **"BFS or DFS for the shortest path in a maze?"** BFS. It guarantees the first arrival at a cell is along a shortest path in an unweighted grid. DFS finds *a* path, not necessarily the shortest, and would need to explore everything to be sure. For weighted grids, use Dijkstra or A* (with an admissible heuristic like Manhattan distance). For 0/1 weights, use 0-1 BFS.
