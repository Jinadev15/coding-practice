---
id: cpp-gr-dfs-timestamps
title: Iterative DFS with Timestamps and Edge Classification
difficulty: Medium
order: 8
tags: DFS, iterative DFS, discovery time, finish time, edge classification
time_limit: 2
---
## Statement
Run a depth-first search over a **directed** graph and record, for every vertex, its **discovery time** `tin[v]` and **finish time** `tout[v]`. Also classify every edge `u → v` (each edge entry once, at the moment `u` examines it):

- **tree** if it discovers `v` (v was unvisited),
- **back** if `v` is still active (discovered, not finished), including self-loops,
- **forward** if `v` is finished and `tin[u] < tin[v]`,
- **cross** if `v` is finished and `tin[v] < tin[u]`.

```cpp
struct DfsResult { std::vector<int> tin, tout; long long tree = 0, back = 0, fwd = 0, cross = 0; };
DfsResult dfs_times(int n, const std::vector<std::vector<int>>& adj);
```

The order is fixed so the answer is unique: start new trees from the smallest unvisited vertex (`0, 1, 2, …`), scan each adjacency list **in order**, and use one clock starting at 0 that ticks after every discovery and every finish (so all `2n` times are distinct, `0 … 2n−1`). This is exactly what the textbook recursive DFS produces. Your version must produce the same numbers **without recursion**, because the graph can be a path of 2·10⁵ vertices.

**Input:** cases until the end of input: `n m`, then `m` directed edges `u v` (1 ≤ n ≤ 2·10⁵, m ≤ 4·10⁵). The driver appends `v` to `adj[u]` in input order.

**Output (printed by the driver):** the four edge counts, then `tin`/`tout` (or a checksum when n > 12).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

struct DfsResult { vector<int> tin, tout; long long tree = 0, back = 0, fwd = 0, cross = 0; };

DfsResult dfs_times(int n, const vector<vector<int>>& adj) {
    DfsResult r; r.tin.assign(n, 0); r.tout.assign(n, 0);
    return r;                          // TODO
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n, m;
    while (cin >> n >> m) {
        vector<vector<int>> adj(n);
        for (int i = 0; i < m; ++i) { int u, v; cin >> u >> v; adj[u].push_back(v); }
        DfsResult r = dfs_times(n, adj);
        cout << "tree " << r.tree << " back " << r.back << " forward " << r.fwd << " cross " << r.cross << '\n';
        if ((int)r.tin.size() != n || (int)r.tout.size() != n) { cout << "wrong sizes\n"; continue; }
        if (n <= 12) {
            for (int i = 0; i < n; ++i) cout << r.tin[i] << '/' << r.tout[i] << (i + 1 < n ? ' ' : '\n');
        } else {
            unsigned long long h = 0;
            for (int i = 0; i < n; ++i) h = h * 1000003 + (unsigned)r.tin[i] * 7 + (unsigned)r.tout[i];
            cout << "checksum " << h << '\n';
        }
    }
}
```

## Tests
=== sample
4 5
0 1
1 2
2 0
0 2
3 1
---
tree 2 back 1 forward 1 cross 1
0/5 1/4 2/3 6/7
=== sample
3 1
1 1
---
tree 0 back 1 forward 0 cross 0
0/1 2/3 4/5
=== hidden
1 0
---
tree 0 back 0 forward 0 cross 0
0/1
=== hidden
5 6
0 1
0 2
1 3
2 3
3 4
0 4
---
tree 4 back 0 forward 1 cross 1
0/9 1/6 7/8 2/5 3/4
=== hidden
4 4
3 2
2 1
1 0
0 3
---
tree 3 back 1 forward 0 cross 0
0/7 3/4 2/5 1/6
=== hidden
6 2
1 2
2 3
3 10
1 0
2 2
1 0
1 2
0 1
1 2
1 1
0 2
2 1
0 2
3 9
1 0
2 2
2 2
1 1
1 2
0 0
2 0
0 2
2 1
3 1
0 1
---
tree 2 back 0 forward 0 cross 0
0/1 2/7 3/6 4/5 8/9 10/11
tree 2 back 5 forward 3 cross 0
0/5 1/4 2/3
tree 2 back 7 forward 0 cross 0
0/5 2/3 1/4
tree 1 back 0 forward 0 cross 0
0/3 1/2 4/5
=== hidden
5 11
2 3
1 4
2 2
1 1
3 4
1 2
0 3
4 4
1 0
1 3
3 4
1 11
0 0
0 0
0 0
0 0
0 0
0 0
0 0
0 0
0 0
0 0
0 0
4 11
2 2
3 1
3 0
0 0
2 0
2 0
2 2
1 3
3 2
2 0
2 1
7 0
---
tree 3 back 3 forward 1 cross 4
0/5 6/9 7/8 1/4 2/3
tree 0 back 11 forward 0 cross 0
0/1
tree 2 back 5 forward 0 cross 4
0/1 2/7 4/5 3/6
tree 0 back 0 forward 0 cross 0
0/1 2/3 4/5 6/7 8/9 10/11 12/13
=== hidden
2 2
0 1
0 0
5 12
4 2
2 2
2 1
3 4
3 3
4 2
0 3
1 3
1 0
3 3
1 0
0 0
6 2
0 2
4 1
2 5
0 1
1 0
0 0
1 1
0 1
---
tree 1 back 1 forward 0 cross 0
0/3 1/2
tree 4 back 7 forward 1 cross 0
0/9 4/5 3/6 1/8 2/7
tree 1 back 0 forward 0 cross 1
0/3 4/5 1/2 6/7 8/9 10/11
tree 1 back 3 forward 1 cross 0
0/3 1/2
=== hidden
@gen 2387007255 big
=== hidden
@gen 2387007256 big
=== hidden
@gen 2387007257 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(4 if not big else 1):
    if not big:
        n = r.randint(1, 8); m = r.randint(0, 14)
        print(n, m)
        for _ in range(m): print(r.randrange(n), r.randrange(n))
    else:
        n = 200000
        es = [(i, i + 1) for i in range(n - 1)]        # a 2e5-deep path forces non-recursive DFS
        es += [(r.randrange(n), r.randrange(n)) for _ in range(200000)]
        r.shuffle(es)
        print(n, len(es))
        for u, v in es: print(u, v)
```

