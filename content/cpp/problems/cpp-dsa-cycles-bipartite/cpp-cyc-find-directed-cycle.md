---
id: cpp-cyc-find-directed-cycle
title: Find a Cycle in a Directed Graph
difficulty: Medium
order: 3
tags: directed graph, cycle detection, DFS colours, back edge, iterative DFS
time_limit: 2
---
## Statement
Given a directed graph, return **any** directed cycle as a list of distinct vertices `v₀, v₁, …, v_{k−1}` such that the edges `v₀→v₁, v₁→v₂, …, v_{k−1}→v₀` all exist (a self-loop `u→u` is the cycle `{u}`). Return an empty vector if the graph is acyclic.

```cpp
std::vector<int> find_cycle(int n, const std::vector<std::pair<int,int>>& edges);
```

Use **three colours**: white (unvisited), grey (on the current DFS path), black (finished). An edge into a **grey** vertex is a back edge and closes a cycle; walk the DFS parent pointers back from the current vertex to that grey vertex to list it. An edge into a black vertex is harmless: everything reachable from a black vertex was already explored without finding a cycle. The graph can be a 2·10⁵-vertex path, so the DFS must be iterative.

**Input:** cases until the end of input: `n m`, then `m` directed edges `u v` (1 ≤ n ≤ 2·10⁵, 0 ≤ m ≤ 4·10⁵).

**Output (printed by the driver):** `acyclic`, `cycle ok`, or a description of what is wrong with the returned cycle.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> find_cycle(int n, const vector<pair<int,int>>& edges) {
    return {};                         // TODO
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n, m;
    while (cin >> n >> m) {
        vector<pair<int,int>> e(m);
        for (auto& [u, v] : e) cin >> u >> v;
        // ground truth: does a cycle exist? (Kahn's algorithm)
        vector<int> indeg(n, 0); vector<vector<int>> adj(n);
        for (auto [u, v] : e) { adj[u].push_back(v); ++indeg[v]; }
        vector<int> q; for (int i = 0; i < n; ++i) if (!indeg[i]) q.push_back(i);
        for (size_t h = 0; h < q.size(); ++h) for (int v : adj[q[h]]) if (--indeg[v] == 0) q.push_back(v);
        bool cyclic = (int)q.size() < n;
        vector<int> c = find_cycle(n, e);
        if (c.empty()) { cout << (cyclic ? "missed a cycle" : "acyclic") << '\n'; continue; }
        if (!cyclic) { cout << "reported a cycle in an acyclic graph\n"; continue; }
        vector<pair<int,int>> es(e.begin(), e.end()); sort(es.begin(), es.end());
        vector<char> used(n, 0); string err;
        for (int x : c) { if (x < 0 || x >= n || used[x]) { err = "vertex out of range or repeated"; break; } used[x] = 1; }
        if (err.empty()) for (size_t i = 0; i < c.size(); ++i) if (!binary_search(es.begin(), es.end(), make_pair(c[i], c[(i + 1) % c.size()]))) { err = "missing edge"; break; }
        cout << (err.empty() ? "cycle ok" : "invalid: " + err) << '\n';
    }
}
```

## Tests
=== sample
4 4
0 1
1 2
2 3
3 1
---
cycle ok
=== sample
3 3
0 1
0 2
1 2
---
acyclic
=== hidden
1 1
0 0
---
cycle ok
=== hidden
2 2
0 1
1 0
---
cycle ok
=== hidden
5 4
0 1
1 2
2 3
3 4
---
acyclic
=== hidden
2 2
0 0
1 0
8 6
1 7
4 7
7 0
4 6
0 4
5 6
7 0
8 0
---
cycle ok
cycle ok
acyclic
acyclic
=== hidden
1 7
0 0
0 0
0 0
0 0
0 0
0 0
0 0
1 2
0 0
0 0
3 9
0 0
1 1
0 0
1 0
1 2
1 0
2 1
1 1
2 1
4 4
0 1
0 2
1 2
1 3
---
cycle ok
cycle ok
cycle ok
acyclic
=== hidden
4 9
0 3
1 2
0 1
2 1
3 0
3 3
0 3
2 2
3 0
7 1
3 5
5 5
1 2
2 4
0 2
1 4
0 4
6 4
0 3
1 5
3 1
2 2
---
cycle ok
acyclic
acyclic
cycle ok
=== hidden
@gen 4219878241 big
=== hidden
@gen 4219878242 big
=== hidden
@gen 4219878243 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(4 if not big else 1):
    if not big:
        n = r.randint(1, 8); m = r.randint(0, 10)
        dag = r.random() < 0.5
        es = []
        for _ in range(m):
            u, v = r.randrange(n), r.randrange(n)
            if dag and u >= v: continue
            es.append((u, v))
        print(n, len(es))
        for u, v in es: print(u, v)
    else:
        n = 200000
        perm = list(range(n)); r.shuffle(perm)
        es = [(perm[i], perm[i + 1]) for i in range(n - 1)]          # a long path in topological order
        es += [(perm[a], perm[b]) for a, b in (sorted((r.randrange(n), r.randrange(n))) for _ in range(150000)) if a < b]
        if r.random() < 0.7: es.append((perm[n - 1], perm[r.randrange(n // 2)]))   # one long back edge
        r.shuffle(es)
        print(n, len(es))
        for u, v in es: print(u, v)
```

