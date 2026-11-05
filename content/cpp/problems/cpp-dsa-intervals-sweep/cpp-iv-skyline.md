---
id: cpp-iv-skyline
title: The Skyline Problem
difficulty: Hard
order: 7
tags: sweep line, multiset, heaps, events
time_limit: 1
---
## Statement
Buildings are rectangles `[L, R)` with height `H > 0`, standing on the ground. The **skyline** is the outline seen from far away: a list of **key points** `(x, h)`, meaning that from `x` onward the outline's height is `h`, until the next key point. The last key point always has height 0.

```cpp
std::vector<std::pair<long long,long long>> skyline(const std::vector<std::array<long long,3>>& b);   // {L, R, H}
long long skyline_area(const std::vector<std::array<long long,3>>& b);   // area under the skyline
```

Consecutive key points must have **different** heights, and there must be no two key points at the same `x`.

**Sweep** the building edges left to right while keeping a **multiset of active heights**. At each x coordinate, apply every start and end at that x, then read the current maximum (0 if nothing is active). If it differs from the last key point's height, emit `(x, max)`.

**Input:** cases until the end of input: `n` + n buildings `L R H` (n ≤ 2·10⁵, 0 ≤ L < R ≤ 10⁹, H ≤ 10⁹).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

vector<pair<long long,long long>> skyline(const vector<array<long long,3>>& b) { return {}; }
long long skyline_area(const vector<array<long long,3>>& b) {
    long long a = 0; for (auto& x : b) a += (x[1] - x[0]) * x[2]; return a;    // counts overlaps twice
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n;
    while (cin >> n) {
        vector<array<long long,3>> b(n);
        for (auto& x : b) cin >> x[0] >> x[1] >> x[2];
        auto s = skyline(b);
        long long h = 0;
        for (auto& [x, y] : s) h = (h * 1000003 + x % 998244353 + 7 * (y % 998244353)) % 998244353;
        cout << s.size() << ':';
        for (size_t i = 0; i < min<size_t>(s.size(), 8); ++i) cout << " (" << s[i].first << ',' << s[i].second << ')';
        cout << " | " << h << " | area " << skyline_area(b) << '\n';
    }
}
```

## Tests
=== sample
5
2 9 10
3 7 15
5 12 12
15 20 10
19 24 8
2
0 2 3
2 5 3
---
7: (2,10) (3,15) (7,12) (12,0) (15,10) (20,8) (24,0) | 322499300 | area 212
2: (0,3) (5,0) | 21000068 | area 15
=== hidden
1
1 2 5
2
0 5 3
0 5 3
3
0 10 5
2 4 5
6 8 9
2
1 3 4
5 7 4
---
2: (1,5) (2,0) | 36000110 | area 5
2: (0,3) (5,0) | 21000068 | area 15
4: (0,5) (6,9) (8,5) (10,0) | 863639682 | area 58
4: (1,4) (3,0) (5,4) (7,0) | 942353753 | area 16
=== hidden
5
3 8 1
4 5 4
2 7 2
1 2 5
9 14 5
5
0 3 2
2 3 5
7 12 5
0 3 4
4 7 3
2
6 9 4
10 12 5
3
8 9 1
5 9 1
8 11 4
1
2 4 2
5
0 2 5
6 11 5
7 9 1
10 14 1
1 6 5
---
8: (1,5) (2,2) (4,4) (5,2) (7,1) (8,0) (9,5) (14,0) | 489680178 | area 43
6: (0,4) (2,5) (3,0) (4,3) (7,5) (12,0) | 578109203 | area 47
4: (6,4) (9,0) (10,5) (12,0) | 408736291 | area 22
3: (5,1) (8,4) (11,0) | 212632814 | area 15
2: (2,2) (4,0) | 16000052 | area 4
3: (0,5) (11,1) (14,0) | 782739850 | area 58
=== hidden
6
3 6 3
1 5 5
5 7 1
1 6 4
3 4 2
7 8 1
2
2 3 5
0 4 3
5
10 14 1
1 4 5
10 12 4
6 8 2
2 7 5
4
4 5 2
0 4 5
7 9 1
8 9 4
3
6 8 1
5 8 3
7 9 4
5
5 8 1
10 12 3
0 4 5
5 6 2
8 11 4
---
4: (1,5) (5,4) (6,1) (8,0) | 875725782 | area 26
4: (0,3) (2,5) (3,3) (4,0) | 351794045 | area 14
6: (1,5) (7,2) (8,0) (10,4) (12,1) (14,0) | 788150017 | area 42
6: (0,5) (4,2) (5,0) (7,1) (8,4) (9,0) | 481627946 | area 27
3: (5,3) (7,4) (9,0) | 916826463 | area 14
7: (0,5) (4,0) (5,2) (6,1) (8,4) (11,3) (12,0) | 397575984 | area 39
=== hidden
6
3 8 2
10 14 1
4 9 2
2 6 1
1 2 4
1 5 1
2
8 13 3
3 8 3
6
1 4 3
5 6 2
3 7 4
0 2 5
5 6 3
5 7 4
5
10 11 2
0 1 3
5 9 2
9 10 3
0 5 4
6
2 5 1
2 7 5
1 3 4
10 15 3
9 10 1
3 4 5
6
7 11 3
4 8 1
4 8 4
4 8 3
6 7 2
0 4 2
---
6: (1,4) (2,1) (3,2) (9,0) (10,1) (14,0) | 688173868 | area 21
2: (3,3) (13,0) | 24000085 | area 30
4: (0,5) (2,3) (3,4) (7,0) | 673669822 | area 29
5: (0,4) (5,2) (9,3) (10,2) (11,0) | 859844070 | area 33
6: (1,4) (2,5) (7,0) (9,1) (10,3) (15,0) | 334276426 | area 45
4: (0,2) (4,4) (8,3) (11,0) | 521845672 | area 33
=== hidden
@gen 1444748339 big
=== hidden
@gen 1444748340 big
=== hidden
@gen 1444748341 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 1):
    n = r.randint(1, 6) if not big else 200000
    print(n)
    for _ in range(n):
        L = r.randint(0, 10) if not big else r.randint(0, 10**9 - 10**6); R = L + r.randint(1, 5) if not big else L + r.randint(1, 10**6)
        print(L, R, r.randint(1, 5) if not big else r.randint(1, 10**4))
```

