---
id: cpp-gr-bfs-path
title: Shortest Path in an Unweighted Graph (Lexicographically Smallest)
difficulty: Medium
order: 3
tags: BFS, shortest path, path reconstruction, tie-breaking
time_limit: 2
---
## Statement
An undirected, unweighted graph has `n` vertices (`0 … n−1`) and `m` edges. Find a **shortest path** from `s` to `t` (fewest edges). Several shortest paths may exist; return the **lexicographically smallest** one, as the list of vertices from `s` to `t`. Return an empty vector if `t` is unreachable. If `s == t` the answer is `{s}`.

```cpp
std::vector<int> shortest_path(int n, const std::vector<std::pair<int,int>>& edges, int s, int t);
```

Lexicographic order compares the sequences vertex by vertex: `0 2 5` < `0 3 1` because `2 < 3` at the first difference. A BFS from `s` with parent pointers gives *a* shortest path, but not necessarily the smallest one. Think about what a BFS **from `t`** tells you.

**Input:** cases until the end of input: `n m s t`, then `m` lines `u v` (1 ≤ n ≤ 2·10⁵, 0 ≤ m ≤ 4·10⁵). Duplicate edges and self-loops may appear.

**Output (printed by the driver):** `-1` if unreachable; otherwise the number of edges on the path, then the path (or a checksum if it has more than 40 vertices).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> shortest_path(int n, const vector<pair<int,int>>& edges, int s, int t) {
    if (s == t) return {s};
    return {};                         // TODO
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n, m, s, t;
    while (cin >> n >> m >> s >> t) {
        vector<pair<int,int>> e(m);
        for (auto& [u, v] : e) cin >> u >> v;
        vector<int> p = shortest_path(n, e, s, t);
        if (p.empty()) { cout << -1 << '\n'; continue; }
        cout << p.size() - 1 << ':';
        unsigned long long h = 0;
        for (int x : p) h = h * 1000003 + (unsigned)x;
        if (p.size() <= 40) for (int x : p) cout << ' ' << x;
        else cout << " checksum " << h;
        cout << '\n';
    }
}
```

## Tests
=== sample
6 7 0 5
0 3
0 2
2 4
3 4
3 1
4 5
1 5
---
3: 0 2 4 5
=== sample
4 1 0 3
0 1
---
-1
=== hidden
1 0 0 0
---
0: 0
=== hidden
5 5 4 0
4 3
4 2
3 0
2 0
1 1
---
2: 4 2 0
=== hidden
7 8 6 0
6 5
6 4
5 3
4 3
4 2
3 1
2 1
1 0
---
4: 6 4 2 1 0
=== hidden
3 0 0 2
4 4 2 1
1 1
1 0
2 2
1 3
8 6 5 3
6 1
6 0
3 7
7 7
2 4
2 0
8 8 2 1
2 3
4 5
3 2
0 1
2 2
4 6
6 6
0 7
---
-1
-1
-1
-1
=== hidden
2 5 0 0
0 0
0 0
1 1
0 0
0 0
7 2 1 2
1 6
5 3
7 3 4 3
4 2
1 1
0 2
1 4 0 0
0 0
0 0
0 0
0 0
---
0: 0
-1
-1
0: 0
=== hidden
6 4 1 0
2 2
1 0
5 4
1 2
8 4 6 0
7 4
4 1
0 5
6 3
7 12 1 3
1 4
5 0
5 0
6 4
3 5
5 2
2 2
2 4
6 0
4 5
4 0
5 4
2 2 0 1
1 0
0 1
---
1: 1 0
-1
3: 1 4 5 3
1: 0 1
=== hidden
@gen 2031606760 big
=== hidden
@gen 2031606761 big
=== hidden
@gen 2031606762 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(4 if not big else 1):
    if not big:
        n = r.randint(1, 8); m = r.randint(0, 12)
        print(n, m, r.randrange(n), r.randrange(n))
        for _ in range(m): print(r.randrange(n), r.randrange(n))
    else:
        # a long "ladder" with many equal-length alternatives, randomly relabelled
        L = 50000; n = 4 * L; perm = list(range(n)); r.shuffle(perm)
        es = []
        for i in range(L - 1):
            for a in range(4):
                for b in range(4):
                    if r.random() < 0.3 or a == b: es.append((perm[4*i+a], perm[4*(i+1)+b]))
        r.shuffle(es)
        print(n, len(es), perm[0], perm[4*(L-1)+3])
        for u, v in es: print(u, v)
```

## Hints
- BFS from `t` gives every vertex's distance to `t`.
- On a shortest path, each step moves from distance `d` to distance `d − 1`, and every such neighbour can still finish the path.
- Walk from `s`, always moving to the smallest neighbour that is one step closer to `t`.

## Solution
**BFS computes unweighted distances.** BFS visits vertices in order of their distance from the source: all vertices at distance 0, then 1, then 2, and so on. The first time a vertex is discovered, the edge used is part of a shortest path.

**Which next steps are allowed?** Run the BFS from **`t`** to get `distT[v]`, the distance from every vertex to `t`. A path `s = v₀, v₁, …, v_d = t` is shortest exactly when each step goes one layer closer: `distT[v_{i+1}] = distT[v_i] − 1`. So from the current vertex, the *candidates* for the next vertex are the neighbours one layer closer, and **any** of them still leads to `t` in the remaining number of steps.

**Greedy is correct.** Lexicographic order is decided by the first position that differs. Choosing the smallest candidate at every step can never be worse, because a candidate always completes to a full shortest path. The walk visits each vertex at most once and scans each adjacency list at most once.

**Why not parent pointers from `s`?** A BFS from `s` stores, for each vertex, whichever parent discovered it first. Following them backwards from `t` gives a valid shortest path, but the choices are made from the *end* of the path, so the earliest positions aren't minimised.

Complexity: O(n + m).

```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> shortest_path(int n, const vector<pair<int,int>>& edges, int s, int t) {
    vector<vector<int>> adj(n);
    for (auto [u, v] : edges) { adj[u].push_back(v); adj[v].push_back(u); }
    // 1) BFS from t: distT[v] = fewest edges from v to t
    vector<int> distT(n, -1), q(n);
    int head = 0, tail = 0;
    distT[t] = 0; q[tail++] = t;
    while (head < tail) {
        int u = q[head++];
        for (int v : adj[u]) if (distT[v] == -1) { distT[v] = distT[u] + 1; q[tail++] = v; }
    }
    if (distT[s] == -1) return {};
    // 2) walk from s: every step must go one layer closer to t; take the smallest such neighbour
    vector<int> path{s};
    int cur = s;
    while (cur != t) {
        int best = INT_MAX;
        for (int v : adj[cur]) if (distT[v] == distT[cur] - 1) best = min(best, v);
        path.push_back(best);
        cur = best;
    }
    return path;
}
```
