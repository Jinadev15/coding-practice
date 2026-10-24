# Union-Find (Disjoint Set Union)

**Union-Find** (Disjoint Set Union, DSU) maintains a partition of elements into disjoint sets and supports two operations: `find(x)` (which set is x in?) and `union(x, y)` (merge their sets). With two optimisations, union by size/rank and path compression, each operation takes **amortised O(α(n))** time, where α is the inverse Ackermann function, which is ≤ 4 for any n that could exist in the physical universe. It's the tool for dynamic connectivity: Kruskal's minimum spanning tree, grouping connected pixels or point-cloud clusters, detecting cycles while adding edges, merging accounts, and percolation simulations.

## 1. The structure

Each set is a tree. Every element points to a parent, and the **root** is the set's representative.

```python
class DSU:
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n
        self.sets = n

    def find(self, x):
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:          # path compression: point everything at the root
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False                       # already connected (adding this edge would form a cycle)
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra                   # union by size: the smaller tree goes under the larger
        self.size[ra] += self.size[rb]
        self.sets -= 1
        return True

    def connected(self, a, b):
        return self.find(a) == self.find(b)
```

> [!KEY]
> - **Union by size (or rank)** alone keeps trees O(log n) tall: an element's depth increases only when its tree at least doubles in size.
> - **Path compression** alone gives amortised O(log n).
> - **Both together** give amortised O(α(n)) (Tarjan, 1975), practically constant.
>
> Write `find` iteratively in Python. The recursive version hits the recursion limit on long chains before compression has a chance to flatten them.

## 2. Kruskal's minimum spanning tree

A **minimum spanning tree** (MST) connects all vertices with the minimum total edge weight. Kruskal's algorithm sorts the edges and adds each one unless it would close a cycle:

```python
def kruskal(n, edges):                    # edges: (w, u, v)
    dsu = DSU(n)
    total, used = 0, []
    for w, u, v in sorted(edges):
        if dsu.union(u, v):
            total += w
            used.append((u, v, w))
            if len(used) == n - 1:
                break
    return total if len(used) == n - 1 else None   # None: the graph is disconnected
```

It's O(E log E), dominated by the sort. Its correctness rests on the **cut property**: the lightest edge crossing any cut belongs to some MST. **Prim's** algorithm (grow from one vertex with a heap) is the alternative, better for dense graphs.

MSTs show up in network design (cheapest cabling), clustering (remove the k−1 heaviest MST edges to get k clusters: single-linkage), and approximating the travelling salesman problem (a 2-approximation for metric TSP).

## 3. Common patterns

| Problem | DSU usage |
|---|---|
| number of connected components (static or as edges arrive) | `dsu.sets` |
| redundant connection (the edge that creates a cycle) | the first edge where `union` returns False |
| accounts merge / grouping by shared attributes | union the items sharing an email/tag, map keys to ids with a dict |
| number of islands II (cells turn to land over time) | union with land neighbours, track the count |
| satisfiability of equations (`a==b`, `a!=b`) | union all `==`, then check no `!=` pair is connected |
| largest component | `max(size[find(x)])` |
| offline "are u, v connected after time t?" | sort queries and edges by time, union as you go |

### Elements that aren't 0..n−1

Use a dict-based DSU (`parent.setdefault(x, x)`) or map labels to ids first.

### Weighted (potential) DSU

Store `diff[x]` = value(x) − value(parent(x)). This answers "x / y = ?" over chains of ratio equations (the evaluate-division problem), and detects contradictions in relative constraints, e.g. relative positions of landmarks in SLAM-like consistency checks. Update the diffs along the path during compression.

## 4. What DSU can't do

- **Split** sets or delete edges. Dynamic connectivity with deletions needs offline tricks (process in reverse, rollback DSU with divide and conquer) or link-cut trees.
- **Enumerate** the members of a set efficiently, unless you keep explicit member lists and merge the smaller into the larger (O(n log n) total).
- Shortest paths: it only knows *whether* elements are connected, not *how*.

## 5. Exam-ready answers

> [!EXAM]
> **The disjoint-set (union-find) data structure.** A disjoint-set structure maintains a collection of disjoint sets, each represented by a rooted tree whose root is the set's representative. `find` follows parent pointers to the root, and `union` links the root of one tree beneath the other. Union by rank or size keeps trees shallow by attaching the smaller tree to the larger, and path compression makes every node on a find path point directly to the root. Together, they give an amortised cost of O(α(n)) per operation, where α is the extremely slowly growing inverse Ackermann function. It is used for dynamic connectivity, cycle detection while adding edges, and Kruskal's minimum spanning tree algorithm.

## 6. Cheat sheet

| Need | Code |
|---|---|
| init | `parent = list(range(n)); size = [1]*n` |
| find | iterative + path compression |
| union | by size; return False if already joined |
| components | count successful unions, `n - unions` |
| MST | sort edges + DSU (Kruskal) |
| cycle in an undirected edge list | the first failing union |

> [!INTERVIEW]
> **"Kruskal or Prim?"** Kruskal is O(E log E), simple with a DSU, natural when edges come as a list, and good for sparse graphs. Prim is O(E log V) with a binary heap, or O(V²) with an array for dense graphs (better when E ≈ V²), and it grows one tree from a start vertex. Both rely on the cut property. Ties in weights can produce different but equally minimal trees.
