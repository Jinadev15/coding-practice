---
id: cpp-iv-activity-selection
title: Non-Overlapping Intervals and Minimum Arrows
difficulty: Medium
order: 3
tags: intervals, greedy, sorting by end, exchange argument
time_limit: 2
---
## Statement
```cpp
int min_removals(std::vector<std::pair<long long,long long>> v);
    // HALF-OPEN [s, e): fewest intervals to delete so that the rest don't overlap ([1,2) and [2,3) are fine)
int min_arrows(std::vector<std::pair<long long,long long>> v);
    // CLOSED [s, e] balloons on a line: fewest points x such that every interval contains some chosen x
```

Both use the same greedy: **sort by end**, then scan.

- **Removals:** keep an interval if it starts at or after the end of the last kept one. Then `removals = n − kept`.
- **Arrows:** shoot at the end of the first balloon not yet hit. Every balloon that starts at or before that point is burst too.

Sorting by start, or by length, is wrong. Find a counterexample for each!

**Input:** cases until the end of input: `rem n` or `arrow n`, followed by n intervals (n ≤ 10⁶).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

int min_removals(vector<pair<long long,long long>> v) {
    sort(v.begin(), v.end());                                  // by START: wrong greedy
    int kept = 0; long long last = LLONG_MIN;
    for (auto& [s, e] : v) if (s >= last) { ++kept; last = e; }
    return (int)v.size() - kept;
}
int min_arrows(vector<pair<long long,long long>> v) { return (int)v.size(); }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string cmd; int n;
    while (cin >> cmd >> n) {
        vector<pair<long long,long long>> v(n);
        for (auto& [s, e] : v) cin >> s >> e;
        cout << (cmd == "rem" ? min_removals(v) : min_arrows(v)) << '\n';
    }
}
```

## Tests
=== sample
rem 4
1 2
2 3
3 4
1 3
arrow 4
10 16
2 8
1 6
7 12
---
1
2
=== hidden
rem 1
1 2
rem 3
1 2
1 2
1 2
arrow 2
1 2
2 3
arrow 2
1 2
3 4
rem 3
1 10
2 3
4 5
---
0
2
1
2
1
=== hidden
rem 1
4 5
rem 5
3 4
1 2
2 3
1 5
7 9
arrow 1
6 10
arrow 7
8 12
8 9
3 4
1 4
5 9
3 4
5 7
arrow 7
4 8
6 9
5 8
1 3
3 6
2 6
4 7
rem 2
8 12
2 5
---
0
1
1
3
2
0
=== hidden
rem 7
2 3
5 7
0 4
7 11
8 9
5 7
4 8
arrow 4
8 12
6 8
7 11
0 4
rem 7
7 8
6 7
5 9
2 4
3 5
5 7
1 4
rem 1
7 11
arrow 4
2 6
2 5
0 2
2 5
rem 1
3 6
---
4
2
4
0
1
0
=== hidden
arrow 2
4 7
7 10
rem 1
8 11
rem 6
3 6
7 11
3 7
5 7
5 6
2 6
rem 5
1 4
3 5
4 8
1 4
3 6
arrow 5
0 2
7 9
0 2
8 12
5 6
rem 5
5 8
0 3
6 8
0 4
4 8
---
1
0
4
3
3
3
=== hidden
@gen 1833583544 big
=== hidden
@gen 1833583545 big
=== hidden
@gen 1833583546 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 2):
    n = r.randint(1, 7) if not big else 1000000
    print(r.choice(["rem", "arrow"]), n)
    for _ in range(n):
        s = r.randint(0, 8) if not big else r.randint(0, 10**12); e = s + r.randint(1, 4) if not big else s + r.randint(1, 10**6)
        print(s, e)
```

## Hints
- Sort by end time. The interval that finishes first leaves the most room for the others.
- Removals: count how many you can keep (each must start at or after the last kept end), then subtract from n.
- Arrows: shoot at the end of the first unburst balloon. Balloons starting at or before that point burst too (closed intervals).

## Solution
**The exchange argument.** Among all intervals, the one that **ends first** is always safe to choose. Take any optimal selection and replace its earliest-ending interval with the globally earliest-ending one. That can't create an overlap, because it ends even sooner. Then repeat the argument on what's left. So greedy-by-end keeps the maximum possible number, and the removals are the rest.

**Arrows** is the dual problem. The first balloon to end must be hit by some arrow at or before its end, and shooting exactly at its end hits every other balloon that has already started, which is the most possible. The only difference between the two problems is the boundary test: `s >= last_end` (half-open, touching is OK to keep) versus `s > shot` (closed, touching is already burst).

Counterexamples: by start, `[1,10) [2,3) [4,5)` keeps 1 instead of 2. By length, `[1,5) [4,7) [6,10)` keeps the short middle interval, which blocks both others.

Complexity: O(n log n).

```cpp
#include <bits/stdc++.h>
using namespace std;

static void by_end(vector<pair<long long,long long>>& v) {
    sort(v.begin(), v.end(), [](auto& a, auto& b) { return a.second < b.second; });
}

int min_removals(vector<pair<long long,long long>> v) {
    by_end(v);
    int kept = 0; long long last_end = LLONG_MIN;
    for (auto& [s, e] : v)
        if (s >= last_end) { ++kept; last_end = e; }          // half-open: touching is allowed
    return (int)v.size() - kept;
}

int min_arrows(vector<pair<long long,long long>> v) {
    by_end(v);
    int arrows = 0; long long shot = LLONG_MIN; bool any = false;
    for (auto& [s, e] : v)
        if (!any || s > shot) { ++arrows; shot = e; any = true; }   // closed: s == shot is already hit
    return arrows;
}
```
