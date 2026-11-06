---
id: cpp-cyc-two-coloring
title: Bipartite Check and Two-Colouring
difficulty: Easy
order: 2
tags: bipartite graph, BFS, two-colouring, graph colouring
time_limit: 2
---
## Statement
A graph is **bipartite** when its vertices can be split into two groups so that every edge joins the two groups, equivalently, when it can be coloured with colours 0 and 1 so that no edge has both ends the same colour. Return such a colouring, or an empty vector if none exists.

```cpp
std::vector<int> two_color(int n, const std::vector<std::pair<int,int>>& edges);
```

To make the answer unique, the **smallest vertex of every connected component gets colour 0**. (Within a component, fixing one vertex's colour forces all the others.) Isolated vertices therefore get 0. A self-loop makes the graph non-bipartite.

**Input:** cases until the end of input: `n m`, then `m` lines `u v` (1 ≤ n ≤ 2·10⁵, 0 ≤ m ≤ 4·10⁵).

**Output (printed by the driver):** `not bipartite`, or the number of vertices with colour 1 followed by the colouring (or a checksum when n > 30).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> two_color(int n, const vector<pair<int,int>>& edges) {
    vector<int> c(n);
    for (int i = 0; i < n; ++i) c[i] = i % 2;      // TODO: guesses a colouring
    return c;
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
        vector<int> c = two_color(n, e);
        if (c.empty()) { cout << "not bipartite\n"; continue; }
        int ones = 0; unsigned long long h = 0;
        for (int x : c) { ones += x == 1; h = h * 3 + (unsigned)x; }
        cout << ones << ':';
        if (n <= 30) for (int x : c) cout << ' ' << x;
        else cout << " checksum " << h;
        cout << '\n';
    }
}
```

## Tests
=== sample
4 4
0 1
1 2
2 3
3 0
---
2: 0 1 0 1
=== sample
3 3
0 1
1 2
2 0
---
not bipartite
=== hidden
1 0
---
0: 0
=== hidden
1 1
0 0
---
not bipartite
=== hidden
6 3
5 4
3 2
1 3
---
2: 0 0 0 1 0 1
=== hidden
5 4
4 3
3 2
2 1
1 0
---
2: 0 1 0 1 0
=== hidden
3 2
0 2
2 1
4 5
3 3
2 1
3 1
0 2
2 1
2 1
0 1
4 1
0 1
---
1: 0 0 1
not bipartite
1: 0 1
1: 0 1 0 0
=== hidden
8 5
1 4
1 4
0 3
2 1
7 4
2 4
0 1
0 1
1 0
1 1
6 4
1 0
1 0
3 4
4 5
2 3
0 1
0 0
1 0
---
3: 0 0 1 1 1 0 0 0
not bipartite
2: 0 1 0 0 1 0
not bipartite
=== hidden
8 1
2 4
2 0
2 2
0 1
0 1
4 0
---
1: 0 0 0 0 1 0 0 0
0: 0 0
1: 0 1
0: 0 0 0 0
=== hidden
@gen 2045552476 big
=== hidden
@gen 2045552477 big
=== hidden
@gen 2045552478 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(4 if not big else 1):
    if not big:
        n = r.randint(1, 9); m = r.randint(0, 9)
        side = [r.randint(0, 1) for _ in range(n)]
        es = []
        for _ in range(m):
            u, v = r.randrange(n), r.randrange(n)
            if r.random() < 0.8 and side[u] == side[v]: continue   # mostly bipartite
            es.append((u, v))
        print(n, len(es))
        for u, v in es: print(u, v)
    else:
        n = 200000
        side = [r.randint(0, 1) for _ in range(n)]
        A = [i for i in range(n) if side[i] == 0]; B = [i for i in range(n) if side[i] == 1]
        es = [(r.choice(A), r.choice(B)) for _ in range(399999)]
        if r.random() < 0.5: es.append((A[0], A[1]))        # sometimes break it with one edge
        r.shuffle(es)
        print(n, len(es))
        for u, v in es: print(u, v)
```

## Hints
- In a connected component, choosing one vertex's colour forces every other colour.
- BFS from the smallest unvisited vertex with colour 0; give each newly found neighbour the opposite colour.
- An edge between two already-coloured vertices of the same colour means the graph is not bipartite.

## Solution
**Colours are forced.** Once one vertex of a component has a colour, each neighbour must take the opposite colour, their neighbours the opposite again, and so on. So a BFS (or DFS) from the component's first vertex assigns the only possible colouring: `color[v] = color[u] ^ 1`.

**Detecting failure.** If the traversal ever sees an edge whose two ends already have the same colour, no colouring exists: the forced colours contradict each other. That happens exactly when the component contains an **odd cycle** (a closed walk with an odd number of edges cannot alternate two colours). A self-loop is an odd cycle of length 1.

**Uniqueness.** Scanning `s = 0, 1, 2, …` and starting each new component at colour 0 means the smallest vertex of each component gets 0, which is the required canonical answer.

Complexity: O(n + m).

```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> two_color(int n, const vector<pair<int,int>>& edges) {
    vector<vector<int>> adj(n);
    for (auto [u, v] : edges) { adj[u].push_back(v); adj[v].push_back(u); }
    vector<int> color(n, -1), q(n);
    for (int s = 0; s < n; ++s) {                  // s is the smallest vertex of a new component
        if (color[s] != -1) continue;
        int head = 0, tail = 0;
        color[s] = 0; q[tail++] = s;
        while (head < tail) {
            int u = q[head++];
            for (int v : adj[u]) {
                if (color[v] == -1) { color[v] = color[u] ^ 1; q[tail++] = v; }   // forced: the opposite colour
                else if (color[v] == color[u]) return {};                          // an edge inside one colour
            }
        }
    }
    return color;
}
```