## Hints
- Keep a stack of active vertices and, for each vertex, an index into its adjacency list saying which neighbour comes next.
- Each iteration examines exactly one edge of the top vertex. If the top vertex has no edges left, stamp its finish time and pop it.
- Classify with the state of `v`: unvisited (tree), discovered but unfinished (back), finished with a larger `tin` (forward), otherwise cross.

## Solution
**Simulate the call stack exactly.** A recursive DFS frame for `u` remembers one thing besides `u`: how far it got through `adj[u]`. Store that position in `it[u]`, and keep the active vertices on an explicit stack. Each loop iteration looks at the top vertex `u`: if it has unexamined edges, examine the next one; if that edge reaches an unvisited `v`, discover `v` and push it (the "recursive call"). If `u` has no edges left, finish it and pop (the "return"). Because only **one** edge is examined before looking at the top again, the discovery and finish order is identical to the recursive version.

> A common shortcut, "pop `u`, push all its unvisited neighbours", is **not** a DFS in this sense: it discovers neighbours too early and has no finish event, so timestamps and edge classes come out wrong.

**Classification from timestamps.** When `u` examines `u → v`:
- `v` unvisited → tree edge.
- `v` discovered but not finished → it is an ancestor on the current path (or `u` itself) → back edge. Back edges are exactly what make a directed cycle.
- `v` finished and `tin[u] < tin[v]` → `v` was discovered *after* `u` and is already done → it's a descendant reached earlier through another path → forward edge.
- `v` finished and `tin[v] < tin[u]` → it lives in an earlier, completed subtree or tree → cross edge.

**Parenthesis theorem.** The intervals `[tin, tout]` of any two vertices are either nested (one is an ancestor of the other) or disjoint. That is why `tin[u] ≤ tin[v] && tout[v] ≤ tout[u]` is an O(1) ancestor test once the DFS has run.

Complexity: O(n + m) time, O(n) extra memory, no recursion.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct DfsResult { vector<int> tin, tout; long long tree = 0, back = 0, fwd = 0, cross = 0; };

DfsResult dfs_times(int n, const vector<vector<int>>& adj) {
    DfsResult r;
    r.tin.assign(n, -1); r.tout.assign(n, -1);
    vector<int> it(n, 0);                  // it[u] = index of the next neighbour of u to examine
    vector<int> stk;                       // the current DFS path (the "recursion stack")
    int clock = 0;
    for (int root = 0; root < n; ++root) {
        if (r.tin[root] != -1) continue;
        r.tin[root] = clock++; stk.push_back(root);
        while (!stk.empty()) {
            int u = stk.back();
            if (it[u] == (int)adj[u].size()) {         // all neighbours done: u finishes
                r.tout[u] = clock++; stk.pop_back();
                continue;
            }
            int v = adj[u][it[u]++];                   // examine ONE edge, then loop again
            if (r.tin[v] == -1) {                      // tree edge: "recurse" into v
                ++r.tree; r.tin[v] = clock++; stk.push_back(v);
            } else if (r.tout[v] == -1) ++r.back;      // v is on the current path
            else if (r.tin[u] < r.tin[v]) ++r.fwd;     // v is a finished descendant
            else ++r.cross;                            // v finished earlier, elsewhere
        }
    }
    return r;
}
```
