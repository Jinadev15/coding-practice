---
id: cpp-iv-insert-and-intersect
title: Insert an Interval and Intersect Two Lists
difficulty: Medium
order: 2
tags: intervals, two pointers, merging
time_limit: 2
---
## Statement
Closed intervals. Each input list is **sorted and disjoint**.

```cpp
using IV = std::vector<std::pair<long long,long long>>;
IV insert_interval(const IV& sorted, std::pair<long long,long long> x);
    // insert x and merge whatever it overlaps (touching counts as overlap); result sorted & disjoint
IV intersect(const IV& a, const IV& b);
    // all pairwise intersections, as a sorted list (single points like [5,5] count)
```

Both are **linear**, with no sorting needed:

- **Insert:** copy the intervals that end before `x` starts, absorb every interval that overlaps `x` into it, then copy the rest.
- **Intersect:** two pointers. The overlap of `a[i]` and `b[j]` is `[max(starts), min(ends)]` when that range is non-empty. Then advance whichever interval **ends first**, because it can't meet anything later.

**Input:** cases until the end of input: `ins n` + n intervals + the new interval, or `cut n m` + n intervals + m intervals (n, m ≤ 5·10⁵).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;
using IV = vector<pair<long long,long long>>;

IV insert_interval(const IV& sorted, pair<long long,long long> x) { IV r = sorted; r.push_back(x); sort(r.begin(), r.end()); return r; }
IV intersect(const IV& a, const IV& b) { return {}; }
```

## Driver
```cpp
static void show(const IV& v) {
    long long h = 0;
    for (auto& [s, e] : v) h = (h * 1000003 + (s % 998244353 + 998244353) + 7 * (e % 998244353 + 998244353)) % 998244353;
    cout << v.size() << ':';
    for (size_t i = 0; i < min<size_t>(v.size(), 6); ++i) cout << " [" << v[i].first << ',' << v[i].second << ']';
    cout << " | " << h << '\n';
}
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string cmd;
    while (cin >> cmd) {
        if (cmd == "ins") {
            int n; cin >> n; IV v(n); for (auto& [s, e] : v) cin >> s >> e;
            pair<long long,long long> x; cin >> x.first >> x.second;
            show(insert_interval(v, x));
        } else {
            int n, m; cin >> n >> m; IV a(n), b(m);
            for (auto& [s, e] : a) cin >> s >> e;
            for (auto& [s, e] : b) cin >> s >> e;
            show(intersect(a, b));
        }
    }
}
```

## Tests
=== sample
ins 2
1 3
6 9
2 5
ins 5
1 2
3 5
6 7
8 10
12 16
4 8
cut 4 4
0 2
5 10
13 23
24 25
1 5
8 12
15 24
25 26
---
2: [1,5] [6,9] | 36000177
3: [1,2] [3,10] [12,16] | 543352300
6: [1,2] [5,5] [8,10] [15,23] [24,24] [25,25] | 425620994
=== hidden
ins 0
4 8
ins 1
1 5
6 8
ins 2
1 2
7 8
3 4
cut 1 1
1 3
3 5
cut 1 1
1 2
3 4
---
1: [4,8] | 60
2: [1,5] [6,8] | 36000170
3: [1,2] [3,4] [7,8] | 501352113
1: [3,3] | 24
0: | 0
=== hidden
cut 2 3
2 2
5 8
-1 2
6 8
10 10
cut 2 4
-4 -2
0 1
-5 -2
-1 0
1 4
6 8
cut 4 5
-5 -5
-2 0
1 3
7 7
2 2
6 7
8 10
13 13
16 17
ins 0
9 16
ins 5
1 1
4 6
9 9
10 12
13 16
-1 4
cut 5 3
2 5
7 10
14 17
18 21
25 27
-2 -1
1 4
8 11
---
2: [2,2] [6,8] | 16000110
3: [-4,-2] [0,0] [1,1] | 234173142
2: [2,2] [7,7] | 16000104
1: [9,16] | 121
4: [-1,6] [9,9] [10,12] [13,16] | 647287462
2: [2,4] [8,10] | 30000168
=== hidden
cut 0 3
-3 0
2 2
4 7
cut 1 0
-9 -8
cut 1 3
-5 -4
-2 0
3 6
9 11
ins 0
11 15
cut 3 4
-8 -8
-5 -5
-1 0
0 2
6 6
9 10
13 13
cut 2 0
1 1
2 5
---
0: | 0
0: | 0
0: | 0
1: [11,15] | 116
1: [0,0] | 0
0: | 0
=== hidden
cut 5 0
-2 1
5 8
11 11
12 12
14 17
ins 5
-4 -3
-1 1
5 8
11 11
14 15
-6 -3
ins 2
-4 -1
3 3
12 12
cut 3 1
1 2
6 6
8 8
-5 -4
ins 0
-5 -2
ins 3
2 3
5 7
9 9
26 30
---
0: | 0
5: [-6,-3] [-1,1] [5,8] [11,11] [14,15] | 131762373
3: [-4,-1] [3,3] [12,12] | 610770129
0: | 0
1: [-5,-2] | 998244334
4: [2,3] [5,7] [9,9] [26,30] | 546187185
=== hidden
@gen 2326662703 big
=== hidden
@gen 2326662704 big
=== hidden
@gen 2326662705 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
def disjoint(n, step):
    out = []; x = r.randint(-10, 0) if not big else 0
    for _ in range(n):
        s = x + r.randint(0, step); e = s + r.randint(0, step); out.append((s, e)); x = e + 1
    return out
for _ in range(6 if not big else 2):
    n = r.randint(0, 5) if not big else 500000
    a = disjoint(n, 3 if not big else 1000)
    if r.random() < 0.5:
        s = r.randint(-12, 30) if not big else r.randint(0, 5 * 10**8); e = s + r.randint(0, 8 if not big else 10**8)
        print("ins", n)
        for p in a: print(*p)
        print(s, e)
    else:
        m = r.randint(0, 5) if not big else 500000
        b = disjoint(m, 3 if not big else 1000)
        print("cut", n, m)
        for p in a: print(*p)
        for p in b: print(*p)
```

