---
id: cpp-bsa-eating-speed
title: Minimum Eating Speed
difficulty: Medium
order: 1
tags: binary search on answer, feasibility check, ceiling division
time_limit: 2
---
## Statement
There are `n` piles of bananas, and pile `i` holds `p[i]`. Each hour you choose one pile and eat up to `k` bananas from it. If the pile has fewer than `k`, you finish it, and that hour is over. What is the **minimum** integer speed `k` that lets you finish everything within `h` hours?

```cpp
long long min_speed(const std::vector<long long>& p, long long h);   // guaranteed h >= n
```

- **Answer range:** `k ∈ [1, max(p)]`. At speed `max(p)` every pile takes one hour.
- **Check:** the hours needed at speed `k` are `Σ ⌈p[i] / k⌉`. Feasibility is monotone: faster never takes longer.

Stop summing as soon as the total exceeds `h`, which also prevents overflow.

**Input:** cases until the end of input: `n h` + n piles (n ≤ 10⁶, p[i] ≤ 10⁹, h ≤ 10¹⁵).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

long long min_speed(const vector<long long>& p, long long h) {
    for (long long k = 1; ; ++k) {                    // try every speed: up to 10^9 tries
        long long hours = 0;
        for (long long x : p) hours += (x + k - 1) / k;
        if (hours <= h) return k;
    }
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n; long long h;
    while (cin >> n >> h) {
        vector<long long> p(n);
        for (auto& x : p) cin >> x;
        cout << min_speed(p, h) << '\n';
    }
}
```

## Tests
=== sample
4 8
3 6 7 11
5 5
30 11 23 4 20
5 6
30 11 23 4 20
---
4
30
23
=== hidden
1 1
1000000000
1 1000000000000000
1000000000
3 3
1 1 1
2 5
9 9
---
1000000000
1
1
5
=== hidden
6 56
10 15 7 24 19 1
6 41
28 39 23 31 33 18
3 36
26 22 28
1 4
24
5 38
27 39 20 27 26
---
2
5
3
6
4
=== hidden
6 10
37 5 35 19 19 39
4 23
21 26 5 11
2 5
35 34
6 24
33 29 7 7 2 7
2 35
19 22
---
19
3
17
4
2
=== hidden
3 14
10 26 8
2 34
2 24
4 41
26 24 22 15
2 35
29 36
4 45
12 12 19 11
---
4
1
3
2
2
=== hidden
@gen 215261609 big
=== hidden
@gen 215261610 big
=== hidden
@gen 215261611 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(5 if not big else 2):
    n = r.randint(1, 6) if not big else 1000000
    p = [r.randint(1, 40) if not big else r.randint(1, 10**9) for _ in range(n)]
    h = r.randint(n, n + 50) if not big else r.randint(n, 3 * n)
    print(n, h); print(*p)
```

## Hints
- Can you quickly check whether a given speed k is enough? How many hours does a pile of x bananas take?
- If speed k works, does k+1 work? Then binary search the smallest working k in [1, max pile].
- Use ceiling division `(x + k − 1) / k`, and stop summing once you pass h.

## Solution
**Reframe:** instead of computing the speed directly, ask "is speed `k` enough?". That check is a single O(n) pass: pile `x` needs `⌈x/k⌉` hours.

**Monotonicity:** if speed `k` finishes in time, any faster speed does too, because every term `⌈x/k⌉` can only shrink. So feasibility looks like false…false true…true over `k`, and the first true value is the answer.

**Range:** speed `max(p)` finishes each pile in one hour, which is `n ≤ h` hours, so it's feasible. Speed 1 is the smallest meaningful speed (and avoids dividing by zero).

The early exit keeps the check fast when `k` is too small, and stops the sum from growing huge.

Complexity: O(n log max(p)).

```cpp
#include <bits/stdc++.h>
using namespace std;

static bool feasible(const vector<long long>& p, long long h, long long k) {
    long long hours = 0;
    for (long long x : p) {
        hours += (x + k - 1) / k;                // ceil(x / k)
        if (hours > h) return false;             // early exit: also keeps the sum small
    }
    return true;
}

long long min_speed(const vector<long long>& p, long long h) {
    long long lo = 1, hi = *max_element(p.begin(), p.end());
    while (lo < hi) {                            // first feasible speed
        long long mid = lo + (hi - lo) / 2;
        if (feasible(p, h, mid)) hi = mid; else lo = mid + 1;
    }
    return lo;
}
```
