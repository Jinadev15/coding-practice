---
id: cpp-cyc-first-cycle-edge
title: The First Edge That Closes a Cycle
difficulty: Easy
order: 1
tags: cycle detection, undirected graph, union-find, DSU
time_limit: 2
---
## Statement
Edges of an undirected graph on vertices `0 … n−1` arrive one at a time. Return the (0-based) index of the **first** edge whose endpoints are **already connected** by earlier edges, that is, the first edge that closes a cycle. A self-loop closes a cycle immediately, and so does a repeat of an earlier edge. Return `-1` if the edges form a forest.

```cpp
int first_cycle_edge(int n, const std::vector<std::pair<int,int>>& edges);
```

Re-running a BFS after every edge costs O(m·(n+m)). A **disjoint-set union** (union-find) answers "are `u` and `v` already in the same component?" in nearly O(1): keep a parent pointer per vertex, find the root of each endpoint, and merge the two trees when the roots differ. If the roots are equal, the edge closes a cycle.

**Input:** cases until the end of input: `n m`, then `m` lines `u v` (1 ≤ n ≤ 2·10⁵, 0 ≤ m ≤ 4·10⁵).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

int first_cycle_edge(int n, const vector<pair<int,int>>& edges) {
    return -1;                         // TODO
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
        cout << first_cycle_edge(n, e) << '\n';
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
3
=== sample
3 2
0 1
1 2
---
-1
=== hidden
1 1
0 0
---
0
=== hidden
2 2
0 1
1 0
---
1
=== hidden
5 0
---
-1
=== hidden
6 5
0 1
2 3
4 5
1 2
3 0
---
4
=== hidden
7 9
0 5
4 5
0 5
3 3
3 1
1 1
2 6
4 0
5 5
7 0
7 6
1 3
4 1
0 6
0 1
3 6
2 4
3 0
---
2
-1
4
-1
=== hidden
4 0
5 2
2 1
0 1
1 3
0 0
0 0
0 0
7 3
4 2
4 6
2 1
---
-1
-1
0
-1
=== hidden
1 3
0 0
0 0
0 0
4 3
1 3
0 3
2 0
6 9
5 1
2 5
1 3
3 3
1 0
0 1
4 0
5 2
2 1
5 2
3 0
4 1
---
0
-1
3
-1
=== hidden
@gen 2175942596 big
=== hidden
@gen 2175942597 big
=== hidden
@gen 2175942598 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(4 if not big else 1):
    if not big:
        n = r.randint(1, 8); m = r.randint(0, 9)
        print(n, m)
        for _ in range(m): print(r.randrange(n), r.randrange(n))
    else:
        n = 200000
        # a long random spanning tree first (no cycle), then one cycle-closing edge near the end
        perm = list(range(n)); r.shuffle(perm)
        es = [(perm[i], perm[r.randrange(i)]) for i in range(1, n)]
        r.shuffle(es)
        if r.random() < 0.7: es.append((r.randrange(n), r.randrange(n)))
        print(n, len(es))
        for u, v in es: print(u, v)
```

## Hints
- An edge closes a cycle exactly when its endpoints were already connected before it arrived.
- Maintain components with union-find: `find` gives a component's representative, `unite` merges two components.
- Use union by size and path compression (or halving) so long chains don't make `find` slow.

## Solution
**Cycle ⇔ endpoints already connected.** Adding edge `u–v` to a forest creates a cycle exactly when `u` and `v` are already in the same tree: the new edge plus the existing tree path between them form the cycle. Otherwise it joins two trees into one and the result is still a forest.

**Union-find.** Each component is a rooted tree of parent pointers; `find(x)` follows pointers to the root, which names the component. Two vertices are connected iff their roots are equal. `union` points one root at the other.

- **Union by size** attaches the smaller tree under the larger, so depths stay O(log n).
- **Path halving** (`parent[x] = parent[parent[x]]` while walking) flattens the trees further. Together they make each operation O(α(n)), effectively constant.
- `find` is a loop, not recursion, so no stack depth issues.

A self-loop has `find(u) == find(u)`, and a repeated edge finds its endpoints already merged by the first copy, so both are detected without special cases.

Complexity: O(n + m·α(n)).

```cpp
#include <bits/stdc++.h>
using namespace std;

int first_cycle_edge(int n, const vector<pair<int,int>>& edges) {
    vector<int> parent(n), sz(n, 1);
    iota(parent.begin(), parent.end(), 0);
    auto find = [&](int x) {
        while (parent[x] != x) {
            parent[x] = parent[parent[x]];      // path halving keeps the trees shallow
            x = parent[x];
        }
        return x;
    };
    for (int i = 0; i < (int)edges.size(); ++i) {
        int a = find(edges[i].first), b = find(edges[i].second);
        if (a == b) return i;                   // already connected: this edge closes a cycle
        if (sz[a] < sz[b]) swap(a, b);          // union by size: hang the smaller tree
        parent[b] = a; sz[a] += sz[b];
    }
    return -1;
}
```
