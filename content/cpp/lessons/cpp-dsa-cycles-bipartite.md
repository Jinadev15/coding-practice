# Cycles and Bipartite Graphs

Two questions come up constantly once you have a graph: **"does it contain a cycle?"** and **"can its vertices be split into two sides so that every edge crosses?"** The first decides whether a build system can order its tasks, whether a spreadsheet's formulas can be evaluated, whether a set of processes is deadlocked, and whether a set of roads forms a tree. The second decides whether people can be split into two teams without a conflict, whether a circuit board can be two-layered, whether a matching problem is a bipartite matching, and whether a scheduling problem with "these two must not overlap" constraints has a two-slot solution.

Both are answered with the BFS and DFS you already know, plus one new tool, **union-find**. The twist is that **undirected and directed graphs behave differently**, and confusing the two is the most common bug in this topic.

## 1. What counts as a cycle

```text
undirected: a cycle needs ≥ 3 distinct vertices        directed: 2 is enough, even 1
   0 ─── 1                                              0 ──→ 1        2 ⟲
   │     │        cycle 0-1-2-3-0                       ↑     │        (self-loop)
   3 ─── 2                                              └──── ┘   cycle 0→1→0
```

- In an **undirected** simple graph, walking `0 → 1 → 0` along the same edge is **not** a cycle. A cycle uses at least 3 vertices and never reuses an edge. (A multigraph with two parallel edges `0–1` *does* have a 2-cycle, and a self-loop is a 1-cycle.)
- In a **directed** graph, `0 → 1 → 0` is a cycle because the two edges are different, and `u → u` is a cycle of length 1.
- A connected undirected graph is a **tree** iff it has `n − 1` edges and no cycle. A forest with `c` components has `n − c` edges. So an undirected graph has a cycle iff `m > n − c`. That counting fact is a good sanity check, though it doesn't tell you *where* the cycle is.

## 2. Undirected cycle detection

### 2.1 DFS with a parent

Run a DFS (or BFS). Every edge you see either discovers a new vertex (a **tree edge**) or reaches an already visited vertex. In an undirected traversal, one of those already-visited neighbours is always your own parent, through the edge you just came in on. Any *other* visited neighbour means a second route between two vertices: a cycle.

```cpp
bool has_cycle_undirected(int n, const vector<pair<int,int>>& edges) {
    vector<vector<pair<int,int>>> adj(n);           // (neighbour, edge id)
    for (int i = 0; i < (int)edges.size(); ++i) {
        auto [u, v] = edges[i];
        adj[u].push_back({v, i}); adj[v].push_back({u, i});
    }
    vector<int> parentEdge(n, -2);                   // -2 = unvisited
    for (int s = 0; s < n; ++s) {
        if (parentEdge[s] != -2) continue;
        parentEdge[s] = -1;
        vector<int> st{s};
        while (!st.empty()) {
            int u = st.back(); st.pop_back();
            for (auto [v, id] : adj[u]) {
                if (id == parentEdge[u]) continue;   // the edge we arrived by
                if (parentEdge[v] != -2) return true; // seen by another route
                parentEdge[v] = id; st.push_back(v);
            }
        }
    }
    return false;
}
```

Skipping the parent **edge id**, not the parent **vertex**, makes parallel edges and self-loops work. A second copy of edge `u–v` has a different id, so it is (correctly) reported as a 2-cycle. A self-loop `u–u` is never the edge `u` arrived by, and its other end `u` is already visited, so it is reported as a 1-cycle. If the input is guaranteed simple, comparing the parent vertex is enough.

Since we mark vertices when we *push* them, a vertex discovered by two different neighbours is caught on the second discovery, which is exactly the second route.

### 2.2 Union-find (online)

When edges **arrive one at a time** ("report the first edge that closes a cycle", "Kruskal: skip edges that would close a cycle"), keep components in a **disjoint-set union**:

```cpp
struct DSU {
    vector<int> p, sz;
    explicit DSU(int n) : p(n), sz(n, 1) { iota(p.begin(), p.end(), 0); }
    int find(int x) {
        while (p[x] != x) { p[x] = p[p[x]]; x = p[x]; }   // path halving, no recursion
        return x;
    }
    bool unite(int a, int b) {                 // false if a and b were already connected
        a = find(a); b = find(b);
        if (a == b) return false;
        if (sz[a] < sz[b]) swap(a, b);         // union by size
        p[b] = a; sz[a] += sz[b];
        return true;
    }
};
```

