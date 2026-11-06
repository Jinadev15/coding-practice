---
id: cpp-topo-lex-smallest
title: Lexicographically Smallest Topological Order
difficulty: Medium
order: 3
tags: topological sort, Kahn's algorithm, priority queue, min-heap, tie-breaking
time_limit: 2
---
## Statement
Return the **lexicographically smallest** topological order of a directed graph (edge `u v`: `u` before `v`), or an empty vector if the graph has a cycle.

```cpp
std::vector<int> smallest_order(int n, const std::vector<std::pair<int,int>>& edges);
```

Kahn's algorithm leaves a choice open: *which* available vertex to output next. A FIFO queue outputs them in discovery order, which is valid but not smallest. To make the first position as small as possible, output the **smallest available** vertex; then the second position, and so on. Keep the available vertices in a **min-heap**.

**Input:** cases until the end of input: `n m`, then `m` edges `u v` (1 ≤ n ≤ 2·10⁵, 0 ≤ m ≤ 4·10⁵).

**Output (printed by the driver):** `cycle`, or the order (a checksum when n > 30).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> smallest_order(int n, const vector<pair<int,int>>& edges) {
    // Kahn with a FIFO queue: a valid order, but not always the smallest one
    vector<vector<int>> adj(n); vector<int> indeg(n, 0);
    for (auto [u, v] : edges) { adj[u].push_back(v); ++indeg[v]; }
    vector<int> q; for (int i = 0; i < n; ++i) if (!indeg[i]) q.push_back(i);
    for (size_t h = 0; h < q.size(); ++h) for (int v : adj[q[h]]) if (--indeg[v] == 0) q.push_back(v);
    if ((int)q.size() < n) return {};
    return q;
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
        vector<int> o = smallest_order(n, e);
        if (o.empty()) { cout << "cycle\n"; continue; }
        unsigned long long h = 0;
        for (int x : o) h = h * 1000003 + (unsigned)x;
        if (n <= 30) { for (size_t i = 0; i < o.size(); ++i) cout << (i ? " " : "") << o[i]; cout << '\n'; }
        else cout << o.size() << " checksum " << h << '\n';
    }
}
```

## Tests
=== sample
4 2
0 3
1 2
---
0 1 2 3
=== sample
5 3
3 1
4 1
1 0
---
2 3 4 1 0
=== sample
3 3
0 1
1 2
2 0
---
cycle
=== hidden
1 0
---
0
=== hidden
3 1
2 0
---
1 2 0
=== hidden
6 5
5 4
4 0
1 3
3 2
5 1
---
5 1 3 2 4 0
=== hidden
4 2
3 0
3 0
---
1 2 3 0
=== hidden
6 1
4 0
6 3
4 1
3 0
1 5
1 0
5 2
4 2
3 0
1 0
7 7
2 2
3 5
1 3
0 4
2 3
6 2
4 4
---
1 2 3 4 0 5
2 3 0 4 1 5
0
1 3 0 4 2
0
cycle
=== hidden
3 6
1 2
0 2
1 2
2 1
0 0
1 1
3 5
2 1
1 1
1 2
2 0
0 1
1 0
2 1
1 0
1 0
5 2
1 4
1 4
---
cycle
cycle
0
1 0
0
0 1 2 3 4
=== hidden
8 1
2 6
5 0
6 0
1 0
4 1
0 0
5 3
1 4
2 0
2 4
---
0 1 2 3 4 5 6 7
0 1 2 3 4
0 1 2 3 4 5
0
cycle
1 2 0 3 4
=== hidden
@gen 1209038493 big
=== hidden
@gen 1209038494 big
=== hidden
@gen 1209038495 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 1):
    if not big:
        n = r.randint(1, 8); m = r.randint(0, 9)
        perm = list(range(n)); r.shuffle(perm)
        dag = r.random() < 0.8
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
        es = [(perm[a], perm[b]) for a, b in (sorted((r.randrange(n), r.randrange(n))) for _ in range(400000)) if a < b]
        print(n, len(es))
        for u, v in es: print(u, v)
```

## Hints
- Kahn's algorithm lets you choose any vertex with in-degree 0 next.
- To make the order lexicographically smallest, always output the smallest available vertex.
- Keep the available vertices in a `priority_queue<int, vector<int>, greater<int>>`.

## Solution
**Greedy on the first position.** Any topological order must start with a vertex of in-degree 0. To minimise the first element, pick the smallest such vertex. After removing it, the rest of the order is a topological order of the remaining graph, and the same argument applies to the second position, and so on. Lexicographic order is decided position by position, so this greedy choice is optimal.

**Why FIFO is wrong.** With edges `0 → 3` and `1 → 2`, the available set starts as `{0, 1}`. A FIFO queue pops `0`, which frees `3` and appends it, then pops `1`, which frees `2` and appends it *behind* `3`. It outputs `0 1 3 2`. The heap compares everything available and outputs `0 1 2 3`.

**Cost.** Each vertex is pushed and popped once: O(n log n) for the heap plus O(m) for the edges.

**Careful:** "lexicographically smallest order" is *not* the same as "put vertex 0 as early as possible, then 1, …". That second problem needs a different trick (see the hard problem in this topic).

Complexity: O(n log n + m).

```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> smallest_order(int n, const vector<pair<int,int>>& edges) {
    vector<vector<int>> adj(n);
    vector<int> indeg(n, 0);
    for (auto [u, v] : edges) { adj[u].push_back(v); ++indeg[v]; }
    priority_queue<int, vector<int>, greater<int>> pq;     // min-heap of available vertices
    for (int i = 0; i < n; ++i) if (indeg[i] == 0) pq.push(i);
    vector<int> order;
    order.reserve(n);
    while (!pq.empty()) {
        int u = pq.top(); pq.pop();                          // smallest available goes next
        order.push_back(u);
        for (int v : adj[u]) if (--indeg[v] == 0) pq.push(v);
    }
    if ((int)order.size() < n) return {};                    // some vertices never freed: cycle
    return order;
}
```
