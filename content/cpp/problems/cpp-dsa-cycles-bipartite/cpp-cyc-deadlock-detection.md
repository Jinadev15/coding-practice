---
id: cpp-cyc-deadlock-detection
title: Deadlock Detection with Multi-Instance Resources
difficulty: Hard
order: 8
tags: deadlock, wait-for graph, graph reduction, operating systems, event-driven pointers
time_limit: 2
---
## Statement
An operating system has `k` resource types. `avail[j]` instances of type `j` are free. Process `i` currently **holds** `alloc[i][j]` instances of type `j` and is **waiting** for `req[i][j]` more. A process whose whole request can be granted from the free pool runs to completion and **releases everything it holds**, which may unblock others. Processes that can never be satisfied, no matter in which order the others finish, are **deadlocked**. Return them in increasing order.

```cpp
std::vector<int> deadlocked(int n, int k, std::vector<long long> avail,
                            const std::vector<std::vector<long long>>& alloc,
                            const std::vector<std::vector<long long>>& req);
```

With one instance per resource this is cycle detection in the **wait-for graph** (`p → q` when `p` waits for something `q` holds). With several instances a cycle no longer implies deadlock, so the OS runs **graph reduction**: repeatedly pick any process with `req[i] ≤ work` (component-wise), add its `alloc[i]` to `work`, and mark it finished. Order doesn't matter, because `work` only grows. Whatever is left is deadlocked.

The textbook loop rescans all processes after each completion: O(n²·k), far too slow when completions trickle out one per pass. Make it event-driven: for each type `j`, sort the processes by `req[i][j]` and keep a pointer into that order. `work[j]` only increases, so the pointer only moves forward. Count, per process, how many types are already satisfied; at `k`, the process can finish.

**Input:** cases until the end of input: `n k`, then `k` values `avail`, then `n` lines of `2k` values: `alloc[i][0..k−1]` followed by `req[i][0..k−1]` (1 ≤ n·k ≤ 5·10⁵, 0 ≤ values ≤ 10⁹).

**Output (printed by the driver):** the number of deadlocked processes, then the list (or a checksum when there are more than 30).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> deadlocked(int n, int k, vector<long long> avail,
                       const vector<vector<long long>>& alloc, const vector<vector<long long>>& req) {
    // textbook detection loop: correct, but O(n^2 * k) when processes finish one per pass
    vector<char> done(n, 0);
    bool progress = true;
    while (progress) {
        progress = false;
        for (int i = 0; i < n; ++i) {
            if (done[i]) continue;
            bool ok = true;
            for (int j = 0; j < k && ok; ++j) ok = req[i][j] <= avail[j];
            if (ok) { done[i] = 1; progress = true; for (int j = 0; j < k; ++j) avail[j] += alloc[i][j]; }
        }
    }
    vector<int> r; for (int i = 0; i < n; ++i) if (!done[i]) r.push_back(i);
    return r;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n, k;
    while (cin >> n >> k) {
        vector<long long> av(k);
        for (auto& x : av) cin >> x;
        vector<vector<long long>> al(n, vector<long long>(k)), rq(n, vector<long long>(k));
        for (int i = 0; i < n; ++i) { for (auto& x : al[i]) cin >> x; for (auto& x : rq[i]) cin >> x; }
        vector<int> d = deadlocked(n, k, av, al, rq);
        cout << d.size() << ':';
        unsigned long long h = 0;
        for (int x : d) h = h * 1000003 + (unsigned)x;
        if (d.size() <= 30) for (int x : d) cout << ' ' << x;
        else cout << " checksum " << h;
        cout << '\n';
    }
}
```

## Tests
=== sample
5 3
0 0 0
0 1 0 0 0 0
2 0 0 2 0 2
3 0 3 0 0 0
2 1 1 1 0 0
0 0 2 0 0 2
---
0:
=== sample
3 1
1
1 2
1 2
1 1
---
0:
=== hidden
1 1
0
5 0
---
0:
=== hidden
1 2
3 4
0 0 3 5
---
1: 0
=== hidden
4 2
0 0
1 0 0 1
0 1 1 0
5 5 0 0
0 0 6 0
---
0:
=== hidden
2 1
1000000000
1000000000 1000000000
1000000000 2000000000
---
0:
=== hidden
5 2
2 0
1 1 1 2
2 3 4 4
0 3 4 2
2 3 4 0
2 1 2 1
5 1
2
0 4
3 2
2 0
0 3
3 2
1 2
2 2
3 1 2 0
6 1
2
2 3
1 4
0 0
3 3
1 2
3 2
5 1
2
2 3
3 4
2 0
1 3
0 4
5 3
0 0 1
0 3 0 4 1 0
2 3 0 4 1 3
1 1 3 4 0 1
1 0 0 2 4 4
0 2 1 1 2 4
---
5: 0 1 2 3 4
0:
0:
0:
0:
5: 0 1 2 3 4
=== hidden
3 3
2 2 1
3 2 0 3 1 2
2 0 2 2 4 3
2 0 1 2 3 4
5 1
1
2 3
1 1
2 0
2 0
0 3
1 3
1 2 2
0 1 1 3 1 2
1 3
0 2 1
2 1 1 2 3 0
4 3
0 1 1
2 2 3 2 4 1
3 3 2 4 2 3
2 2 0 1 4 1
1 1 1 4 1 2
4 3
0 2 2
3 0 0 1 3 3
3 3 2 4 0 3
2 2 2 1 3 3
1 2 0 1 4 2
---
3: 0 1 2
0:
1: 0
1: 0
4: 0 1 2 3
4: 0 1 2 3
=== hidden
3 2
1 1
1 0 3 1
1 3 0 4
0 1 2 0
4 2
0 1
0 3 4 2
0 0 1 1
1 3 0 0
0 0 4 1
6 2
0 0
1 0 2 2
1 0 4 1
0 1 2 4
3 1 1 1
3 3 3 2
3 2 0 4
1 3
0 0 0
0 2 0 2 4 3
5 2
0 0
2 1 0 0
2 2 0 2
3 0 1 0
1 3 1 1
0 3 1 4
2 3
1 2 1
1 3 2 4 1 3
2 1 0 4 3 2
---
3: 0 1 2
2: 0 3
6: 0 1 2 3 4 5
1: 0
0:
2: 0 1
=== hidden
@gen 791878554 big
=== hidden
@gen 791878555 big
=== hidden
@gen 791878556 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 1):
    if not big:
        n, k = r.randint(1, 6), r.randint(1, 3)
        print(n, k); print(*[r.randint(0, 2) for _ in range(k)])
        for _ in range(n): print(*([r.randint(0, 3) for _ in range(k)] + [r.randint(0, 4) for _ in range(k)]))
    else:
        n, k = 50000, 10
        print(n, k)
        print(*([10**9] * (k - 1) + [1]))
        # reverse chain on the LAST type: process n-1 finishes first, then n-2, ... (worst case for rescanning)
        stuck = set(r.sample(range(n), 5)) if r.random() < 0.7 else set()
        later = 0                                   # non-stuck processes with a larger index
        rows = []
        for i in range(n - 1, -1, -1):
            al = [r.randint(0, 10**9) for _ in range(k - 1)]
            rq = [r.randint(0, 10**9) for _ in range(k - 1)]
            if i in stuck: al.append(0); rq.append(10**9)      # never satisfiable, holds none of the chain type
            else: al.append(1); rq.append(1 + later); later += 1
            rows.append(al + rq)
        for row in reversed(rows): print(*row)
```