`unite(u, v)` returning `false` means the edge `u–v` closes a cycle. With union by size and path halving, each operation costs O(α(n)), which is at most 4 for any realistic `n`. Dry run on edges `0-1, 1-2, 2-3, 3-1`:

| edge | find(u) | find(v) | action | components |
|---|---|---|---|---|
| 0-1 | 0 | 1 | unite | {0,1} {2} {3} |
| 1-2 | 0 | 2 | unite | {0,1,2} {3} |
| 2-3 | 0 | 3 | unite | {0,1,2,3} |
| 3-1 | 0 | 0 | **same root: cycle** | |

## 3. Directed cycle detection: three colours

In a directed graph, "already visited" is **not** a cycle:

```text
0 ──→ 1
 ╲    │          vertex 2 is reached twice (0→2 and 0→1→2)
  ↘   ↓          but there is no directed cycle
    2
```

What matters is whether the visited vertex is **still on the current DFS path**. Colour each vertex:

- **white**: not visited yet,
- **grey**: entered, still being explored (on the path),
- **black**: finished; everything reachable from it is explored.

An edge `u → v` with `v` **grey** is a back edge: `v` reaches `u` down the path and `u → v` closes the loop. An edge to a **black** vertex can never close a cycle; if a cycle were reachable from `v`, the DFS from `v` would already have found it.

```cpp
// returns a directed cycle (in order) or an empty vector; iterative, safe for deep graphs
vector<int> directed_cycle(const vector<vector<int>>& adj) {
    int n = adj.size();
    vector<char> color(n, 0);                  // 0 white, 1 grey, 2 black
    vector<int> parent(n, -1), it(n, 0), st;
    for (int r = 0; r < n; ++r) {
        if (color[r]) continue;
        color[r] = 1; st.push_back(r);
        while (!st.empty()) {
            int u = st.back();
            if (it[u] == (int)adj[u].size()) { color[u] = 2; st.pop_back(); continue; }
            int v = adj[u][it[u]++];
            if (color[v] == 0) { color[v] = 1; parent[v] = u; st.push_back(v); }
            else if (color[v] == 1) {          // back edge u -> v
                vector<int> cyc;
                for (int x = u; x != v; x = parent[x]) cyc.push_back(x);
                cyc.push_back(v);
                reverse(cyc.begin(), cyc.end());
                return cyc;
            }
        }
    }
    return {};
}
```

### Dry run

Edges `0→1, 1→2, 2→3, 3→1`:

| step | top `u` | edge | colour of `v` | action | stack (grey) |
|---|---|---|---|---|---|
| 1 | 0 | 0→1 | white | push 1 | 0 1 |
| 2 | 1 | 1→2 | white | push 2 | 0 1 2 |
| 3 | 2 | 2→3 | white | push 3 | 0 1 2 3 |
| 4 | 3 | 3→1 | **grey** | cycle: walk parent from 3 to 1 | |

Walking `parent` from 3: `3 → 2 → 1`, reversed `1 2 3`, and the back edge `3 → 1` closes it.

The cycle must use **iterative** DFS on large inputs: a chain of 2·10⁵ vertices would nest that many recursive calls. The `it[u]` array remembers where each vertex is in its adjacency list, exactly like a recursive frame would.

**Alternative: Kahn's algorithm.** Repeatedly remove vertices of in-degree 0. If some vertices are never removed, the graph has a cycle. This is the topological-sort topic's main tool; it tells you *whether* there is a cycle but not directly *which* one.

## 4. Eventual safety: who can reach a cycle?

A vertex is **safe** if every walk from it eventually stops at a vertex with no outgoing edges. It is unsafe iff it can reach a cycle (an infinite walk must repeat a vertex). Two equivalent algorithms:

- **Colours:** a vertex is safe iff its DFS finishes without meeting grey and all successors are safe.
- **Reverse peeling:** terminals are safe; a vertex all of whose out-edges point to safe vertices is safe. Store the reverse graph, keep `out[u]` = out-edges not yet known safe, and run a queue from the terminals. Whatever is never peeled is unsafe.

The same reasoning detects **deadlock in a wait-for graph**: with one instance per resource, process `p` waits for the process holding what `p` needs, and a process is stuck iff it can reach a cycle. With several instances per resource type, a cycle no longer guarantees deadlock, so operating systems use **graph reduction**: repeatedly let any process whose request fits in the free pool finish and release its allocation. That is peeling again, with "fits in the pool" replacing "all successors safe".

