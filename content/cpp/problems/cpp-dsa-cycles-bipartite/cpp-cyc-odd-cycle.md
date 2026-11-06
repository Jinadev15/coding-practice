---
id: cpp-cyc-odd-cycle
title: Prove It Isn't Bipartite: Find an Odd Cycle
difficulty: Medium
order: 6
tags: bipartite graph, odd cycle, BFS tree, lowest common ancestor, certificate
time_limit: 2
---
## Statement
A graph is bipartite **if and only if** it has no cycle of odd length. When your two-colouring fails, a good program doesn't just say "no": it shows a **certificate**, an odd cycle. Return the vertices of a simple cycle with an **odd** number of edges, `v₀, …, v_{k−1}` (distinct vertices, `k` odd, edges `v_i–v_{i+1}` and `v_{k−1}–v₀` all present; a self-loop is the cycle `{u}` with `k = 1`). Return an empty vector if the graph is bipartite.

```cpp
std::vector<int> odd_cycle(int n, const std::vector<std::pair<int,int>>& edges);
```

Run BFS and colour by depth parity. A conflicting edge `u–v` joins two vertices of the same colour, and in a BFS tree adjacent vertices differ in depth by at most one, so `depth[u] == depth[v]`. Walk both up the BFS tree in lockstep until they meet at their lowest common ancestor `a`. The path `a → … → u`, the edge `u–v`, and `v → … → a` form a cycle of length `2·(depth[u] − depth[a]) + 1`, which is odd.

**Input:** cases until the end of input: `n m`, then `m` lines `u v` (1 ≤ n ≤ 2·10⁵, 0 ≤ m ≤ 4·10⁵).

**Output (printed by the driver):** `bipartite`, `odd cycle ok`, or what's wrong with the returned cycle.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> odd_cycle(int n, const vector<pair<int,int>>& edges) {
    for (auto [u, v] : edges) if (u == v) return {u};   // only finds self-loops
    return {};
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
        // ground truth via 2-colouring
        vector<vector<int>> adj(n); for (auto [u, v] : e) { adj[u].push_back(v); adj[v].push_back(u); }
        vector<int> col(n, -1); bool bip = true;
        for (int s = 0; s < n && bip; ++s) if (col[s] < 0) { col[s] = 0; vector<int> q{s};
            for (size_t h = 0; h < q.size() && bip; ++h) for (int y : adj[q[h]]) { if (col[y] < 0) { col[y] = col[q[h]] ^ 1; q.push_back(y); } else if (col[y] == col[q[h]]) { bip = false; break; } } }
        vector<int> c = odd_cycle(n, e);
        if (c.empty()) { cout << (bip ? "bipartite" : "missed an odd cycle") << '\n'; continue; }
        if (bip) { cout << "reported an odd cycle in a bipartite graph\n"; continue; }
        vector<pair<int,int>> es; for (auto [u, v] : e) { es.push_back({u, v}); es.push_back({v, u}); } sort(es.begin(), es.end());
        vector<char> used(n, 0); string err;
        if (c.size() % 2 == 0) err = "even length";
        for (int x : c) { if (!err.empty()) break; if (x < 0 || x >= n || used[x]) { err = "vertex out of range or repeated"; break; } used[x] = 1; }
        if (err.empty()) for (size_t i = 0; i < c.size(); ++i) if (!binary_search(es.begin(), es.end(), make_pair(c[i], c[(i + 1) % c.size()]))) { err = "missing edge"; break; }
        cout << (err.empty() ? "odd cycle ok" : "invalid: " + err) << '\n';
    }
}
```

## Tests
=== sample
5 5
0 1
1 2
2 3
3 4
4 0
---
odd cycle ok
=== sample
4 4
0 1
1 2
2 3
3 0
---
bipartite
=== hidden
1 1
0 0
---
odd cycle ok
=== hidden
3 3
0 1
1 2
2 0
---
odd cycle ok
=== hidden
6 7
0 1
0 2
1 3
2 4
3 5
4 5
1 2
---
odd cycle ok
=== hidden
5 6
4 1
1 2
3 2
1 4
3 3
0 1
4 3
3 0
1 1
3 2
3 0
6 4
3 2
1 2
4 1
2 0
---
odd cycle ok
odd cycle ok
bipartite
bipartite
=== hidden
7 4
3 1
5 6
5 5
4 3
6 1
5 2
3 6
1 2
0 1
1 2
1 2
1 0
1 0
5 0
---
odd cycle ok
bipartite
bipartite
bipartite
=== hidden
6 1
4 0
4 1
0 3
1 6
0 0
0 0
0 0
0 0
0 0
0 0
4 4
0 3
2 3
1 2
1 0
---
bipartite
bipartite
odd cycle ok
bipartite
=== hidden
@gen 3317294022 big
=== hidden
@gen 3317294023 big
=== hidden
@gen 3317294024 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(4 if not big else 1):
    if not big:
        n = r.randint(1, 7); m = r.randint(0, 9)
        side = [r.randint(0, 1) for _ in range(n)]
        es = []
        for _ in range(m):
            u, v = r.randrange(n), r.randrange(n)
            if side[u] == side[v] and r.random() < 0.7: continue
            es.append((u, v))
        print(n, len(es))
        for u, v in es: print(u, v)
    else:
        n = 200000
        # a long even cycle plus random bipartite chords, then one chord that creates a huge odd cycle
        es = [(i, (i + 1) % n) for i in range(n)]
        for _ in range(150000):
            a = r.randrange(n); b = (a + 2 * r.randrange(1, 1000) + 1) % n
            es.append((a, b))
        if r.random() < 0.7: es.append((0, n // 2))
        r.shuffle(es)
        print(n, len(es))
        for u, v in es: print(u, v)
```

