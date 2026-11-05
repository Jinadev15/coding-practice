---
id: cpp-iv-merge
title: Merge Intervals and Covered Length
difficulty: Easy
order: 1
tags: intervals, sorting, merging
time_limit: 2
---
## Statement
Intervals are **closed** `[s, e]` with `s ≤ e`. Intervals that merely touch (`[1,3]` and `[3,5]`) overlap.

```cpp
std::vector<std::pair<long long,long long>> merge_all(std::vector<std::pair<long long,long long>> v);
    // the union as disjoint intervals, sorted by start
long long covered_points(std::vector<std::pair<long long,long long>> v);
    // how many integer points lie in at least one interval
```

Sort by start. Extend the last merged interval while the next one starts at or before its end. Remember that a later interval may be **nested** inside the current one, so use `max` for the end.

**Input:** cases until the end of input: `n` + n lines `s e` (n ≤ 10⁶, |s|, |e| ≤ 10¹⁸, and every interval length is below 10¹⁸). Print the number of merged intervals, the first 5 of them, and the covered count.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

vector<pair<long long,long long>> merge_all(vector<pair<long long,long long>> v) { return v; }
long long covered_points(vector<pair<long long,long long>> v) {
    long long c = 0; for (auto& [s, e] : v) c += e - s + 1; return c;    // double-counts overlaps
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n;
    while (cin >> n) {
        vector<pair<long long,long long>> v(n);
        for (auto& [s, e] : v) cin >> s >> e;
        auto m = merge_all(v);
        cout << m.size() << ':';
        for (size_t i = 0; i < min<size_t>(m.size(), 5); ++i) cout << " [" << m[i].first << ',' << m[i].second << ']';
        cout << " covered " << covered_points(v) << '\n';
    }
}
```

## Tests
=== sample
4
1 3
8 10
2 6
15 18
3
1 4
4 5
2 3
---
3: [1,6] [8,10] [15,18] covered 13
1: [1,5] covered 5
=== hidden
1
5 5
2
1 10
2 3
3
-5 -1
0 0
1 2
---
1: [5,5] covered 1
1: [1,10] covered 10
3: [-5,-1] [0,0] [1,2] covered 8
=== hidden
6
-2 2
-3 -3
-3 -3
6 6
1 3
-3 -1
3
1 1
3 6
-5 -5
1
-2 1
2
5 7
6 6
6
3 4
-3 1
-2 2
0 2
-3 -2
1 5
2
-1 1
3 5
---
2: [-3,3] [6,6] covered 8
3: [-5,-5] [1,1] [3,6] covered 6
1: [-2,1] covered 4
1: [5,7] covered 3
1: [-3,5] covered 9
2: [-1,1] [3,5] covered 6
=== hidden
1
1 2
2
-3 -2
-5 -2
2
2 5
4 4
4
0 1
6 7
8 8
6 9
6
7 7
2 4
7 8
8 8
-3 1
-5 -1
5
0 1
1 2
6 6
-4 -1
8 10
---
1: [1,2] covered 2
1: [-5,-2] covered 4
1: [2,5] covered 4
2: [0,1] [6,9] covered 6
3: [-5,1] [2,4] [7,8] covered 12
4: [-4,-1] [0,2] [6,6] [8,10] covered 11
=== hidden
6
3 5
4 5
0 0
-2 0
6 6
-4 -2
3
6 7
-4 0
-4 0
6
2 5
8 9
2 5
5 9
-2 2
2 3
3
4 8
2 4
1 2
2
-1 2
6 7
2
7 11
5 5
---
3: [-4,0] [3,5] [6,6] covered 9
2: [-4,0] [6,7] covered 7
1: [-2,9] covered 12
1: [1,8] covered 8
2: [-1,2] [6,7] covered 6
2: [5,5] [7,11] covered 6
=== hidden
@gen 1735366108 big
=== hidden
@gen 1735366109 big
=== hidden
@gen 1735366110 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 1):
    n = r.randint(1, 7) if not big else 1000000
    print(n)
    for _ in range(n):
        if big: s = r.randint(-10**17, 10**17); e = s + r.randint(0, 10**11)
        else: s = r.randint(-5, 8); e = s + r.randint(0, 4)
        print(s, e)
```

## Hints
- Sort by start. Can an interval overlap anything except the last merged block?
- Overlap (closed intervals) means `cur.start <= last.end`. Extend with `max`, because `cur` might be nested inside.
- Count the covered points from the merged, disjoint intervals: `e − s + 1` each.

## Solution
After sorting by start, an interval can only overlap the **most recent** merged block. All earlier blocks end before that block starts. So a single pass suffices:

- an overlapping interval extends the block to `max(end, cur.end)`. Without the `max`, a nested interval like `[2,3]` inside `[1,10]` would shrink the block;
- a non-overlapping one starts a new block.

**Covered points** can't be summed per interval, because overlaps would be counted twice. Merge first, and then the blocks are disjoint.

The total can approach 10¹⁸ (within `long long`'s 9.2·10¹⁸) because every interval length is below 10¹⁸ and the blocks are disjoint. In general, sums of lengths need care with overflow.

Complexity: O(n log n) time, O(n) space.

```cpp
#include <bits/stdc++.h>
using namespace std;

vector<pair<long long,long long>> merge_all(vector<pair<long long,long long>> v) {
    sort(v.begin(), v.end());                                // by start (then end)
    vector<pair<long long,long long>> out;
    for (auto& cur : v) {
        if (!out.empty() && cur.first <= out.back().second)  // overlaps or touches (closed)
            out.back().second = max(out.back().second, cur.second);   // nested intervals keep the old end
        else out.push_back(cur);
    }
    return out;
}

long long covered_points(vector<pair<long long,long long>> v) {
    long long c = 0;
    for (auto& [s, e] : merge_all(std::move(v))) c += e - s + 1;      // disjoint now: no double counting
    return c;
}
```