## 5. Bipartite graphs and two-colouring

```text
bipartite:                  not bipartite (triangle):
  A side   B side               0
   0 ───── 3                   ╱ ╲
   │ ╲   ╱ │                  1 ─── 2
   1 ─╳─── 4
   2 ╱
```

A graph is **bipartite** if its vertices can be coloured 0/1 so that every edge has two different colours. Inside one connected component, the colour of one vertex **forces** all others: neighbours get the opposite colour, their neighbours the same colour again, and so on. So BFS from any vertex either produces the colouring or finds a contradiction:

```cpp
// colour[v] in {0,1}, or an empty vector if the graph is not bipartite
vector<int> bipartite_colors(const vector<vector<int>>& adj) {
    int n = adj.size();
    vector<int> color(n, -1);
    for (int s = 0; s < n; ++s) {
        if (color[s] != -1) continue;
        color[s] = 0;
        vector<int> q{s};
        for (size_t h = 0; h < q.size(); ++h) {
            int u = q[h];
            for (int v : adj[u]) {
                if (color[v] == -1) { color[v] = color[u] ^ 1; q.push_back(v); }
                else if (color[v] == color[u]) return {};   // both ends same colour
            }
        }
    }
    return color;
}
```

### The key theorem

> **A graph is bipartite if and only if it contains no cycle of odd length.**

- *Odd cycle ⇒ not bipartite:* colours alternate around a cycle, so a cycle of odd length would need its last vertex to differ from the first and also equal it.
- *Not bipartite ⇒ odd cycle:* colour by BFS depth parity. In a BFS tree, an edge joins vertices whose depths differ by at most 1. A conflict edge `u–v` joins two vertices of the same parity, so `depth[u] = depth[v]`. Walk both up the tree until they meet at their lowest common ancestor `a`, after `k` steps each. The two tree paths and the edge form a simple cycle of length `2k + 1`.

```text
           a            depth d
          ╱ ╲
        ...  ...
        ╱      ╲
       u ─────── v      depth d + k   (same depth: conflict edge)
cycle: a … u, edge u–v, v … a   →  k + 1 + k = 2k + 1 edges
```

That gives an **odd cycle certificate**: instead of just answering "no", the program shows a short proof that a checker can verify in O(k).

### Two-colouring with relations: parity union-find

Sometimes constraints arrive online and some say "**same** team" while others say "**different** teams". Store, in union-find, `par[x]` = colour(x) XOR colour(parent(x)). The parity of `x` relative to its root is the XOR along the path. Then:

- `u` and `v` in the same set: their relation is fixed, `parity(u) ^ parity(v)`. A constraint `t` contradicts it iff they differ.
- Different sets: link root `rv` under `ru` with `par[rv] = parity(u) ^ parity(v) ^ t`.

Path compression must update the parities as it re-points nodes to the root. This handles "is the graph still bipartite after each new edge?" in near-constant time per edge, and it generalises to "weighted union-find" with differences instead of XOR.

## 6. Shortest cycle (girth)

Finding *a* cycle is linear; finding the **shortest** one in an undirected graph is harder. BFS from every vertex `s`; any non-tree edge `u–v` met during that BFS gives a cycle of length at most `dist[u] + dist[v] + 1`. When `s` lies on a shortest cycle, the BFS from `s` reports that cycle's length exactly, so the minimum over all `s` is the girth. Cost O(n·(n + m)). Stop each BFS once `2·dist[u] + 1` can't beat the best answer so far.

For a **directed** graph, the shortest cycle through `s` is `1 + dist(v, s)` minimised over edges `s → v`, or simply a BFS from every `s` looking for the first edge back into `s`.

## 7. Complexity summary

| task | method | time |
|---|---|---|
| undirected: any cycle | DFS with parent edge, or DSU | O(n + m) / O(m·α(n)) |
| undirected: first edge closing a cycle | DSU, online | O(m·α(n)) |
| directed: any cycle + listing it | three-colour DFS (iterative) | O(n + m) |
| directed: vertices that reach a cycle | reverse peeling (Kahn on out-degrees) | O(n + m) |
| bipartite + colouring | BFS colouring | O(n + m) |
| odd cycle certificate | BFS depths + LCA walk | O(n + m) |
| online same/different constraints | parity DSU | O(m·α(n)) |
| girth (undirected) | BFS from every vertex | O(n·(n + m)) |
| multi-instance deadlock | graph reduction with sorted pointers | O(n·k log n) |

