---
id: cpp-kd-stock-profits
title: Stock Profits with Running Minimums
difficulty: Medium
order: 8
tags: running minimum, greedy, Kadane, arrays
time_limit: 2
---
## Statement
`p[i]` is a stock's price on day `i`.

```cpp
long long one_transaction(const std::vector<int>& p);      // buy once, then sell on a later day (0 if no profit)
long long unlimited(const std::vector<int>& p);            // any number of buy/sell pairs, holding at most one share
long long best_two_disjoint(const std::vector<int>& p);    // at most TWO transactions that don't overlap in time
```

- **One transaction:** for each sell day, the best buy day is the cheapest day so far (a running minimum).
- **Unlimited:** every rising step `p[i] − p[i−1] > 0` can be collected. A long climb equals the sum of its steps.
- **Two transactions:** split the timeline. Let `left[i]` be the best single transaction within days `0..i`, and `right[i]` the best within days `i..n−1`. The answer is `max over i of left[i] + right[i]`. (A transaction may sell and the next buy on the same day, which is equivalent to not trading that day.)

**Input:** cases until the end of input: `n` + prices (n ≤ 10⁶, 0 ≤ p ≤ 10⁹).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

long long one_transaction(const vector<int>& p) {
    long long b = 0;
    for (size_t i = 0; i < p.size(); ++i) for (size_t j = i + 1; j < p.size(); ++j) b = max(b, (long long)p[j] - p[i]);
    return b;
}
long long unlimited(const vector<int>& p) { return 0; }
long long best_two_disjoint(const vector<int>& p) { return 0; }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n;
    while (cin >> n) {
        vector<int> p(n);
        for (auto& x : p) cin >> x;
        cout << one_transaction(p) << ' ' << unlimited(p) << ' ' << best_two_disjoint(p) << '\n';
    }
}
```

## Tests
=== sample
6
7 1 5 3 6 4
5
1 2 3 4 5
8
3 3 5 0 0 3 1 4
---
5 7 7
4 4 4
4 8 6
=== hidden
1
5
2
5 1
5
7 6 4 3 1
6
1 4 2 7 1 9
---
0 0 0
0 0 0
0 0 0
8 16 14
=== hidden
9
0 3 8 0 5 8 9 4 6
4
3 1 7 5
2
9 3
6
6 7 9 5 3 0
7
6 2 8 9 3 1 8
6
1 8 3 3 4 5
---
9 19 17
6 6 6
0 0 0
3 3 3
7 14 14
7 9 9
=== hidden
5
9 3 3 8 3
3
1 0 2
3
5 5 9
7
4 9 3 1 2 8 7
1
4
8
4 6 6 6 3 2 2 3
---
5 5 5
2 2 2
4 4 4
7 12 12
0 0 0
2 3 3
=== hidden
3
8 7 3
5
3 4 6 6 4
6
4 3 0 2 5 2
8
2 6 6 2 3 1 0 9
7
8 6 6 8 2 8 2
1
4
---
0 0 0
3 3 3
5 5 5
9 14 13
6 8 8
0 0 0
=== hidden
@gen 2987758320 big
=== hidden
@gen 2987758321 big
=== hidden
@gen 2987758322 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 1):
    n = r.randint(1, 9) if not big else 1000000
    print(n); print(*[r.randint(0, 9) if not big else r.randint(0, 10**9) for _ in range(n)])
```

## Hints
- One transaction: keep the minimum price seen so far, and the best `price − minimum`.
- Unlimited: add up every positive difference between consecutive days.
- Two transactions: compute the best single trade ending by day i (left to right) and starting from day i (right to left), then maximise their sum over i.

## Solution
**Running minimum.** The best profit when selling on day `i` is `p[i] − min(p[0..i])`. Tracking the minimum as you go makes it O(n) instead of trying every pair.

**Unlimited trades.** Any profitable trade from day `a` to day `b` equals the sum of the daily changes in between. Taking exactly the positive daily changes is optimal: it collects every rise and avoids every fall.

**Two transactions.** Their time intervals don't overlap, so there's a split day `i` with the first trade inside `[0, i]` and the second inside `[i, n−1]`. Precompute the best single trade on each prefix (forward pass with a running min) and each suffix (backward pass with a running max), then try every split.

This "best on the left + best on the right" decomposition is a reusable pattern. It is also the first step toward the general "at most k transactions" DP.

Complexity: O(n) time, O(n) space for the two-transaction version.

```cpp
#include <bits/stdc++.h>
using namespace std;

long long one_transaction(const vector<int>& p) {
    long long lowest = LLONG_MAX, best = 0;
    for (int x : p) { lowest = min(lowest, (long long)x); best = max(best, x - lowest); }
    return best;
}

long long unlimited(const vector<int>& p) {
    long long s = 0;
    for (size_t i = 1; i < p.size(); ++i) s += max(0, p[i] - p[i - 1]);
    return s;
}

long long best_two_disjoint(const vector<int>& p) {
    int n = p.size();
    if (n < 2) return 0;
    vector<long long> left(n), right(n);
    long long lowest = p[0];
    left[0] = 0;
    for (int i = 1; i < n; ++i) {                       // best sell-by-day-i profit
        lowest = min(lowest, (long long)p[i]);
        left[i] = max(left[i - 1], p[i] - lowest);
    }
    long long highest = p[n - 1];
    right[n - 1] = 0;
    for (int i = n - 2; i >= 0; --i) {                  // best buy-from-day-i profit
        highest = max(highest, (long long)p[i]);
        right[i] = max(right[i + 1], highest - p[i]);
    }
    long long best = 0;
    for (int i = 0; i < n; ++i) best = max(best, left[i] + right[i]);
    return best;
}
```
