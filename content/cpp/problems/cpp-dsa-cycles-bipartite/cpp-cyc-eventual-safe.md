---
id: cpp-cyc-eventual-safe
title: Eventually Safe States
difficulty: Medium
order: 5
tags: directed graph, cycles, reverse graph, Kahn's algorithm, out-degree peeling
time_limit: 2
---
## Statement
In a directed graph, a vertex is **terminal** if it has no outgoing edges. A vertex is **safe** if *every* walk starting from it eventually reaches a terminal vertex, in other words, no walk from it can go on forever. A walk can go on forever exactly when it can reach a cycle. Return all safe vertices in increasing order.

```cpp
std::vector<int> safe_states(int n, const std::vector<std::pair<int,int>>& edges);
```

Peel from the safe end: terminal vertices are safe. A vertex all of whose out-edges lead to safe vertices is safe too. Keep, for each vertex, the number of out-edges not yet known to lead somewhere safe; when it drops to 0 the vertex becomes safe. Driving that requires the **reverse** graph (who points at me?). It is Kahn's algorithm run backwards. Vertices never peeled are exactly those that can reach a cycle.

**Input:** cases until the end of input: `n m`, then `m` directed edges `u v` (1 ≤ n ≤ 2·10⁵, 0 ≤ m ≤ 4·10⁵; self-loops and repeated edges may appear).

**Output (printed by the driver):** the number of safe vertices, then the list (or a checksum when there are more than 30).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> safe_states(int n, const vector<pair<int,int>>& edges) {
    // wrong: only vertices that are not themselves on a self-loop and have out-degree 0
    vector<int> out(n, 0); for (auto [u, v] : edges) ++out[u];
    vector<int> r; for (int i = 0; i < n; ++i) if (!out[i]) r.push_back(i);
    return r;
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
        vector<int> s = safe_states(n, e);
        cout << s.size() << ':';
        unsigned long long h = 0;
        for (int x : s) h = h * 1000003 + (unsigned)x;
        if (s.size() <= 30) for (int x : s) cout << ' ' << x;
        else cout << " checksum " << h;
        cout << '\n';
    }
}
```

## Tests
=== sample
7 8
0 1
0 2
1 2
1 3
2 5
3 0
3 4
4 5
---
4: 2 4 5 6
=== sample
3 1
1 1
---
2: 0 2
=== hidden
1 0
---
1: 0
=== hidden
1 1
0 0
---
0:
=== hidden
4 4
0 1
1 2
2 1
0 3
---
1: 3
=== hidden
5 5
0 1
0 1
1 2
2 3
4 3
---
5: 0 1 2 3 4
=== hidden
6 8
2 5
3 5
2 3
5 1
0 2
3 4
3 5
0 1
2 5
0 0
0 1
0 1
0 1
0 1
1 3
0 0
0 0
0 0
5 0
---
6: 0 1 2 3 4 5
1: 1
0:
5: 0 1 2 3 4
=== hidden
4 5
3 1
2 3
0 1
2 1
0 3
1 3
0 0
0 0
0 0
7 1
5 6
1 0
---
4: 0 1 2 3
0:
7: 0 1 2 3 4 5 6
1: 0
=== hidden
2 6
0 1
1 1
0 1
0 0
0 0
0 1
8 0
2 7
0 1
0 0
1 1
1 1
0 1
0 1
0 1
7 7
3 1
1 1
4 5
2 6
5 3
3 6
0 3
---
0:
8: 0 1 2 3 4 5 6 7
0:
2: 2 6
=== hidden
@gen 2537217521 big
=== hidden
@gen 2537217522 big
=== hidden
@gen 2537217523 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(4 if not big else 1):
    if not big:
        n = r.randint(1, 8); m = r.randint(0, 11)
        es = []
        for _ in range(m):
            u, v = r.randrange(n), r.randrange(n)
            if r.random() < 0.7 and u >= v: u, v = v, u
            if r.random() < 0.6 and u == v: continue
            es.append((u, v))
        print(n, len(es))
        for u, v in es: print(u, v)
    else:
        n = 200000
        perm = list(range(n)); r.shuffle(perm)
        es = [(perm[i], perm[i + 1]) for i in range(n - 1)]
        es += [(perm[a], perm[b]) for a, b in (sorted((r.randrange(n), r.randrange(n))) for _ in range(190000)) if a < b]
        for _ in range(3): k = r.randrange(n // 2, n); es.append((perm[k], perm[k - r.randint(1, 50)]))   # a few short cycles deep down
        r.shuffle(es)
        print(n, len(es))
        for u, v in es: print(u, v)
```

## Hints
- A vertex is unsafe exactly when it can reach a cycle.
- Terminals are safe; a vertex whose every out-edge goes to a safe vertex is safe.
- Reverse the edges and run Kahn's algorithm on out-degrees: start from terminals, and when a vertex becomes safe decrement the counters of its predecessors.

## Solution
**Characterisation.** A vertex is unsafe iff some walk from it never ends. In a finite graph an infinite walk must repeat a vertex, so it enters a cycle. So: unsafe ⇔ can reach a cycle (including being on one, and self-loops).

**Peeling (reverse Kahn).** Safe vertices can be built up inductively: terminals are safe; if all successors of `u` are safe, `u` is safe. Keep `out[u]` = number of `u`'s out-edges whose target is not yet known safe. When `v` becomes safe, every reverse edge `v ← u` decrements `out[u]`; at zero, `u` joins the queue. Repeated edges are counted (and decremented) once per copy, so they work automatically.

**Why the rest are unsafe.** If the peeling stops with `u` unpeeled, `u` has an edge to an unpeeled vertex, which has an edge to an unpeeled vertex, and so on forever: an infinite walk. So the unpeeled vertices are exactly those that can reach a cycle.

**Alternative.** A three-colour DFS: a vertex is safe iff its DFS finishes without meeting a grey vertex and all its successors are safe. It's equivalent, but needs an iterative DFS at this size.

Complexity: O(n + m).

```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> safe_states(int n, const vector<pair<int,int>>& edges) {
    vector<vector<int>> radj(n);                  // reverse edges: v -> u for every u -> v
    vector<int> out(n, 0);                        // out-edges of u not yet known to be safe
    for (auto [u, v] : edges) { radj[v].push_back(u); ++out[u]; }
    vector<int> q;
    for (int i = 0; i < n; ++i) if (out[i] == 0) q.push_back(i);   // terminals are safe
    vector<char> safe(n, 0);
    for (size_t h = 0; h < q.size(); ++h) {
        int v = q[h]; safe[v] = 1;
        for (int u : radj[v])                     // each edge u -> v now leads somewhere safe
            if (--out[u] == 0) q.push_back(u);    // all of u's edges are safe: u is safe
    }
    vector<int> res;
    for (int i = 0; i < n; ++i) if (safe[i]) res.push_back(i);
    return res;
}
```