## 8. Pattern recognition

- "Can all courses / tasks / formulas be completed?", "is there a circular dependency?": **directed cycle** (colours or Kahn).
- "Which edge is redundant?", "first connection that creates a loop", "is this graph a tree?": **undirected cycle**, usually DSU.
- "Split into two groups", "no two enemies together", "two-colour the map", "is the conflict graph two-slot schedulable?": **bipartite**.
- "Prove it's impossible": return an **odd cycle** (bipartite) or a **directed cycle** (ordering).
- "Same / different" constraints arriving over time: **parity DSU**.
- "Nodes from which you can't get stuck in a loop", "processes that will finish": **safe states / reduction**.

## 9. Common mistakes

- **Using "visited" as the cycle test in a directed graph.** It reports false cycles (two paths to the same vertex). You need grey vs black.
- **Using grey/black in an undirected graph without skipping the parent edge.** The edge back to the parent looks like a back edge and every graph with an edge looks cyclic.
- **Skipping the parent *vertex* instead of the parent *edge*** when parallel edges are allowed: two copies of `u–v` are a real 2-cycle.
- **Recursive DFS on 10⁵+ vertices**: stack overflow. Use the iterative form with a per-vertex neighbour index.
- **Forgetting disconnected parts.** Start a traversal from every unvisited vertex; a cycle or an odd cycle can hide in any component.
- **Forgetting self-loops**: a self-loop is an odd cycle, so the graph is not bipartite.
- **Parity DSU without updating parities during path compression.** The stored parity must become "relative to the new parent", i.e. to the root.

## 10. Interview questions

> [!INTERVIEW] "Detect a cycle in a directed graph. Why can't you use a simple visited array?"
> A vertex can be reached by two different paths without any cycle (a diamond). Only an edge to a vertex that is still on the current DFS path (grey) proves a cycle. Black vertices are fully explored and safe to ignore, which keeps the algorithm O(n + m).

> [!INTERVIEW] "Is this graph bipartite? What if it isn't — can you prove it?"
> BFS-colour each component; a same-colour edge means not bipartite. For a proof, climb from both endpoints of the conflicting edge to their lowest common ancestor in the BFS tree: the result is an odd cycle, which can't be two-coloured.

> [!EXAM] Why does union-find detect a cycle when `find(u) == find(v)`?
> Equal roots mean `u` and `v` are already connected by a path of earlier edges. Adding `u–v` creates a second, edge-disjoint route between them, i.e. a cycle consisting of the old path plus the new edge.

> [!EXAM] State the time complexity of computing the girth by BFS from every vertex, and say why one BFS is not enough.
> O(n·(n + m)). A BFS from one root only certifies cycles through (or near) its own tree; the shortest cycle may be far from that root, where the BFS overestimates its length. Only a BFS started on the shortest cycle is guaranteed to measure it exactly.

## Check your understanding

1. In a directed graph DFS, `u` examines `u → v` and `v` is black. Can this edge be part of a cycle?
2. An undirected graph has 10 vertices, 3 components and 8 edges. Does it have a cycle?
3. Why does a BFS conflict edge always join two vertices of exactly the same depth?
4. In parity DSU, `parity(u) = 1`, `parity(v) = 0`, same root, and the new constraint says "same team". What happens?
5. A process in a multi-instance wait-for graph lies on a cycle. Is it necessarily deadlocked?

<details><summary>Answers</summary>

1. No. A cycle through `u → v` needs a path from `v` back to `u`. While `v` was being explored, `u` was either grey (then that path would have ended in a back edge into `u` and the cycle would already have been reported) or white (then `u` would have become a descendant of `v` and finished before `v`, but `u` is still active). Both are impossible, so the edge to a black vertex can be ignored.
2. Yes. A forest with 3 components on 10 vertices has exactly 7 edges; with 8 edges at least one edge is extra, so a cycle exists.
3. BFS layers mean any edge joins depths differing by at most 1. Depths that differ by exactly 1 have different parity, so a same-parity (same-colour) edge must join equal depths.
4. Their known relation is `1 ^ 0 = 1` (different teams), but the constraint says 0 (same). It's a contradiction: the constraint is the first conflict.
5. No. With several instances, another process outside the cycle may release enough instances to satisfy one member of the cycle and break it. You need graph reduction (the detection algorithm) to decide.

</details>
