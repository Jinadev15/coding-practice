---
id: cpp-hp-ipo
title: IPO - Maximize Capital with Two Orders
difficulty: Hard
order: 8
tags: heap, greedy, sorting, two pointers
time_limit: 1
---
## Statement
```cpp
long long max_capital(int k, long long w, const std::vector<long long>& profit,
                      const std::vector<long long>& capital);
```

You start with capital `w` and may complete **at most `k`** distinct projects, one after another. Project `i` can be started only if your current capital is **≥ `capital[i]`**; completing it adds `profit[i]` (≥ 0) to your capital (the capital is not spent). Return the maximum final capital.

`k = 2, w = 0, profit = [1, 2, 3], capital = [0, 1, 1]` → **4** (do project 0 → capital 1, then project 2 → 4).

**Input:** cases until the end of input: `n k w`, then `n` lines `profit capital` (n ≤ 5·10⁵ in total, 1 ≤ k ≤ 10⁹, 0 ≤ w, profit, capital ≤ 10⁹).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

long long max_capital(int k, long long w, const vector<long long>& profit, const vector<long long>& capital) {
    int n = profit.size();
    vector<bool> used(n);
    for (int step = 0; step < k; ++step) {                     // O(k * n): rescans every project each step
        int best = -1;
        for (int i = 0; i < n; ++i)
            if (!used[i] && capital[i] <= w && (best < 0 || profit[i] > profit[best])) best = i;
        if (best < 0) break;
        used[best] = true; w += profit[best];
    }
    return w;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n, k; long long w;
    while (cin >> n >> k >> w) {
        vector<long long> p(n), c(n);
        for (int i = 0; i < n; ++i) cin >> p[i] >> c[i];
        cout << max_capital(k, w, p, c) << '\n';
    }
}
```

## Tests
=== sample
3 2 0
1 0
2 1
3 1
3 3 0
1 0
2 1
3 2
---
4
6
=== hidden
1 1 0
5 1
1 1000000000 7
0 7
4 10 2
1 0
1 3
10 4
100 15
3 1 5
4 5
9 6
2 0
---
0
7
14
9
=== hidden
1 1 1
4 4
6 4 3
4 1
0 8
0 0
1 5
1 0
4 6
4 4 1
4 4
0 8
3 1
4 7
5 2 0
1 5
3 6
0 0
2 1
0 5
3 2 0
1 5
2 5
1 6
3 2 3
4 8
3 6
4 4
5 2 2
1 2
4 3
1 6
0 5
0 4
4 2 3
3 6
4 3
4 6
2 5
---
1
13
12
0
0
3
7
11
=== hidden
6 4 2
1 1
0 6
3 5
0 8
0 3
4 3
1 2 0
1 5
6 5 1
3 8
4 4
4 3
1 6
0 2
3 0
3 4 3
4 5
0 5
2 1
2 2 2
1 3
2 8
4 5 3
4 4
3 0
0 2
3 5
6 5 2
1 8
2 3
0 5
3 8
0 1
3 4
3 1 0
2 4
2 2
3 0
---
10
0
16
9
2
13
2
3
=== hidden
2 1 3
0 8
4 0
2 3 3
0 0
1 2
5 4 3
1 6
1 6
2 5
4 5
2 8
2 2 3
3 2
4 0
4 1 0
4 0
4 1
4 8
0 3
1 2 0
4 6
2 2 0
1 1
1 7
4 4 0
3 5
3 7
0 8
4 7
---
7
4
3
10
4
0
0
0
=== hidden
@gen 3191568317 big
=== hidden
@gen 3191568318 big
=== hidden
@gen 3191568319 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(8 if not big else 1):
    n = r.randint(1, 6) if not big else 500000
    k = r.randint(1, n + 1) if not big else r.choice([200000, 10**9])
    w = r.randint(0, 3) if not big else 1000
    print(n, k, w)
    for _ in range(n):
        if big:   # capital requirements grow slowly, so almost every project is eventually unlocked
            print(r.randint(0, 10**9), r.choice([r.randint(0, 1000), r.randint(0, 10**9)]))
        else:
            print(r.randint(0, 4), r.randint(0, 8))
```

## Hints
- Among the projects you can afford now, which one should you do first? Why does doing it never hurt?
- A project becomes affordable once (capital only grows). Sort by required capital and unlock with a moving pointer.
- Keep unlocked profits in a max-heap; each step pop the top. Stop early when the heap is empty.

## Solution
**Greedy choice.** Among the projects you can afford now, take the most profitable one. Profits are non-negative, so it never hurts: it maximises the capital after this step, and more capital only unlocks more projects later. (Exchange argument: if an optimal plan does a smaller affordable project first, swapping in the bigger one gives at least as much capital at every later step.)

**Two orders.** Projects become affordable in order of **capital** (and stay affordable, since capital never decreases), but are chosen in order of **profit**. So:

- sort projects by required capital, and move a pointer forward as your capital grows, pushing newly affordable profits into a max-heap;
- each step, pop the max profit.

```text
w=0: unlock (capital 0) -> heap {1}       take 1, w=1
w=1: unlock capital-1 projects -> heap {2,3}   take 3, w=4    (k=2 done)
```

Each project is pushed once and popped at most once: O(n log n), independent of k. If the heap is empty, no affordable project remains and you stop early, which also handles k ≫ n.

The starter rescans all projects every step: O(k·n).

```cpp
#include <bits/stdc++.h>
using namespace std;

long long max_capital(int k, long long w, const vector<long long>& profit, const vector<long long>& capital) {
    int n = profit.size();
    vector<int> idx(n);
    iota(idx.begin(), idx.end(), 0);
    sort(idx.begin(), idx.end(), [&](int a, int b) { return capital[a] < capital[b]; });   // unlock order
    priority_queue<long long> affordable;                       // profits of unlocked, unused projects
    int next = 0;
    for (int step = 0; step < k; ++step) {
        while (next < n && capital[idx[next]] <= w) affordable.push(profit[idx[next++]]);   // newly unlocked
        if (affordable.empty()) break;                          // nothing can be started: stuck
        w += affordable.top();                                  // greedy: the most profitable one
        affordable.pop();
    }
    return w;
}
```
