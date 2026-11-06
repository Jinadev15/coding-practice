---
id: cpp-cyc-first-conflict
title: Same-or-Different Constraints: the First Contradiction
difficulty: Medium
order: 4
tags: bipartite graph, union-find with parity, online, odd cycle
time_limit: 2
---
## Statement
`n` people must be split into two teams. Constraints arrive one by one: `u v 0` means *u and v are on the same team*, `u v 1` means *they are on different teams*. Return the 1-based index of the **first** constraint that cannot be satisfied together with all earlier ones, or `0` if all of them can be satisfied.

```cpp
int first_conflict(int n, const std::vector<std::array<int,3>>& cons);   // {u, v, t}
```

With only "different" constraints this is "is the graph still bipartite after each edge?", and re-running a BFS each time is too slow for 4·10⁵ constraints. Extend union-find with a **parity**: for each vertex store `p[x]` = (team of x) XOR (team of its parent). Then the parity of `x` relative to its root is the XOR along the path to the root. Two people in the same set have a **known** relation; a new constraint contradicts it iff the known parity differs from `t`.

**Input:** cases until the end of input: `n m`, then `m` lines `u v t` (1 ≤ n ≤ 2·10⁵, 1 ≤ m ≤ 4·10⁵, t ∈ {0, 1}; `u == v` is allowed).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

int first_conflict(int n, const vector<array<int,3>>& cons) {
    // only catches direct contradictions such as "u v 1" with u == v
    for (int i = 0; i < (int)cons.size(); ++i) if (cons[i][0] == cons[i][1] && cons[i][2] == 1) return i + 1;
    return 0;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n, m;
    while (cin >> n >> m) {
        vector<array<int,3>> c(m);
        for (auto& x : c) cin >> x[0] >> x[1] >> x[2];
        cout << first_conflict(n, c) << '\n';
    }
}
```

## Tests
=== sample
3 3
0 1 1
1 2 1
0 2 1
---
3
=== sample
4 4
0 1 0
2 3 1
1 2 0
0 3 1
---
0
=== hidden
1 1
0 0 1
---
1
=== hidden
2 3
0 0 0
0 1 1
1 0 1
---
0
=== hidden
5 4
0 1 1
1 2 1
2 3 1
3 0 0
---
4
=== hidden
2 5
1 1 0
1 0 1
1 0 1
0 0 1
0 1 1
5 5
4 3 1
2 1 0
4 2 0
0 0 0
3 1 1
6 5
4 2 0
2 1 1
1 4 1
5 3 1
5 1 1
3 7
2 1 0
0 0 0
0 1 1
0 1 1
2 0 1
2 0 1
0 2 1
---
4
0
0
0
=== hidden
6 9
2 5 0
3 0 0
4 3 0
2 0 0
5 5 0
5 3 0
2 2 0
5 2 1
0 5 1
3 2
2 0 0
0 2 0
5 10
1 0 1
0 0 0
2 1 1
0 1 0
0 2 0
4 1 0
4 4 0
4 0 1
4 4 0
3 3 1
7 7
4 2 1
6 3 1
4 4 0
4 4 0
1 1 0
6 0 0
4 4 0
---
8
0
4
0
=== hidden
7 9
2 0 1
1 3 0
5 3 1
4 2 1
5 2 0
3 0 0
4 0 0
1 2 1
4 0 0
4 5
2 3 0
3 3 0
1 1 1
2 0 1
2 1 0
7 6
5 2 1
1 3 0
5 5 0
2 0 1
0 3 0
6 3 1
5 1
3 1 0
---
0
3
0
0
=== hidden
@gen 1600439631 big
=== hidden
@gen 1600439632 big
=== hidden
@gen 1600439633 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(4 if not big else 1):
    if not big:
        n = r.randint(1, 7); m = r.randint(1, 10)
        team = [r.randint(0, 1) for _ in range(n)]
        print(n, m)
        for _ in range(m):
            u, v = r.randrange(n), r.randrange(n)
            t = team[u] ^ team[v]
            if r.random() < 0.15: t ^= 1
            print(u, v, t)
    else:
        n = 200000; m = 400000
        team = [r.randint(0, 1) for _ in range(n)]
        bad = r.randrange(m // 2, m) if r.random() < 0.7 else -1
        print(n, m)
        for i in range(m):
            u, v = r.randrange(n), r.randrange(n)
            print(u, v, team[u] ^ team[v] ^ (1 if i == bad else 0))
```

## Hints
- Store, for each vertex, the XOR of its team with its parent's team. A vertex's team relative to its root is the XOR along the path.
- If `u` and `v` already share a root, the constraint is consistent iff `parity(u) XOR parity(v) == t`.
- When merging roots `ru` and `rv`, set `par[rv] = parity(u) XOR parity(v) XOR t`. Update parities during path compression.

## Solution
**Relations, not colours.** We don't know anyone's absolute team, only relations between people. Inside one union-find set, every member's team is determined relative to the root: store `par[x]` = team(x) ⊕ team(parent(x)), so team(x) ⊕ team(root) is the XOR of `par` along the path. Call it `parity(x)`.

**Checking a constraint.** If `u` and `v` are in the same set, their relation is already fixed: same team iff `parity(u) ⊕ parity(v) = 0`. A contradiction is exactly `parity(u) ⊕ parity(v) ≠ t`. In graph terms, the cycle formed by the new edge and the known path has odd "difference" parity, the generalisation of an odd cycle.

**Merging.** Otherwise hang root `rv` under root `ru` and choose `par[rv]` so the new constraint holds: parity'(v) = parity(v) ⊕ par[rv], and we need parity(u) ⊕ parity'(v) = t, so `par[rv] = pu ⊕ pv ⊕ t`.

**Path compression with parity.** When a node is re-pointed straight to the root, its stored parity must become its parity relative to the root: XOR in its old parent's (already compressed) parity. Processing the path from the root side outward guarantees the parent is done first. The loop avoids recursion.

Complexity: O((n + m)·α(n)).

```cpp
#include <bits/stdc++.h>
using namespace std;

int first_conflict(int n, const vector<array<int,3>>& cons) {
    vector<int> parent(n), par(n, 0), sz(n, 1);    // par[x] = team(x) XOR team(parent[x])
    iota(parent.begin(), parent.end(), 0);
    // returns {root, parity of x relative to root}, compressing the path on the way
    auto find = [&](int x) {
        vector<int> path;
        while (parent[x] != x) { path.push_back(x); x = parent[x]; }
        int root = x;
        // process from the node nearest the root outwards so parent's parity is already final
        for (int i = (int)path.size() - 1; i >= 0; --i) {
            int y = path[i];
            if (parent[y] != root) par[y] ^= par[parent[y]];
            parent[y] = root;
        }
        return pair<int,int>{root, path.empty() ? 0 : par[path[0]]};
    };
    for (int i = 0; i < (int)cons.size(); ++i) {
        auto [u, v, t] = cons[i];
        auto [ru, pu] = find(u);
        auto [rv, pv] = find(v);
        if (ru == rv) {
            if ((pu ^ pv) != t) return i + 1;     // known relation contradicts the new one
            continue;
        }
        if (sz[ru] < sz[rv]) { swap(ru, rv); swap(pu, pv); }
        parent[rv] = ru;
        par[rv] = pu ^ pv ^ t;                    // makes parity(u) XOR parity(v) == t
        sz[ru] += sz[rv];
    }
    return 0;
}
```
