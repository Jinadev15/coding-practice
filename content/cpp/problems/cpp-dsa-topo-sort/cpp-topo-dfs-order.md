---
id: cpp-topo-dfs-order
title: Course Schedule II: Produce a Valid Order (DFS Finish Order)
difficulty: Medium
order: 2
tags: topological sort, DFS, finish order, iterative DFS
time_limit: 2
---
## Statement
Same courses and prerequisites as before (`u v`: `u` before `v`). Return **any** order in which all `n` courses can be taken, or an empty vector if no such order exists.

```cpp
std::vector<int> course_order(int n, const std::vector<std::pair<int,int>>& pre);
```

Solve it the **DFS way** this time (Kahn's algorithm also works, but you've seen it): in a DFS, a vertex **finishes** only after everything reachable from it has finished. So if you list vertices by **decreasing finish time** (reverse post-order), every edge `u → v` goes from left to right. A grey-vertex hit during the same DFS means a cycle. The graph can be a chain of 2·10⁵ courses, so use an iterative DFS.

**Input:** cases until the end of input: `n m`, then `m` pairs `u v` (1 ≤ n ≤ 2·10⁵, 0 ≤ m ≤ 4·10⁵).

**Output (printed by the driver):** `impossible`, `valid order`, or what's wrong with the returned order.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> course_order(int n, const vector<pair<int,int>>& pre) {
    vector<int> o(n);
    iota(o.begin(), o.end(), 0);       // TODO: ignores the prerequisites
    return o;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n, m;
    while (cin >> n >> m) {
        vector<pair<int,int>> p(m);
        for (auto& [u, v] : p) cin >> u >> v;
        vector<int> indeg(n, 0); vector<vector<int>> adj(n);
        for (auto [u, v] : p) { adj[u].push_back(v); ++indeg[v]; }
        vector<int> q; for (int i = 0; i < n; ++i) if (!indeg[i]) q.push_back(i);
        for (size_t h = 0; h < q.size(); ++h) for (int v : adj[q[h]]) if (--indeg[v] == 0) q.push_back(v);
        bool dag = (int)q.size() == n;
        vector<int> o = course_order(n, p);
        if (o.empty()) { cout << (dag ? "missed a valid order" : "impossible") << '\n'; continue; }
        if (!dag) { cout << "returned an order for a cyclic graph\n"; continue; }
        string err;
        vector<int> pos(n, -1);
        if ((int)o.size() != n) err = "wrong length";
        for (int i = 0; i < (int)o.size() && err.empty(); ++i) { if (o[i] < 0 || o[i] >= n || pos[o[i]] != -1) err = "not a permutation"; else pos[o[i]] = i; }
        if (err.empty()) for (auto [u, v] : p) if (pos[u] >= pos[v]) { err = "prerequisite violated"; break; }
        cout << (err.empty() ? "valid order" : "invalid: " + err) << '\n';
    }
}
```

## Tests
=== sample
4 4
1 0
2 0
3 1
3 2
---
valid order
=== sample
2 2
0 1
1 0
---
impossible
=== hidden
1 0
---
valid order
=== hidden
1 1
0 0
---
impossible
=== hidden
5 4
4 3
3 2
2 1
1 0
---
valid order
=== hidden
4 3
0 1
0 1
2 3
---
valid order
=== hidden
6 1
4 2
1 7
0 0
0 0
0 0
0 0
0 0
0 0
0 0
6 2
2 3
0 5
4 3
2 3
1 2
0 1
5 0
7 0
---
valid order
impossible
valid order
valid order
valid order
valid order
=== hidden
5 3
1 4
1 0
3 2
6 8
0 3
4 4
2 5
2 4
4 5
1 5
5 5
1 5
5 4
0 1
2 3
0 2
4 1
4 1
3 0
5 9
4 1
1 3
4 0
3 4
3 2
4 4
1 0
3 2
4 4
8 0
---
valid order
impossible
valid order
valid order
impossible
valid order
=== hidden
4 0
1 0
7 1
2 6
7 5
2 5
1 3
6 1
2 5
2 0
3 2
2 0
2 1
7 2
5 1
6 2
---
valid order
valid order
valid order
valid order
valid order
valid order
=== hidden
@gen 680715570 big
=== hidden
@gen 680715571 big
=== hidden
@gen 680715572 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 1):
    if not big:
        n = r.randint(1, 8); m = r.randint(0, 10)
        perm = list(range(n)); r.shuffle(perm)
        dag = r.random() < 0.6
        es = []
        for _ in range(m):
            a, b = r.randrange(n), r.randrange(n)
            if dag and a >= b: continue
            es.append((perm[a], perm[b]))
        print(n, len(es))
        for u, v in es: print(u, v)
    else:
        n = 200000
        perm = list(range(n)); r.shuffle(perm)
        es = [(perm[i], perm[i + 1]) for i in range(n - 1)]
        es += [(perm[a], perm[b]) for a, b in (sorted((r.randrange(n), r.randrange(n))) for _ in range(150000)) if a < b]
        if r.random() < 0.4: es.append((perm[n - 1], perm[0]))
        r.shuffle(es)
        print(n, len(es))
        for u, v in es: print(u, v)
```

## Hints
- In a DAG, for every edge `u → v`, `v` finishes its DFS before `u` does.
- Record vertices as they finish; the reverse of that list is a valid order.
- Meeting a grey vertex (on the current path) means a cycle, so no order exists. Use an explicit stack with a per-vertex neighbour index.

## Solution
**Finish order is a topological order, reversed.** Take any edge `u → v` in a DAG. When the DFS examines it, `v` is either white (then `v` is explored and finishes before `u` does), or black (it already finished). It can't be grey, since that would be a cycle. Either way `v` finishes before `u`. So sorting by decreasing finish time puts every `u` before its `v`.

**Cycle detection for free.** Meeting a grey vertex means a back edge, and a DAG has none, so return empty.

**Iterative, because chains are deep.** A course chain of 2·10⁵ would nest that many recursive calls. The explicit stack with a per-vertex edge index `it[u]` performs exactly the recursive DFS, including the moment each vertex finishes (when its edges run out).

**Kahn vs DFS.** Both are O(n + m). Kahn's in-degree queue is easy to adapt to "smallest label first" (use a heap) or to levels (semesters). The DFS version is what you reach for when you already need a DFS (for example to also compute reachability or strongly connected components).

Complexity: O(n + m).

```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> course_order(int n, const vector<pair<int,int>>& pre) {
    vector<vector<int>> adj(n);
    for (auto [u, v] : pre) adj[u].push_back(v);
    vector<char> color(n, 0);                  // 0 white, 1 grey, 2 black
    vector<int> it(n, 0), stk, post;           // post = vertices in finishing order
    post.reserve(n);
    for (int r = 0; r < n; ++r) {
        if (color[r]) continue;
        color[r] = 1; stk.push_back(r);
        while (!stk.empty()) {
            int u = stk.back();
            if (it[u] == (int)adj[u].size()) { color[u] = 2; post.push_back(u); stk.pop_back(); continue; }
            int v = adj[u][it[u]++];
            if (color[v] == 0) { color[v] = 1; stk.push_back(v); }
            else if (color[v] == 1) return {};   // back edge: cycle, no order exists
        }
    }
    reverse(post.begin(), post.end());          // decreasing finish time
    return post;
}
```
