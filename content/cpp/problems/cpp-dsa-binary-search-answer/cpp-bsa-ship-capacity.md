---
id: cpp-bsa-ship-capacity
title: Ship Packages Within D Days
difficulty: Medium
order: 8
tags: binary search on answer, greedy partition, minimise maximum
time_limit: 2
---
## Statement
Packages arrive in a fixed order with weights `w[i]`. Each day the ship carries a **contiguous** prefix of the remaining packages, with total weight at most the ship's capacity. What is the minimum capacity that ships everything within `D` days? And with that capacity, on which day does each package ship?

```cpp
long long min_capacity(const std::vector<long long>& w, int D);
std::vector<int> schedule(const std::vector<long long>& w, long long capacity);   // day index (0-based) per package, greedy
```

- **Range:** `[max(w), sum(w)]`. A smaller capacity can't carry the heaviest package, and `sum(w)` ships everything in one day.
- **Check:** load greedily, starting a new day when the next package doesn't fit. Count the days.

**Input:** cases until the end of input: `n D` + n weights (n ≤ 10⁶, w ≤ 10⁹). Print the capacity, then the number of days the greedy schedule uses, and a checksum of the schedule.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

long long min_capacity(const vector<long long>& w, int D) { return accumulate(w.begin(), w.end(), 0LL); }
vector<int> schedule(const vector<long long>& w, long long capacity) { return vector<int>(w.size(), 0); }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n, D;
    while (cin >> n >> D) {
        vector<long long> w(n);
        for (auto& x : w) cin >> x;
        long long c = min_capacity(w, D);
        auto s = schedule(w, c);
        unsigned long long h = 0;
        for (int d : s) h = h * 1000003 + (unsigned)d;
        cout << c << ' ' << (s.empty() ? 0 : s.back() + 1) << " days | " << h << '\n';
    }
}
```

## Tests
=== sample
10 5
1 2 3 4 5 6 7 8 9 10
6 3
3 2 2 4 1 4
5 4
1 2 3 1 1
---
15 5 days | 15003829205356896779
6 3 days | 1000010000035000044
3 3 days | 1000008000017
=== hidden
1 1
7
3 3
5 5 5
3 1
5 5 5
4 10
1 2 3 4
---
7 1 days | 0
5 3 days | 1000005
15 1 days | 0
4 3 days | 1000005
=== hidden
4 3
7 3 2 3
8 3
4 6 7 9 7 7 7 6
3 3
4 9 5
5 1
6 6 3 1 1
5 2
6 7 5 6 6
---
7 3 days | 1000007000014
20 3 days | 15003829205355896774
9 3 days | 1000005
17 1 days | 0
17 2 days | 1000007000013
=== hidden
6 2
8 6 8 9 8 8
4 2
3 4 9 9
8 3
1 8 1 5 7 1 8 4
8 2
5 7 6 7 6 7 1 2
5 5
4 1 6 6 1
---
25 2 days | 1000007000013
16 2 days | 1
13 3 days | 15003828205349896765
23 2 days | 15003828205348896761
6 4 days | 1000008000018
=== hidden
4 4
9 9 3 9
3 1
8 9 6
8 7
9 5 3 2 7 4 5 5
6 5
3 9 9 2 7 4
5 4
5 6 1 6 2
---
9 4 days | 1000008000018
23 1 days | 0
9 5 days | 44152901358998348
9 5 days | 16003839205389896815
7 4 days | 1000010000035000045
=== hidden
@gen 1395361251 big
=== hidden
@gen 1395361252 big
=== hidden
@gen 1395361253 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(5 if not big else 2):
    n = r.randint(1, 8) if not big else 1000000
    print(n, r.randint(1, n)); print(*[r.randint(1, 9) if not big else r.randint(1, 10**9) for _ in range(n)])
```

## Hints
- Guess a capacity C. Greedily fill each day in order. How many days do you need?
- More capacity never needs more days, so binary search C between max(w) and sum(w).
- The schedule for the final capacity is the same greedy pass, recording the day of each package.

## Solution
**This is the "minimise the maximum" family:** the capacity is the largest load allowed on any day.

- **The greedy check is optimal:** packing each day as full as possible never increases the number of days. Any valid schedule can be shifted toward the greedy one without using more days.
- **Monotone:** a larger capacity never needs more days.
- **Bounds:** the heaviest package must fit, so `lo = max(w)`. One day carrying everything gives `hi = sum(w)`.

The same template solves splitting an array into m parts, book allocation, and the painter's partition: only the story changes.

Complexity: O(n log(sum)).

```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> schedule(const vector<long long>& w, long long capacity) {
    vector<int> day(w.size());
    int d = 0; long long load = 0;
    for (size_t i = 0; i < w.size(); ++i) {
        if (load + w[i] > capacity) { ++d; load = 0; }      // doesn't fit: ship tomorrow
        load += w[i];
        day[i] = d;
    }
    return day;
}

static int days_needed(const vector<long long>& w, long long capacity) {
    int d = 1; long long load = 0;
    for (long long x : w) {
        if (load + x > capacity) { ++d; load = 0; }
        load += x;
    }
    return d;
}

long long min_capacity(const vector<long long>& w, int D) {
    long long lo = *max_element(w.begin(), w.end()), hi = accumulate(w.begin(), w.end(), 0LL);
    while (lo < hi) {
        long long mid = lo + (hi - lo) / 2;
        if (days_needed(w, mid) <= D) hi = mid; else lo = mid + 1;
    }
    return lo;
}
```