## Hints
- Colour by BFS depth parity. A conflicting edge joins two vertices of equal depth (why?).
- From both endpoints, move up the BFS tree together until they meet.
- The two tree paths plus the conflicting edge form a cycle of length 2k + 1.

## Solution
**Why BFS depths work.** In a BFS tree every edge joins vertices whose depths differ by at most 1 (otherwise the deeper one would have been discovered earlier). If the edge `u–v` joins two vertices of the same depth parity, their depths must therefore be **equal**.

**Building the cycle.** With equal depths, step `u` and `v` up the tree one parent at a time; they meet at their lowest common ancestor `a` after the same number `k` of steps. The tree paths `a…u` and `a…v` share only `a` (they first meet there), so `a…u`, edge `u–v`, `v…a` is a **simple** cycle with `k + 1 + k = 2k + 1` edges: odd.

**The theorem behind it.** "Bipartite ⇔ no odd cycle". One direction: an odd cycle cannot alternate two colours. The other direction is exactly this algorithm: if the BFS colouring by depth parity fails, it produces an odd cycle. So the cycle is a *certificate* that the answer "not bipartite" is correct, which a checker can verify in O(k).

**Edge cases.** A self-loop is an odd cycle of length 1; parallel edges form a cycle of length 2, which is even and harmless.

Complexity: O(n + m) for the BFS plus O(k) to extract the cycle.

```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> odd_cycle(int n, const vector<pair<int,int>>& edges) {
    vector<vector<int>> adj(n);
    for (auto [u, v] : edges) {
        if (u == v) return {u};                       // a self-loop is an odd cycle of length 1
        adj[u].push_back(v); adj[v].push_back(u);
    }
    vector<int> depth(n, -1), parent(n, -1), q(n);
    for (int s = 0; s < n; ++s) {
        if (depth[s] != -1) continue;
        int head = 0, tail = 0;
        depth[s] = 0; q[tail++] = s;
        while (head < tail) {
            int u = q[head++];
            for (int v : adj[u]) {
                if (depth[v] == -1) { depth[v] = depth[u] + 1; parent[v] = u; q[tail++] = v; }
                else if ((depth[v] & 1) == (depth[u] & 1)) {   // same colour: depth[u] == depth[v]
                    vector<int> left, right;                    // climb both sides to the LCA
                    int a = u, b = v;
                    while (a != b) { left.push_back(a); right.push_back(b); a = parent[a]; b = parent[b]; }
                    vector<int> cyc{a};                         // LCA, then down to u, then v back up
                    for (int i = (int)left.size() - 1; i >= 0; --i) cyc.push_back(left[i]);
                    for (int x : right) cyc.push_back(x);
                    return cyc;
                }
            }
        }
    }
    return {};
}
```
