---
id: cpp-topo-critical-path
title: Project Scheduling: Critical Path
difficulty: Medium
order: 5
tags: DAG, longest path, dynamic programming on a DAG, critical path method, slack
time_limit: 2
---
## Statement
A project has `n` tasks. Task `i` takes `d[i]` days. A dependency `u v` means `v` can start only after `u` has **finished**. Any number of tasks can run in parallel. The dependency graph is guaranteed to be a DAG.

Compute:
1. `T`, the minimum number of days to finish the whole project (start at day 0), and
2. the number of **critical** tasks: tasks whose start cannot be delayed by even one day without delaying the project.

```cpp
std::pair<long long,int> critical_path(int n, const std::vector<long long>& d,
                                       const std::vector<std::pair<int,int>>& deps);
```

This is the **critical path method** used in construction and engineering planning. In topological order, the earliest start is `ES[v] = max(EF[u])` over the predecessors `u` (0 if none), with `EF = ES + d`. Then `T = max EF`. In **reverse** topological order, the latest finish is `LF[u] = min(LS[v])` over the successors (`T` if none), with `LS = LF − d`. A task is critical iff its **slack** `LS − ES` is 0.

**Input:** cases until the end of input: `n m`, then `n` durations, then `m` dependencies `u v` (1 ≤ n ≤ 2·10⁵, 0 ≤ m ≤ 4·10⁵, 1 ≤ d[i] ≤ 10⁹).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

pair<long long,int> critical_path(int n, const vector<long long>& d, const vector<pair<int,int>>& deps) {
    // ignores parallelism: as if every task ran one after another
    long long t = 0; for (long long x : d) t += x;
    return {t, n};
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n, m;
    while (cin >> n >> m) {
        vector<long long> d(n);
        for (auto& x : d) cin >> x;
        vector<pair<int,int>> e(m);
        for (auto& [u, v] : e) cin >> u >> v;
        auto [T, c] = critical_path(n, d, e);
        cout << T << ' ' << c << '\n';
    }
}
```

## Tests
=== sample
6 6
3 2 4 1 5 2
0 1
0 2
1 3
2 3
3 4
2 5
---
13 4
=== sample
3 0
5 9 9
---
9 2
=== hidden
1 0
1000000000
---
1000000000 1
=== hidden
4 3
1 1 1 1
0 3
1 3
2 3
---
2 4
=== hidden
5 6
2 2 2 2 2
0 1
1 2
0 2
2 3
3 4
0 4
---
10 5
=== hidden
3 2
4 1 3
0 1
0 1
---
5 2
=== hidden
4 7
3 3 1 5
0 2
2 1
3 1
3 2
2 1
0 3
3 2
7 0
5 1 5 5 3 2 2
1 0
3
4 4
2 5 3 5
3 2
0 2
1 2
3 2
1 0
5
8 2
5 1 3 2 4 4 4 5
5 4
6 5
---
12 4
5 3
3 1
8 3
5 1
12 3
=== hidden
7 0
5 3 2 4 1 2 2
6 4
1 4 3 1 1 4
3 2
1 0
5 0
4 0
8 7
1 3 2 5 2 1 4 3
0 6
7 2
0 6
4 2
1 2
4 0
1 0
8 5
2 2 3 3 3 1 3 1
6 1
5 3
2 5
7 0
3 1
7 4
4 2 3 5 1 3 1
2 5
3 0
3 0
5 4
5 1
2 1 5 2 4
2 3
---
5 1
5 3
8 3
9 4
9 2
7 2
=== hidden
8 4
3 2 3 2 2 3 3 1
0 4
0 4
2 5
7 5
4 6
3 4 4 4
1 3
1 0
1 2
1 3
1 3
1 2
8 9
4 3 3 4 5 1 3 5
4 6
3 0
4 7
2 6
4 3
4 2
5 3
2 0
7 3
5 3
1 4 3 1 1
3 0
2 0
0 1
5 7
2 5 1 1 3
3 4
1 0
3 2
4 2
0 3
1 0
3 4
6 8
4 2 1 3 3 4
3 0
0 4
5 4
3 0
3 4
0 2
1 4
3 0
---
6 2
8 3
18 4
8 3
12 5
10 3
=== hidden
@gen 1386415450 big
=== hidden
@gen 1386415451 big
=== hidden
@gen 1386415452 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 1):
    if not big:
        n = r.randint(1, 8); m = r.randint(0, 10)
        d = [r.randint(1, 5) for _ in range(n)]
    else:
        n = 200000; m = 380000
        d = [r.randint(1, 10**9) for _ in range(n)]
    perm = list(range(n)); r.shuffle(perm)
    es = []
    for _ in range(m):
        a, b = r.randrange(n), r.randrange(n)
        if a == b: continue
        if a > b: a, b = b, a
        if big and b - a > 50 and r.random() < 0.9: b = a + r.randint(1, 50)
        es.append((perm[a], perm[b]))
    print(n, len(es)); print(*d)
    for u, v in es: print(u, v)
```