## Hints
- A process whose whole request fits in the free pool can finish and release its allocation. Finishing never hurts anyone else, so the order of finishing doesn't matter.
- Processes left when no one else can finish are deadlocked. The challenge is finding the next finishable process fast.
- Per resource type, sort processes by their request and keep a pointer that advances as the free amount grows; count satisfied types per process.

## Solution
**From cycles to reduction.** With a single instance of every resource, a process waiting on a resource held by another gives a **wait-for graph**, and deadlock ⇔ a directed cycle, which a three-colour DFS finds. With several instances that's no longer true: `P` may wait for a printer held by `Q` while a second printer is about to be released by `R`, so a cycle can dissolve. The general test is **graph reduction**: any process whose outstanding request fits in the free pool can finish and return what it holds. Repeat until nothing changes; the processes left over are deadlocked.

**Order doesn't matter.** Finishing a process only *adds* to `work`, so a process that is satisfiable stays satisfiable. Any maximal sequence of reductions therefore finishes the same set, and the leftover set is well defined.

**Event-driven pointers.** For each type `j`, sort the processes by `req[i][j]`. Because `work[j]` never decreases, the processes whose type-`j` request fits always form a prefix of that sorted order, and the prefix only grows. Moving `ptr[j]` forward marks type `j` as satisfied for each newly covered process. A process with all `k` types satisfied goes on the ready stack. Each (process, type) pair is crossed exactly once.

**Cost.** Sorting is O(k·n log n); all pointer moves together are O(n·k); each finished process adds its `alloc` row in O(k). The textbook loop, in contrast, can need `n` full passes when completions come out in reverse index order: O(n²·k), about 10¹¹ here.

This is the detection half of the **Banker's algorithm**; the avoidance half runs the same safety check before granting a request.

Complexity: O(n·k·log n).

```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> deadlocked(int n, int k, vector<long long> avail,
                       const vector<vector<long long>>& alloc, const vector<vector<long long>>& req) {
    vector<long long>& work = avail;                 // free instances; only ever grows
    vector<vector<int>> order(k, vector<int>(n));    // per type: processes by increasing request
    for (int j = 0; j < k; ++j) {
        iota(order[j].begin(), order[j].end(), 0);
        sort(order[j].begin(), order[j].end(), [&](int a, int b) { return req[a][j] < req[b][j]; });
    }
    vector<int> ptr(k, 0), satisfied(n, 0), ready;
    auto advance = [&](int j) {                      // grant type j to everyone whose need now fits
        while (ptr[j] < n && req[order[j][ptr[j]]][j] <= work[j]) {
            int i = order[j][ptr[j]++];
            if (++satisfied[i] == k) ready.push_back(i);   // every type fits: i can finish
        }
    };
    for (int j = 0; j < k; ++j) advance(j);
    vector<char> done(n, 0);
    while (!ready.empty()) {
        int i = ready.back(); ready.pop_back();
        done[i] = 1;
        for (int j = 0; j < k; ++j)
            if (alloc[i][j] > 0) { work[j] += alloc[i][j]; advance(j); }   // i releases what it held
    }
    vector<int> res;
    for (int i = 0; i < n; ++i) if (!done[i]) res.push_back(i);
    return res;
}
```
