---
id: cpp-bsa-bouquets
title: Minimum Days to Make Bouquets
difficulty: Medium
order: 2
tags: binary search on answer, greedy check, adjacency
time_limit: 2
---
## Statement
Flower `i` blooms on day `bloom[i]`. A bouquet needs `k` **adjacent** bloomed flowers, and each flower can be used once. What is the earliest day on which you can make `m` bouquets? Return −1 if it's impossible.

```cpp
long long min_days(const std::vector<long long>& bloom, int m, int k);
```

- **Impossible** when `m·k > n` (watch for overflow: compare in `long long`).
- **Check day `D`:** scan once, counting runs of consecutive flowers with `bloom ≤ D`. Every `k` in a row make one bouquet, and an unbloomed flower resets the run.
- **Monotone:** more days never un-bloom a flower.

The answer is always one of the `bloom` values. Binary search over `[min(bloom), max(bloom)]`.

**Input:** cases until the end of input: `n m k` + n days (n ≤ 10⁶, days ≤ 10⁹, m, k ≤ 10⁶).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

long long min_days(const vector<long long>& bloom, int m, int k) { return *max_element(bloom.begin(), bloom.end()); }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n, m, k;
    while (cin >> n >> m >> k) {
        vector<long long> b(n);
        for (auto& x : b) cin >> x;
        cout << min_days(b, m, k) << '\n';
    }
}
```

## Tests
=== sample
5 3 1
1 10 3 10 2
5 3 2
1 10 3 10 2
7 2 3
7 7 7 7 12 7 7
---
3
-1
12
=== hidden
1 1 1
5
3 1 3
1 2 3
3 2 2
1 1 1
2 1 1
1000000000 1
---
5
3
-1
1
=== hidden
4 2 3
9 7 5 2
6 4 2
5 4 5 3 3 8
4 2 2
2 3 10 7
3 4 1
9 2 6
5 4 2
5 4 1 2 6
---
-1
-1
10
-1
-1
=== hidden
8 4 3
6 8 4 6 4 7 9 5
7 4 3
2 1 3 9 2 7 6
7 4 1
5 3 6 3 1 8 4
6 4 1
10 5 9 10 3 9
1 3 3
8
---
-1
-1
4
9
-1
=== hidden
3 3 1
7 1 8
2 1 2
1 9
7 1 3
6 7 2 7 2 3 10
5 3 2
4 10 9 10 10
6 3 3
5 3 6 10 4 6
---
8
9
7
-1
-1
=== hidden
@gen 3455441326 big
=== hidden
@gen 3455441327 big
=== hidden
@gen 3455441328 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(5 if not big else 2):
    n = r.randint(1, 8) if not big else 1000000
    k = r.randint(1, 3) if not big else r.randint(1, 5); m = r.randint(1, 4) if not big else r.randint(1, n // max(k, 1) // 2 + 1)
    print(n, m, k); print(*[r.randint(1, 10) if not big else r.randint(1, 10**9) for _ in range(n)])
```

## Hints
- First check `m·k > n` (in 64-bit): then it's impossible.
- For a fixed day D, scan the flowers and count runs of bloomed ones. Each k in a row form a bouquet, and a gap resets the run.
- Binary search the smallest D for which the scan finds at least m bouquets.

## Solution
**Feasibility for a fixed day.** Taking bouquets greedily from left to right is optimal. Whenever `k` consecutive bloomed flowers appear, using them immediately can't block a better choice, because any bouquet that overlaps them could be shifted to them instead. So one pass counts the maximum number of bouquets.

**Monotone in the day:** the set of bloomed flowers only grows, so the count never decreases. Binary search the first feasible day. By the last day everything has bloomed, so if `m·k ≤ n` the maximum day is feasible.

Compute `m·k` in `long long`: both can be 10⁶, and the product overflows `int`.

Complexity: O(n log(max day)).

```cpp
#include <bits/stdc++.h>
using namespace std;

static bool can_make(const vector<long long>& bloom, int m, int k, long long day) {
    long long bouquets = 0, run = 0;
    for (long long b : bloom) {
        if (b <= day) {
            if (++run == k) { ++bouquets; run = 0; }   // k adjacent bloomed flowers -> one bouquet
        } else run = 0;                                 // a gap breaks adjacency
        if (bouquets >= m) return true;
    }
    return false;
}

long long min_days(const vector<long long>& bloom, int m, int k) {
    if ((long long)m * k > (long long)bloom.size()) return -1;
    long long lo = *min_element(bloom.begin(), bloom.end()), hi = *max_element(bloom.begin(), bloom.end());
    while (lo < hi) {
        long long mid = lo + (hi - lo) / 2;
        if (can_make(bloom, m, k, mid)) hi = mid; else lo = mid + 1;
    }
    return lo;
}
```
