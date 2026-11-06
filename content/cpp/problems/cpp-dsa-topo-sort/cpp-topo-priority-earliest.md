---
id: cpp-topo-priority-earliest
title: Urgent Tasks First: Task 0 as Early as Possible, Then Task 1, …
difficulty: Hard
order: 7
tags: topological sort, reverse graph, max-heap, exchange argument, tie-breaking
time_limit: 2
---
## Statement
Tasks `0 … n−1` have precedence constraints `u v` (`u` before `v`). Task 0 is the most urgent, task 1 the next, and so on. Find the topological order that places task 0 **as early as possible**; among those, task 1 as early as possible; among those, task 2; and so on. Formally, minimise the vector `(pos[0], pos[1], …, pos[n−1])` lexicographically, where `pos[x]` is the position of task `x`. Return the order, or an empty vector if there is a cycle.

```cpp
std::vector<int> priority_order(int n, const std::vector<std::pair<int,int>>& edges);
```

This is **not** the lexicographically smallest order. With `2 → 0` and task `1` free, the smallest order is `1 2 0`, but `2 0 1` puts task 0 at position 1 instead of 2. Greedy from the front fails, because the front choice should be "whatever leads to task 0 soonest", which a min-heap can't see. The trick is to build the order **from the back**: reverse every edge, repeatedly output the **largest** available label (max-heap), and reverse the result.

**Input:** cases until the end of input: `n m`, then `m` edges `u v` (1 ≤ n ≤ 2·10⁵, 0 ≤ m ≤ 4·10⁵).

**Output (printed by the driver):** `cycle`, or the order (a checksum when n > 30).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> priority_order(int n, const vector<pair<int,int>>& edges) {
    // the tempting wrong answer: lexicographically smallest order (min-heap from the front)
    vector<vector<int>> adj(n); vector<int> indeg(n, 0);
    for (auto [u, v] : edges) { adj[u].push_back(v); ++indeg[v]; }
    priority_queue<int, vector<int>, greater<int>> pq;
    for (int i = 0; i < n; ++i) if (!indeg[i]) pq.push(i);
    vector<int> o;
    while (!pq.empty()) { int u = pq.top(); pq.pop(); o.push_back(u); for (int v : adj[u]) if (--indeg[v] == 0) pq.push(v); }
    if ((int)o.size() < n) return {};
    return o;
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
        vector<int> o = priority_order(n, e);
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
3 1
2 0
---
2 0 1
=== sample
5 3
4 0
3 1
2 4
---
2 4 0 3 1
=== sample
2 2
0 1
1 0
---
cycle
=== hidden
1 0
---
0
=== hidden
4 2
3 0
2 1
---
3 0 2 1
=== hidden
5 4
4 0
3 0
1 4
2 3
---
1 2 3 4 0
=== hidden
6 4
5 0
5 1
4 2
3 2
---
5 0 1 3 4 2
=== hidden
6 2
5 3
3 2
4 2
0 3
0 2
1 0
7 0
5 0
6 2
0 2
1 3
---
0 1 5 3 2 4
0 1 2 3
0
0 1 2 3 4 5 6
0 1 2 3 4
0 1 2 3 4 5
=== hidden
2 0
7 1
4 3
5 4
4 1
2 3
4 3
2 0
6 2
2 1
5 1
1 0
3 0
---
0 1
0 1 2 4 3 5 6
2 0 4 1 3
0 2 5 1 3 4
0
0 1 2
=== hidden
1 0
3 1
1 2
6 1
4 5
6 3
4 5
3 0
3 4
3 0
7 0
---
0
0 1 2
0 1 2 3 4 5
3 0 1 2 4 5
0 1 2
0 1 2 3 4 5 6
=== hidden
@gen 3923822364 big
=== hidden
@gen 3923822365 big
=== hidden
@gen 3923822366 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 1):
    if not big:
        n = r.randint(1, 7); m = r.randint(0, 7)
        perm = list(range(n)); r.shuffle(perm)
        dag = r.random() < 0.85
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
        es = [(perm[a], perm[b]) for a, b in (sorted((r.randrange(n), r.randrange(n))) for _ in range(300000)) if a < b]
        print(n, len(es))
        for u, v in es: print(u, v)
```

## Hints
- The lexicographically smallest order is not the answer: small irrelevant tasks may push task 0 back.
- Decide the last position first. Only tasks with no dependants can go last; which one should it be?
- Reverse the edges, run Kahn's algorithm with a max-heap, then reverse the sequence you produced.

## Solution
**Why the front-greedy fails.** To bring task 0 forward you may have to schedule some of its prerequisites first, even if they have large labels. A min-heap from the front happily outputs small but irrelevant tasks first and pushes task 0 back.

**Fill the order from the end.** Look at the **last** position. Only a task that nothing depends on (out-degree 0) can go there. Among those candidates, put the **largest label** last. Then repeat on the remaining tasks for the second-to-last position. In the reversed graph that is Kahn's algorithm with a max-heap.

**Exchange argument (sketch).** Let `x` be the largest-label candidate for the last slot, and suppose an optimal order ends with some other candidate `y < x`. In that order, `x` sits somewhere earlier, and every task after `x` is free to move (nothing after `x` depends on `x`, because `x` has no dependants left). Move `x` to the very end: everything that was after it shifts one place earlier. All those tasks, including `y`, gain or keep their positions, and the only task that loses is `x`, which is less urgent than `y`. The first differing entry of the `pos` vector improves or stays, so ending with `x` is never worse. Induction on the remaining tasks completes the proof.

**Equivalence.** Minimising `(pos[0], pos[1], …)` is the same as making the **reversed** order lexicographically **largest**, which is exactly what the max-heap from the back produces.

Complexity: O(n log n + m).

```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> priority_order(int n, const vector<pair<int,int>>& edges) {
    vector<vector<int>> radj(n);                 // reversed: v -> u for each u -> v
    vector<int> outdeg(n, 0);                    // in-degree in the reversed graph
    for (auto [u, v] : edges) { radj[v].push_back(u); ++outdeg[u]; }
    priority_queue<int> pq;                      // MAX-heap
    for (int i = 0; i < n; ++i) if (!outdeg[i]) pq.push(i);   // tasks nothing waits for can go last
    vector<int> back;                            // the order, built from the last position backwards
    back.reserve(n);
    while (!pq.empty()) {
        int v = pq.top(); pq.pop();              // the least urgent candidate takes the last free slot
        back.push_back(v);
        for (int u : radj[v]) if (--outdeg[u] == 0) pq.push(u);
    }
    if ((int)back.size() < n) return {};
    reverse(back.begin(), back.end());
    return back;
}
```
