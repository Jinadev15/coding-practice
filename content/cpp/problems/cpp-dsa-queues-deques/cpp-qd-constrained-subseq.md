---
id: cpp-qd-constrained-subseq
title: Constrained Subsequence Sum (DP + Monotonic Deque)
difficulty: Hard
order: 7
tags: deque, dynamic programming, sliding window maximum, optimization
time_limit: 1
---
## Statement
```cpp
long long constrained_sum(const std::vector<int>& a, int k);
```

Choose a **non-empty** subsequence of `a` such that any two consecutively chosen indices `i < j` satisfy `j − i ≤ k`. Return the maximum possible sum.

- `a = [10, 2, -10, 5, 20]`, `k = 2` → **37** (10, 2, 5, 20).
- `a = [-1, -2, -3]`, `k = 1` → **−1** (non-empty: take the single best element).
- `a = [10, -2, -10, -5, 20]`, `k = 2` → **23** (10, −2, −5, 20).

The DP is `dp[i] = a[i] + max(0, dp[i−k], …, dp[i−1])`, which is O(n·k) directly. Make it **O(n)**.

**Input:** cases until the end of input: `n k`, then `n` values (1 ≤ k ≤ n ≤ 10⁶ in total, |a[i]| ≤ 10⁴).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

long long constrained_sum(const vector<int>& a, int k) {
    int n = a.size();
    vector<long long> dp(n);
    long long best = LLONG_MIN;
    for (int i = 0; i < n; ++i) {                              // O(n*k)
        long long m = 0;
        for (int j = max(0, i - k); j < i; ++j) m = max(m, dp[j]);
        dp[i] = a[i] + m;
        best = max(best, dp[i]);
    }
    return best;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n, k;
    while (cin >> n >> k) {
        vector<int> a(n); for (auto& x : a) cin >> x;
        cout << constrained_sum(a, k) << '\n';
    }
}
```

## Tests
=== sample
5 2
10 2 -10 5 20
3 1
-1 -2 -3
5 2
10 -2 -10 -5 20
---
37
-1
23
=== hidden
1 1
-10000
4 1
5 -1 -1 5
4 3
5 -1 -1 5
6 1
3 -5 3 -5 3 -5
5 5
-3 -1 -4 -1 -5
---
-10000
8
10
3
-1
=== hidden
3 2
3 -7 1
9 4
-8 -2 -5 -2 -9 -4 -5 5 4
5 3
-9 5 -1 -3 -7
6 3
6 -9 5 1 4 4
9 3
-5 -9 -7 0 -1 -7 5 -1 3
2 1
0 -7
5 1
-6 -1 -7 -6 -8
10 3
-7 -8 3 -10 -8 -10 1 -5 -9 -4
---
4
9
5
20
8
0
-1
3
=== hidden
1 1
1
2 2
-6 5
11 8
5 1 0 2 5 2 -4 3 -1 0 6
11 10
-5 0 -7 0 -1 6 2 0 2 -7 4
4 3
1 -10 4 3
3 3
2 0 5
2 2
3 -2
5 2
-8 -6 4 -3 -8
---
1
5
24
14
8
7
3
4
=== hidden
5 5
-3 0 -9 -8 5
7 3
-5 -4 5 -1 -7 0 -4
12 5
4 -1 0 -9 -5 1 -9 6 -6 -10 0 2
1 1
-6
2 1
-5 -1
12 10
4 -9 -7 -2 -7 -1 -2 -2 -8 -2 -3 -8
12 12
4 -5 -6 0 1 -2 -1 -3 -2 4 5 5
9 7
-8 -8 4 -2 -3 4 -4 -9 -1
---
5
5
13
-6
-1
4
19
8
=== hidden
@gen 2577043233 big
=== hidden
@gen 2577043234 big
=== hidden
@gen 2577043235 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(8 if not big else 1):
    n = r.randint(1, 12) if not big else 1000000
    k = r.randint(1, n) if not big else r.choice([1000, 200000])
    a = [r.randint(-10, 6) if not big else r.randint(-10**4, 5000) for _ in range(n)]
    print(n, k); print(*a)
```

## Hints
- Define `dp[i]` = best sum of a valid subsequence ending exactly at `i`. Which earlier dp values can it extend?
- `dp[i] = a[i] + max(0, max of dp over the previous k indices)`. The max part is a sliding window maximum.
- Maintain a deque of indices with decreasing dp; drop the front when `front < i − k`.

## Solution
**The DP.** Let `dp[i]` be the best sum of a valid subsequence that **ends** at `i`. Its previous chosen index is one of `i−k … i−1`, or there is none (start fresh at `i`):

```text
dp[i] = a[i] + max(0, max(dp[i-k..i-1]))
answer = max over i of dp[i]
```

**The speed-up.** `max(dp[i-k..i-1])` is a **sliding window maximum** over the dp array, with the window moving right by one each step. So keep a monotonic deque of indices with decreasing dp values: expire the front when it is more than k behind, read the maximum at the front, and after computing `dp[i]` pop dominated values from the back.

```text
a = 10 2 -10 5 20, k = 2
i  window max  dp[i]          deque (dp values)
0  -          10              10
1  10         12              12
2  12         2               12 2
3  12         17              17
4  17         37              37      answer 37
```

The `max(0, …)` handles "start a new subsequence here". Because the subsequence must be non-empty, the answer for an all-negative array is its largest element, which falls out naturally (each dp[i] is at least a[i]).

Complexity: O(n) time, O(n) memory (O(k) is enough if you only keep the deque's dp values).

```cpp
#include <bits/stdc++.h>
using namespace std;

long long constrained_sum(const vector<int>& a, int k) {
    int n = a.size();
    vector<long long> dp(n);
    deque<int> dq;                          // indices of the last k dp values, dp decreasing front to back
    long long best = LLONG_MIN;
    for (int i = 0; i < n; ++i) {
        if (!dq.empty() && dq.front() < i - k) dq.pop_front();          // out of reach
        long long prev = dq.empty() ? 0 : max(0LL, dp[dq.front()]);    // best start-or-extend
        dp[i] = a[i] + prev;
        best = max(best, dp[i]);
        while (!dq.empty() && dp[dq.back()] <= dp[i]) dq.pop_back();
        dq.push_back(i);
    }
    return best;
}
```
