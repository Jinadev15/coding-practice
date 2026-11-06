---
id: cpp-topo-completable
title: Course Schedule: How Many Courses Can Be Completed?
difficulty: Easy
order: 1
tags: topological sort, Kahn's algorithm, in-degree, DAG
time_limit: 2
---
## Statement
There are `n` courses `0 … n−1`. A prerequisite pair `u v` means course `u` must be completed **before** course `v`. A course can be taken once all of its prerequisites are completed. Return the number of courses that can eventually be completed. (All `n` of them exactly when the prerequisite graph has no cycle.)

```cpp
int completable(int n, const std::vector<std::pair<int,int>>& pre);
```

**Kahn's algorithm** simulates the semester office: keep each course's number of unfinished prerequisites (its **in-degree**), start with every course whose in-degree is 0, and whenever a course is completed, decrement the in-degree of the courses that depend on it. Courses on a cycle, or depending on one, never reach in-degree 0.

**Input:** cases until the end of input: `n m`, then `m` pairs `u v` (1 ≤ n ≤ 2·10⁵, 0 ≤ m ≤ 4·10⁵; repeated pairs and `u == v` may appear).

**Output (printed by the driver):** `all` if every course can be completed, otherwise the number that can.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

int completable(int n, const vector<pair<int,int>>& pre) {
    return n;                          // TODO: assumes there is never a cycle
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
        int k = completable(n, p);
        if (k == n) cout << "all\n"; else cout << k << '\n';
    }
}
```

## Tests
=== sample
4 3
0 1
1 2
2 3
---
all
=== sample
4 4
0 1
1 2
2 1
2 3
---
1
=== hidden
1 0
---
all
=== hidden
1 1
0 0
---
0
=== hidden
3 2
0 1
0 1
---
all
=== hidden
6 6
0 1
1 0
2 3
3 4
1 4
5 5
---
2
=== hidden
1 0
7 8
1 4
1 2
6 6
0 1
0 5
3 1
3 1
2 4
4 3
2 3
0 2
2 3
6 7
0 5
2 4
3 0
4 1
2 2
5 1
0 3
7 0
6 1
0 5
---
all
6
all
0
all
all
=== hidden
2 5
0 1
1 1
0 1
0 1
1 0
3 2
0 1
0 1
5 0
8 2
3 7
5 7
4 3
2 3
0 1
2 3
6 3
5 2
2 2
1 3
---
0
all
all
all
all
5
=== hidden
7 3
6 6
2 3
2 5
5 3
0 4
1 2
0 2
7 4
6 5
5 5
4 4
4 0
4 6
1 3
1 2
1 0
0 1
0 3
3 1
8 0
7 7
5 0
3 0
3 6
3 6
4 5
5 3
5 3
---
6
all
4
0
all
all
=== hidden
@gen 1523228644 big
=== hidden
@gen 1523228645 big
=== hidden
@gen 1523228646 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 1):
    if not big:
        n = r.randint(1, 8); m = r.randint(0, 10)
        dag = r.random() < 0.5
        es = []
        for _ in range(m):
            u, v = r.randrange(n), r.randrange(n)
            if dag and u >= v: continue
            es.append((u, v))
        print(n, len(es))
        for u, v in es: print(u, v)
    else:
        n = 200000
        perm = list(range(n)); r.shuffle(perm)
        es = [(perm[i], perm[i + 1]) for i in range(n - 1)]
        es += [(perm[a], perm[b]) for a, b in (sorted((r.randrange(n), r.randrange(n))) for _ in range(200000)) if a < b]
        if r.random() < 0.7: k = r.randrange(n // 2, n); es.append((perm[k], perm[k - 3]))
        r.shuffle(es)
        print(n, len(es))
        for u, v in es: print(u, v)
```

## Hints
- A course is available when all its prerequisites are done. Track, for every course, how many prerequisites are still unfinished.
- Start with all courses that have no prerequisites; completing a course decrements the counters of the courses that depend on it.
- The courses that are never released sit on, or behind, a cycle.

## Solution
**In-degree as "prerequisites left".** Course `v` can be taken exactly when every `u` with an edge `u → v` is done. Count those edges as `indeg[v]`. A course with in-degree 0 is available right now.

**Kahn's algorithm.** Put all available courses in a queue. Completing one removes its outgoing edges, decrementing the in-degree of its dependants; any that reach 0 become available. Each course enters the queue once (when its count hits 0) and each edge is removed once, so this is O(n + m).

**What's left over.** A course on a directed cycle can never reach in-degree 0: the cycle's courses all wait for each other. Courses that depend on a cycle (directly or indirectly) also keep a positive count. So the number of courses ever pushed is exactly the number that can be completed, and it equals `n` iff the graph is a DAG.

**Edge cases.** A self-loop `u u` gives `indeg[u] ≥ 1` that nobody can remove, so `u` is never completable. A repeated pair adds 2 to the in-degree, and both copies are removed when `u` completes, so it is harmless.

Complexity: O(n + m).

```cpp
#include <bits/stdc++.h>
using namespace std;

int completable(int n, const vector<pair<int,int>>& pre) {
    vector<vector<int>> adj(n);
    vector<int> indeg(n, 0);
    for (auto [u, v] : pre) { adj[u].push_back(v); ++indeg[v]; }   // repeated pairs count twice, and are removed twice
    vector<int> q;
    for (int i = 0; i < n; ++i) if (indeg[i] == 0) q.push_back(i);
    for (size_t h = 0; h < q.size(); ++h)
        for (int v : adj[q[h]])
            if (--indeg[v] == 0) q.push_back(v);   // last prerequisite done: v becomes available
    return (int)q.size();                           // every course ever pushed was completed
}
```