## Hints
- With unlimited parallelism, the project length is the longest duration-weighted chain of dependencies.
- Compute earliest starts in topological order: a task starts when its last predecessor finishes.
- Compute latest finishes in reverse topological order, starting from `T`. Critical tasks have latest start equal to earliest start.

## Solution
**Longest path in a DAG.** The project can't finish before its longest chain of dependent tasks (weighted by duration), and with unlimited parallelism it finishes exactly then. Longest path is NP-hard in general graphs, but in a DAG it is a simple DP: process vertices in topological order, so all predecessors of `v` are final before `v` is used: `ES[v] = max over u→v of ES[u] + d[u]`.

**Latest times.** Run the same DP backwards. A task with no successors may finish as late as `T`. Otherwise it must finish before the latest start of each successor: `LF[u] = min over u→v of (LF[v] − d[v])`. Processing in **reverse** topological order makes every successor final first.

**Slack and the critical path.** `slack = LS − ES = LF − d − ES` is how long a task can slip without moving `T`. Tasks with slack 0 form (one or more) longest chains: the critical path(s). Managers watch exactly these tasks.

**Overflow.** Sums of up to 2·10⁵ durations of 10⁹ reach 2·10¹⁴, so use `long long`.

Complexity: O(n + m): one topological sort and two linear passes.

```cpp
#include <bits/stdc++.h>
using namespace std;

pair<long long,int> critical_path(int n, const vector<long long>& d, const vector<pair<int,int>>& deps) {
    vector<vector<int>> adj(n), radj(n);
    vector<int> indeg(n, 0);
    for (auto [u, v] : deps) { adj[u].push_back(v); radj[v].push_back(u); ++indeg[v]; }
    vector<int> topo;                                    // Kahn: a topological order
    for (int i = 0; i < n; ++i) if (!indeg[i]) topo.push_back(i);
    for (size_t h = 0; h < topo.size(); ++h) for (int v : adj[topo[h]]) if (--indeg[v] == 0) topo.push_back(v);
    vector<long long> ES(n, 0), LF(n);
    for (int u : topo)                                   // forward pass: earliest starts
        for (int v : adj[u]) ES[v] = max(ES[v], ES[u] + d[u]);
    long long T = 0;
    for (int i = 0; i < n; ++i) T = max(T, ES[i] + d[i]);
    fill(LF.begin(), LF.end(), T);
    for (int k = n - 1; k >= 0; --k) {                   // backward pass: latest finishes
        int v = topo[k];
        for (int u : radj[v]) LF[u] = min(LF[u], LF[v] - d[v]);   // u must end before v's latest start
    }
    int critical = 0;
    for (int i = 0; i < n; ++i) critical += (LF[i] - d[i] == ES[i]);   // slack 0
    return {T, critical};
}
```