## Hints
- The height can only change at a building's left or right edge. Turn the edges into events and sort them by x.
- Keep the active heights in a `multiset` (with a 0 for the ground). The current height is the largest element.
- Process every event at the same x before checking the height, and erase only one copy of a height when a building ends.

## Solution
**Events and the active set.** The outline's height at any x is the maximum height among the buildings covering x. It can only change at a building edge. Sweep the edges in order, keep the active heights in a `multiset` (O(log n) insert and erase, and the maximum is `rbegin`), and emit a key point when the maximum changes.

**Correctness details:**

- **Group all events at the same x** before reading the maximum. Otherwise an end followed by a start at the same x would emit a spurious dip.
- **Erase one copy** with `erase(find(h))`. `erase(h)` would remove *every* building of that height.
- **Seed the set with 0**, the ground, so the maximum is defined when no building is active.
- **Only emit on a change,** so consecutive key points have different heights.

**Area.** Between consecutive key points the height is constant, so sum `width × height`. Use `__int128` for the intermediate sum, since 10⁹ × 10⁹ is close to the 64-bit limit. The tests keep the final answer within `long long`.

Complexity: O(n log n).

```cpp
#include <bits/stdc++.h>
using namespace std;

vector<pair<long long,long long>> skyline(const vector<array<long long,3>>& b) {
    vector<pair<long long,long long>> ev;                 // (x, +H for start / -H for end)
    for (auto& x : b) { ev.push_back({x[0], x[2]}); ev.push_back({x[1], -x[2]}); }
    sort(ev.begin(), ev.end());
    multiset<long long> active{0};                        // ground level is always "active"
    vector<pair<long long,long long>> out;
    for (size_t i = 0; i < ev.size(); ) {
        long long x = ev[i].first;
        for (; i < ev.size() && ev[i].first == x; ++i) {  // apply ALL events at this x first
            if (ev[i].second > 0) active.insert(ev[i].second);
            else active.erase(active.find(-ev[i].second));   // erase ONE copy, not all equal heights
        }
        long long h = *active.rbegin();
        if (out.empty() || out.back().second != h) out.push_back({x, h});
    }
    return out;
}

long long skyline_area(const vector<array<long long,3>>& b) {
    auto s = skyline(b);
    __int128 area = 0;
    for (size_t i = 0; i + 1 < s.size(); ++i) area += (__int128)(s[i + 1].first - s[i].first) * s[i].second;
    return (long long)area;
}
```
