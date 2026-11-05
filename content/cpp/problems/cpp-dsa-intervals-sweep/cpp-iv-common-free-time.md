---
id: cpp-iv-common-free-time
title: Common Free Time
difficulty: Medium
order: 6
tags: intervals, merging, sweep line, k-way
time_limit: 2
---
## Statement
Each of `p` people has a list of busy intervals `[s, e)` (half-open, possibly overlapping within the same person). Find every **finite** stretch of time when **nobody** is busy, between the earliest busy start and the latest busy end.

```cpp
std::vector<std::pair<long long,long long>> free_time(const std::vector<std::vector<std::pair<long long,long long>>>& people);
    // sorted, positive-length gaps [a, b) with a < b
long long free_minutes_with_at_most(const std::vector<std::vector<std::pair<long long,long long>>>& people, int c);
    // total length of time (between the overall earliest start and latest end) during which
    // AT MOST c people are busy
```

- **Free time:** flatten all the intervals, merge them, and report the gaps between merged blocks.
- **At most c busy:** sweep `+1`/`−1` events (ends before starts at equal times), and add each segment's length whenever the count between events is `≤ c`.

**Input:** cases until the end of input: `p c`, then for each person `m` followed by m intervals (total intervals ≤ 10⁶).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;
using IV = vector<pair<long long,long long>>;

IV free_time(const vector<IV>& people) { return {}; }
long long free_minutes_with_at_most(const vector<IV>& people, int c) { return 0; }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int p, c;
    while (cin >> p >> c) {
        vector<IV> people(p);
        for (auto& v : people) { int m; cin >> m; v.resize(m); for (auto& [s, e] : v) cin >> s >> e; }
        auto f = free_time(people);
        long long h = 0;
        for (auto& [a, b] : f) h = (h * 1000003 + a % 998244353 + 3 * (b % 998244353)) % 998244353;
        cout << f.size() << ':';
        for (size_t i = 0; i < min<size_t>(f.size(), 6); ++i) cout << " [" << f[i].first << ',' << f[i].second << ')';
        cout << " | " << h << " | " << free_minutes_with_at_most(people, c) << '\n';
    }
}
```

## Tests
=== sample
3 1
2 1 3 6 7
1 2 4
2 2 5 9 12
2 0
2 1 3 6 7
1 2 4
---
2: [5,6) [7,9) | 23000103 | 9
1: [4,6) | 22 | 2
=== hidden
1 0
1 5 10
2 1
1 1 2
1 2 3
2 5
0
1 1 4
---
0: | 0 | 0
0: | 0 | 2
0: | 0 | 3
=== hidden
3 0
0
0
1 0 3
1 0
0
2 1
3 0 4 13 16 0 4
1 15 16
3 0
3 6 10 13 14 5 8
0
3 9 14 12 15 1 3
---
0: | 0 | 0
0: | 0 | 0
1: [4,13) | 43 | 11
1: [3,5) | 18 | 2
=== hidden
2 1
1 1 6
2 15 18 0 2
1 1
2 8 9 11 13
1 0
1 18 20
1 2
0
---
1: [6,15) | 51 | 17
1: [9,11) | 42 | 5
0: | 0 | 0
0: | 0 | 0
=== hidden
2 2
0
3 1 4 10 14 10 11
2 0
2 3 8 14 15
1 5 7
3 1
2 1 4 9 14
2 8 13 3 5
2 2 3 13 16
1 1
1 8 12
---
1: [4,10) | 34 | 13
1: [8,14) | 50 | 6
1: [5,8) | 29 | 8
0: | 0 | 4
=== hidden
@gen 1356419551 big
=== hidden
@gen 1356419552 big
=== hidden
@gen 1356419553 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(4 if not big else 1):
    p = r.randint(1, 3) if not big else 1000
    print(p, r.randint(0, 2) if not big else r.randint(0, 50))
    for _ in range(p):
        m = r.randint(0, 3) if not big else 1000
        iv = []
        for _ in range(m):
            s = r.randint(0, 20) if not big else r.randint(0, 10**9); iv.append((s, s + r.randint(1, 5 if not big else 10**5)))
        print(m, *[x for pr in iv for x in pr])
```

## Hints
- Free time doesn't care who is busy. Put every interval into one list.
- Sort by start, track the furthest end seen so far, and report a gap whenever the next start is beyond it.
- For "at most c busy", sweep `+1`/`−1` events and add the length of each segment between consecutive events whose count is `≤ c`.

## Solution
**Free time** is the complement of the union of all busy intervals. Who is busy doesn't matter, only whether *anyone* is. So flatten the lists, sort by start, and track how far the merged busy time reaches. An interval starting beyond the reach opens a gap `[reach, s)`. With half-open intervals, touching intervals leave no gap (`s == reach`).

**Counting coverage.** Between two consecutive event times the number of busy people is constant. So add the segment's length when that constant is `≤ c`. Ends sort before starts at equal times, which yields zero-length segments that contribute nothing. That matches the half-open semantics.

(With per-person lists already sorted, a k-way merge with a heap avoids the global sort. It's the same complexity class, and a classic follow-up question.)

Complexity: O(N log N) for N intervals in total.

```cpp
#include <bits/stdc++.h>
using namespace std;
using IV = vector<pair<long long,long long>>;

IV free_time(const vector<IV>& people) {
    IV all;
    for (auto& v : people) all.insert(all.end(), v.begin(), v.end());
    sort(all.begin(), all.end());
    IV gaps;
    long long reach = LLONG_MIN; bool started = false;
    for (auto& [s, e] : all) {
        if (started && s > reach) gaps.push_back({reach, s});   // nobody busy in [reach, s)
        reach = started ? max(reach, e) : e;
        started = true;
    }
    return gaps;
}

long long free_minutes_with_at_most(const vector<IV>& people, int c) {
    vector<pair<long long,int>> ev;
    for (auto& v : people) for (auto& [s, e] : v) { ev.push_back({s, +1}); ev.push_back({e, -1}); }
    if (ev.empty()) return 0;
    sort(ev.begin(), ev.end());
    long long total = 0; int cur = 0;
    for (size_t i = 0; i + 1 < ev.size(); ++i) {
        cur += ev[i].second;                                   // count on [ev[i].t, ev[i+1].t)
        if (cur <= c) total += ev[i + 1].first - ev[i].first;
    }
    return total;
}
```