## Hints
- Mark vertices white, grey (on the current DFS path) or black (finished).
- An edge to a grey vertex closes a cycle; an edge to a black vertex never does.
- Keep `parent[]` for tree edges; walk it back from the current vertex to the grey target to list the cycle.

## Solution
**Why grey matters.** In a directed graph, "already visited" is not enough to signal a cycle: in `0→1, 0→2, 1→2` vertex 2 is reached twice but there is no cycle. What matters is whether the visited vertex is **still on the current path**. Grey = entered but not finished = on the path. An edge `u→v` with `v` grey means `v` reaches `u` (down the path) and `u` reaches `v` (the edge): a cycle.

**Black is safe.** A black vertex was fully explored. If a cycle were reachable from it, the DFS would have found it then. So edges into black vertices can be ignored, and every vertex is processed once: O(n + m).

**Extracting the cycle.** The grey vertices form a chain of parent pointers from the root down to `u`. Following `parent` from `u` up to `v` lists the cycle backwards; reverse it. The vertices are distinct because they are distinct stack entries.

**Undirected graphs are different.** There, the edge back to the parent is not a cycle, and every non-tree edge closes one. A two-colour (visited/unvisited) DFS with a parent check, or union-find, suffices.

Complexity: O(n + m) with the iterative DFS.

```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> find_cycle(int n, const vector<pair<int,int>>& edges) {
    vector<vector<int>> adj(n);
    for (auto [u, v] : edges) adj[u].push_back(v);
    vector<char> color(n, 0);                 // 0 white, 1 grey (on the path), 2 black (done)
    vector<int> parent(n, -1), it(n, 0), stk;
    for (int root = 0; root < n; ++root) {
        if (color[root]) continue;
        color[root] = 1; stk.push_back(root);
        while (!stk.empty()) {
            int u = stk.back();
            if (it[u] == (int)adj[u].size()) { color[u] = 2; stk.pop_back(); continue; }
            int v = adj[u][it[u]++];
            if (color[v] == 0) { parent[v] = u; color[v] = 1; stk.push_back(v); }
            else if (color[v] == 1) {         // back edge u -> v: v ... u is on the stack
                vector<int> cyc;
                for (int x = u; x != v; x = parent[x]) cyc.push_back(x);
                cyc.push_back(v);
                reverse(cyc.begin(), cyc.end());   // v -> ... -> u, and u -> v closes it
                return cyc;
            }
            // color[v] == 2: fully explored, no cycle through it
        }
    }
    return {};
}
```
