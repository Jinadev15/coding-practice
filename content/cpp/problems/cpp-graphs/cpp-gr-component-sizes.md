---
id: cpp-gr-component-sizes
title: Connected Component Sizes
difficulty: Easy
order: 1
tags: graphs, adjacency list, BFS, connected components
time_limit: 2
---
## Statement
An undirected graph has `n` vertices numbered `0 … n−1` and `m` edges. Edges may repeat, and self-loops (`u == v`) may appear. Return the sizes of all **connected components**, sorted in **non-increasing** order.

```cpp
std::vector<int> component_sizes(int n, const std::vector<std::pair<int,int>>& edges);
```

Build an **adjacency list** first (one `vector<int>` of neighbours per vertex, with each undirected edge stored in both directions). Then scan the vertices: each vertex that has not been visited yet starts a new component, and a BFS from it visits exactly that component.

**Input:** cases until the end of input: `n m`, then `m` lines `u v` (1 ≤ n ≤ 2·10⁵, 0 ≤ m ≤ 4·10⁵).

**Output (printed by the driver):** the number of components, then the sizes (all of them if there are at most 30, otherwise the first 10 and a checksum).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> component_sizes(int n, const vector<pair<int,int>>& edges) {
    return vector<int>(n, 1);          // TODO: every vertex is treated as its own component
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
        vector<int> s = component_sizes(n, e);
        cout << s.size() << ':';
        unsigned long long h = 0;
        for (size_t i = 0; i < s.size(); ++i) { h = h * 1000003 + (unsigned)s[i]; if (s.size() <= 30 || i < 10) cout << ' ' << s[i]; }
        if (s.size() > 30) cout << " ... | " << h;
        cout << '\n';
    }
}
```

## Tests
=== sample
6 4
0 1
1 2
3 4
5 5
1 0
---
3: 3 2 1
1: 1
=== hidden
4 6
0 1
1 0
0 1
2 3
3 2
2 2
5 4
0 4
4 1
1 3
3 2
---
2: 2 2
1: 5
=== hidden
9 7
2 5
4 1
6 5
0 2
2 2
1 4
7 6
5 5
1 1
0 2
4 2
0 3
3 4
6 5
2 3
5 3
3 3
5 1
3 4
2 0
---
4: 5 2 1 1
2: 4 1
2: 5 1
2: 1 1
=== hidden
2 3
1 0
0 0
0 1
9 10
7 3
5 1
5 4
3 3
4 3
0 5
5 8
0 1
7 5
4 7
5 6
1 3
4 1
1 1
2 0
2 4
4 3
2 8
0 0
0 1
0 0
0 0
0 1
1 0
0 1
1 0
---
1: 2
3: 7 1 1
1: 5
1: 2
=== hidden
2 1
1 0
7 10
6 3
3 6
1 6
1 3
2 5
5 4
5 2
1 0
2 3
5 2
7 5
0 6
0 2
1 0
5 6
4 6
8 6
5 3
0 0
5 3
5 7
1 4
3 1
---
1: 2
1: 7
2: 6 1
4: 5 1 1 1
=== hidden
@gen 4133968764 big
=== hidden
@gen 4133968765 big
=== hidden
@gen 4133968766 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(4 if not big else 1):
    n = r.randint(1, 9) if not big else 200000
    m = r.randint(0, 10) if not big else r.choice([100000, 190000, 400000])
    print(n, m)
    for _ in range(m):
        print(r.randrange(n), r.randrange(n))
```

## Hints
- Store the graph as `vector<vector<int>> adj(n)`, adding each undirected edge in both directions.
- Loop over all vertices. Each one that isn't visited yet starts a new component; a BFS from it visits that whole component.
- Mark a vertex as visited when you push it onto the queue, so nothing is pushed twice. The number of pushes is the component's size.

## Solution
**Representation.** An adjacency list stores, for each vertex, the list of its neighbours. It uses O(n + m) memory, and iterating over the neighbours of `u` costs O(deg(u)). An undirected edge is stored twice, once in each endpoint's list. Self-loops and duplicate edges are harmless: the `seen` check skips vertices that were already reached.

**Components.** Scan the vertices in order. An unvisited vertex `s` is not connected to any earlier component, so it starts a new one. A BFS from `s` reaches exactly the vertices connected to `s`. The number of vertices pushed onto the queue is the component's size.

**Mark on push.** Setting `seen[v] = 1` when `v` is pushed (not when it's popped) guarantees that every vertex enters the queue at most once, so the queue never holds more than `n` entries and a single array of size `n` can be reused for every BFS.

Complexity: O(n + m) for the traversals plus O(c log c) to sort the `c` sizes.

```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> component_sizes(int n, const vector<pair<int,int>>& edges) {
    vector<vector<int>> adj(n);
    for (auto [u, v] : edges) {            // undirected: store both directions
        adj[u].push_back(v);
        adj[v].push_back(u);
    }
    vector<char> seen(n, 0);
    vector<int> sizes, q(n);               // q is a reusable array-backed queue
    for (int s = 0; s < n; ++s) {
        if (seen[s]) continue;             // already inside an earlier component
        int head = 0, tail = 0;
        q[tail++] = s; seen[s] = 1;
        while (head < tail) {
            int u = q[head++];
            for (int v : adj[u])
                if (!seen[v]) { seen[v] = 1; q[tail++] = v; }   // mark when PUSHED, not when popped
        }
        sizes.push_back(tail);             // everything pushed belongs to this component
    }
    sort(sizes.rbegin(), sizes.rend());
    return sizes;
}
```