## Hints
- Insert: copy everything that ends before `x` starts, merge everything that starts before `x` ends, then copy the rest.
- Intersect: the overlap of two intervals is `[max(start), min(end)]` when start ≤ end.
- Advance the pointer whose interval ends first, because it can't intersect anything further.

## Solution
**Insert in three phases.** Because the list is sorted and disjoint:

1. Every interval ending before `x.start` comes first, untouched.
2. Every interval starting at or before `x.end` (after phase 1) overlaps `x`, so grow `x` to cover it.
3. Everything left starts after `x`'s final end.

One pass, O(n), with no re-sorting.

**Intersect with two pointers.** Two intervals overlap exactly on `[max of starts, min of ends]` when that range is valid. The interval that ends first can't overlap anything after the other one's current interval (the lists are sorted and disjoint), so advance it.

Each step advances a pointer, so the total is O(n + m).

Complexity: O(n) and O(n + m).

```cpp
#include <bits/stdc++.h>
using namespace std;
using IV = vector<pair<long long,long long>>;

IV insert_interval(const IV& v, pair<long long,long long> x) {
    IV out;
    size_t i = 0;
    while (i < v.size() && v[i].second < x.first) out.push_back(v[i++]);         // entirely before x
    while (i < v.size() && v[i].first <= x.second) {                             // overlaps x: absorb
        x.first = min(x.first, v[i].first);
        x.second = max(x.second, v[i].second);
        ++i;
    }
    out.push_back(x);
    while (i < v.size()) out.push_back(v[i++]);                                  // entirely after x
    return out;
}

IV intersect(const IV& a, const IV& b) {
    IV out;
    size_t i = 0, j = 0;
    while (i < a.size() && j < b.size()) {
        long long lo = max(a[i].first, b[j].first), hi = min(a[i].second, b[j].second);
        if (lo <= hi) out.push_back({lo, hi});
        if (a[i].second < b[j].second) ++i; else ++j;                            // drop the one ending first
    }
    return out;
}
```
