---
id: cpp-topo-count-orders
title: Count the Topological Orders (Bitmask DP)
difficulty: Hard
order: 8
tags: topological sort, counting, bitmask DP, subsets, modular arithmetic
time_limit: 2
---
## Statement
Count the topological orders of a directed graph with at most 20 vertices, modulo `10⁹ + 7`. (A graph with a cycle has 0.)

```cpp
long long count_orders(int n, const std::vector<std::pair<int,int>>& edges);
```

Enumerating permutations costs `n!`, which is 2.4·10¹⁸ for `n = 20`. But an order is built one vertex at a time, and what matters for the future is only **which set** of vertices is already placed, not in which order. Let `dp[S]` be the number of ways to order exactly the set `S` as a valid prefix. A vertex `v ∉ S` can come next iff all its predecessors are in `S`. Store each vertex's predecessors as a bitmask `pred[v]`; the test is `(pred[v] & S) == pred[v]`.

**Input:** cases until the end of input: `n m`, then `m` edges `u v` (1 ≤ n ≤ 20, 0 ≤ m ≤ 190; at most 3 cases with n > 16).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

long long count_orders(int n, const vector<pair<int,int>>& edges) {
    // tries every permutation: n! is hopeless beyond n = 11
    vector<int> p(n); iota(p.begin(), p.end(), 0); long long c = 0;
    do { vector<int> pos(n); for (int i = 0; i < n; ++i) pos[p[i]] = i; bool ok = true;
         for (auto [u, v] : edges) if (pos[u] >= pos[v]) { ok = false; break; } c += ok; } while (next_permutation(p.begin(), p.end()));
    return c % 1000000007;
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
        cout << count_orders(n, e) << '\n';
    }
}
```

## Tests
=== sample
3 1
0 1
---
3
=== sample
4 3
0 1
1 2
2 3
---
1
=== sample
3 3
0 1
1 2
2 0
---
0
=== hidden
1 0
---
1
=== hidden
1 1
0 0
---
0
=== hidden
5 0
---
120
=== hidden
4 4
0 1
0 2
1 3
2 3
---
2
=== hidden
20 0
---
146326063
=== hidden
20 2
0 1
2 3
---
786581521
=== hidden
4 1
1 0
6 0
3 0
7 3
5 4
5 1
3 2
3 4
0 1
0 2
2 1
2 1
6 0
1 1
0 0
3 2
1 0
0 2
---
12
720
6
840
1
720
0
1
=== hidden
7 1
6 1
6 1
5 0
4 1
0 2
2 4
0 1
0 1
0 1
0 1
4 0
5 0
4 1
1 0
4 2
3 1
3 1
---
2520
360
12
1
24
120
12
12
=== hidden
7 1
1 2
2 0
4 5
2 0
2 3
2 1
2 3
2 1
5 6
2 1
2 1
1 1
1 0
1 4
1 3
3 0
5 0
7 3
5 2
2 3
3 3
5 0
---
2520
2
6
0
6
120
0
120
=== hidden
20 2
5 4
11 12
20 2
2 0
4 6
20 0
---
786581521
786581521
146326063
=== hidden
20 9
3 7
19 9
15 2
17 9
18 16
19 19
1 17
18 3
16 1
20 1
1 0
20 2
10 15
1 13
---
0
573163035
786581521
=== hidden
20 1
9 2
20 4
6 4
10 19
10 8
15 11
20 9
3 11
6 19
14 9
2 7
8 12
16 13
18 5
16 18
0 17
---
573163035
595527176
701457673

## Hints
- After placing some vertices, the future depends only on which set is placed, not on its order.
- Let `dp[mask]` be the number of valid orders of exactly the vertices in `mask`.
- A vertex `v` can extend `mask` iff `pred[v]` is a subset of `mask`; iterate masks in increasing order.

## Solution
**State = the set already placed.** Two prefixes with the same vertex set have exactly the same possible continuations, because the only question for a vertex `v` is whether all its predecessors are already placed. So the number of complete orders splits over sets: `dp[S]` counts valid orderings of exactly `S`, and `dp[S ∪ {v}] += dp[S]` for every `v` that may follow `S`.

**Bitmasks.** Encode `S` as an integer with bit `i` set when vertex `i` is placed, and `pred[v]` as the mask of `v`'s predecessors. "All predecessors placed" is `(pred[v] & S) == pred[v]`. Masks only grow, so iterating `S` from 0 upwards processes every set after all its subsets.

**Cycles.** If the graph has a cycle, no vertex on it can ever be added (its predecessor on the cycle is never placed first), so `dp[full] = 0` automatically. Self-loops make `pred[v]` contain `v` itself, which is never in `S` before `v`: also 0.

**Cost.** `2ⁿ · n` = 2·10⁷ steps for `n = 20`, with `2ⁿ` `long long`s (8 MB) of memory. This "DP over subsets" pattern also solves travelling-salesman-style problems and assignment problems with `n ≤ 20`.

Complexity: O(2ⁿ · n) time, O(2ⁿ) memory.

```cpp
#include <bits/stdc++.h>
using namespace std;

long long count_orders(int n, const vector<pair<int,int>>& edges) {
    const long long MOD = 1'000'000'007;
    vector<int> pred(n, 0);
    for (auto [u, v] : edges) pred[v] |= 1 << u;          // u must be placed before v
    vector<long long> dp(1 << n, 0);
    dp[0] = 1;                                            // the empty prefix
    for (int S = 0; S < (1 << n); ++S) {
        if (!dp[S]) continue;                             // unreachable set (or a set blocked by a cycle)
        for (int v = 0; v < n; ++v)
            if (!(S >> v & 1) && (pred[v] & S) == pred[v])          // v is free to come next
                dp[S | 1 << v] = (dp[S | 1 << v] + dp[S]) % MOD;
    }
    return dp[(1 << n) - 1];
}
```
