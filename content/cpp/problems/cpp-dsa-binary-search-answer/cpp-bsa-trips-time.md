---
id: cpp-bsa-trips-time
title: Minimum Time for Machines to Finish Jobs
difficulty: Medium
order: 3
tags: binary search on answer, counting, overflow
time_limit: 2
---
## Statement
Machine `i` completes one job every `t[i]` seconds, and all machines work in parallel from time 0. What is the minimum time `T` at which at least `jobs` jobs are done in total?

```cpp
long long min_time(const std::vector<long long>& t, long long jobs);
```

At time `T`, machine `i` has finished `⌊T / t[i]⌋` jobs, and this count only grows with `T`.

The upper bound needs care: the fastest machine alone finishes `jobs` jobs by `min(t) · jobs`, which can be 10⁹ × 10¹² = 10²¹, **beyond 64 bits**. Clamp it. With `jobs ≤ 10¹²` and `t ≤ 10⁶`, the answer fits in `long long`. Also stop summing once you reach `jobs`, so the counts can't overflow.

**Input:** cases until the end of input: `n jobs` + n times (n ≤ 10⁶, t ≤ 10⁶, jobs ≤ 10¹²).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

long long min_time(const vector<long long>& t, long long jobs) {
    for (long long T = 1; ; ++T) { long long done = 0; for (auto x : t) done += T / x; if (done >= jobs) return T; }
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n; long long jobs;
    while (cin >> n >> jobs) {
        vector<long long> t(n);
        for (auto& x : t) cin >> x;
        cout << min_time(t, jobs) << '\n';
    }
}
```

## Tests
=== sample
3 5
1 2 3
1 1
2
---
3
2
=== hidden
1 1000000000000
1000000
2 3
1000000 1
4 10
5 5 5 5
---
1000000000000000000
3
15
=== hidden
3 9
1 5 2
3 20
2 6 2
1 12
6
4 19
1 3 3 6
4 9
2 3 1 4
---
6
18
72
12
5
=== hidden
5 3
4 5 1 3 3
3 22
4 3 1
2 2
2 1
4 13
3 2 5 6
4 28
4 4 3 2
---
3
15
2
12
22
=== hidden
2 14
6 6
2 10
2 5
4 25
2 6 3 3
4 8
5 5 3 5
3 18
5 2 6
---
42
15
20
10
22
=== hidden
@gen 2876644494 big
=== hidden
@gen 2876644495 big
=== hidden
@gen 2876644496 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(5 if not big else 2):
    n = r.randint(1, 5) if not big else 1000000
    jobs = r.randint(1, 30) if not big else r.randint(1, 10**12)
    print(n, jobs); print(*[r.randint(1, 6) if not big else r.randint(1, 10**6) for _ in range(n)])
```

## Hints
- By time T, machine i has done ⌊T / t[i]⌋ jobs. The total only grows with T.
- An upper bound: the fastest machine alone, `min(t) · jobs`.
- In the check, stop as soon as the running total reaches `jobs`. That's faster and avoids overflow.

## Solution
**Counting at a fixed time.** At time `T`, machine `i` has finished `⌊T/t[i]⌋` jobs. Summing over all machines is O(n), and the total is non-decreasing in `T`, so "at least `jobs` done by `T`" is a monotone predicate.

**Bounds.** The fastest machine alone needs `min(t)·jobs` seconds, so that time is certainly enough. With the given limits it's at most 10¹⁸, which fits in a signed 64-bit integer. In general, clamp the upper bound (or use `__int128`).

**Overflow inside the check.** `T/x` can be 10¹⁸ for each of 10⁶ machines. Summing blindly would overflow, but returning as soon as `done ≥ jobs` keeps the sum below about 2·10¹⁸.

Complexity: O(n log(answer)), about 60 × n.

```cpp
#include <bits/stdc++.h>
using namespace std;

static bool enough(const vector<long long>& t, long long jobs, long long T) {
    long long done = 0;
    for (long long x : t) {
        done += T / x;
        if (done >= jobs) return true;       // early exit: no overflow, faster check
    }
    return false;
}

long long min_time(const vector<long long>& t, long long jobs) {
    long long lo = 1, hi = *min_element(t.begin(), t.end()) * jobs;   // <= 1e6 * 1e12 = 1e18: fits
    while (lo < hi) {
        long long mid = lo + (hi - lo) / 2;
        if (enough(t, jobs, mid)) hi = mid; else lo = mid + 1;
    }
    return lo;
}
```
