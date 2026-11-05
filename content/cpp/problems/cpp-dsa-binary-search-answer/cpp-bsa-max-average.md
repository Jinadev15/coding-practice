---
id: cpp-bsa-max-average
title: Maximum Average Subarray of Length at Least k
difficulty: Hard
order: 6
tags: binary search on real numbers, prefix sums, transformation
time_limit: 2
compare: float
---
## Statement
```cpp
double max_average(const std::vector<int>& a, int k);   // the largest average of any contiguous subarray of length >= k
```

Checking all `O(n²)` subarrays is too slow for n = 10⁵. Binary search the **average** `m` over real numbers:

"Is there a subarray of length ≥ k with average ≥ m?" is the same as "is there a subarray of length ≥ k whose sum of `a[i] − m` is ≥ 0?"

Check that in O(n) with prefix sums `P`: for each end `j ≥ k`, you want `P[j] − min(P[0..j−k]) ≥ 0`. Keep a running minimum of the prefix sums, `k` positions behind.

Do 60 iterations on `[min(a), max(a)]`. Print with 6 decimals. Answers within 10⁻⁶ are accepted.

**Input:** cases until the end of input: `n k` + n values (n ≤ 10⁵, |a[i]| ≤ 10⁴).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

double max_average(const vector<int>& a, int k) {
    double best = -1e18;
    for (size_t i = 0; i + k <= a.size(); ++i) { double s = 0; for (int j = 0; j < k; ++j) s += a[i + j]; best = max(best, s / k); }
    return best;                                       // only length exactly k: longer can be better
}
```

## Driver
```cpp
int main() {
    int n, k;
    while (cin >> n >> k) {
        vector<int> a(n);
        for (auto& x : a) cin >> x;
        printf("%.6f\n", max_average(a, k));
    }
}
```

## Tests
=== sample
6 4
1 12 -5 -6 50 3
1 1
5
---
12.750000
5.000000
=== hidden
3 3
-1 -2 -3
5 2
-10000 10000 -10000 10000 -10000
4 1
7 7 7 7
---
-2.000000
3333.333333
7.000000
=== hidden
9 8
16 6 -17 -8 -11 -8 -17 20 -9
5 5
-9 9 17 11 -9
10 2
2 -19 -8 -4 -10 18 -19 -12 -9 15
8 1
1 -8 -8 -2 -17 -1 3 9
5 3
-5 -7 10 5 16
---
-2.375000
3.800000
4.000000
9.000000
10.333333
=== hidden
2 1
-15 14
2 1
-13 2
4 4
19 18 -15 4
2 1
1 10
2 2
8 10
---
14.000000
2.000000
6.500000
10.000000
9.000000
=== hidden
2 2
6 -11
4 4
8 0 -19 15
2 2
-4 11
7 3
1 -6 -15 7 5 17 18
7 2
19 -2 2 -11 20 18 14
---
-2.500000
1.000000
3.500000
13.333333
19.000000
=== hidden
@gen 1099120805 big
=== hidden
@gen 1099120806 big
=== hidden
@gen 1099120807 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(5 if not big else 2):
    n = r.randint(1, 10) if not big else 100000
    print(n, r.randint(1, n)); print(*[r.randint(-20, 20) if not big else r.randint(-10**4, 10**4) for _ in range(n)])
```

## Hints
- Average ≥ m is the same as Σ(a[i] − m) ≥ 0. The ratio becomes a sum.
- For a fixed m, use prefix sums of (a[i] − m). A valid subarray ending at j can start anywhere up to j − k, so keep the minimum prefix in that range.
- Binary search m over doubles for a fixed number of iterations (≈ 60), between min(a) and max(a).

## Solution
**Linearising the average.** "average ≥ m" means `Σ a / len ≥ m`, which is `Σ (a − m) ≥ 0`. Subtracting `m` from every element turns a ratio question into a sum question, which prefix sums answer.

**The check.** For a subarray ending at `j` with length ≥ k, its start `i` satisfies `i ≤ j − k`. The best start is the one with the **smallest** prefix `P[i]`, so keep a running minimum as `j` advances. That's O(n).

**Monotone:** if some subarray reaches average `m`, it reaches every smaller `m'` too. So the feasible values form `(−∞, best]`, and binary search on reals converges to `best`. Sixty halvings of a range of 2·10⁴ give an error far below 10⁻⁶.

(The answer is always between `min(a)` and `max(a)`, so those are safe bounds.)

Complexity: O(n · 60).

```cpp
#include <bits/stdc++.h>
using namespace std;

static bool reachable(const vector<int>& a, int k, double m) {
    // is there a subarray of length >= k with sum(a[i] - m) >= 0 ?
    vector<double> P(a.size() + 1, 0);                   // prefix sums of (a[i] - m)
    for (size_t i = 0; i < a.size(); ++i) P[i + 1] = P[i] + (a[i] - m);
    double minPrefix = 0;                                // min over P[0..j-k]
    for (size_t j = k; j <= a.size(); ++j) {
        minPrefix = min(minPrefix, P[j - k]);
        if (P[j] - minPrefix >= 0) return true;
    }
    return false;
}

double max_average(const vector<int>& a, int k) {
    double lo = *min_element(a.begin(), a.end()), hi = *max_element(a.begin(), a.end());
    for (int it = 0; it < 60; ++it) {                    // the range halves each time: 2e4 / 2^60 is tiny
        double mid = (lo + hi) / 2;
        if (reachable(a, k, mid)) lo = mid; else hi = mid;
    }
    return lo;
}
```
