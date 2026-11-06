---
id: cpp-hp-kway-merge
title: K-Way Merge and the Smallest Covering Range
difficulty: Medium
order: 4
tags: heap, k-way merge, sorted lists, sliding frontier
time_limit: 2
---
## Statement
```cpp
std::vector<long long> merge_k(const std::vector<std::vector<long long>>& lists);
    // all elements of the k sorted lists, in sorted order
std::pair<long long,long long> smallest_range(const std::vector<std::vector<long long>>& lists);
    // the range [lo, hi] with the smallest hi - lo that contains at least one element of EVERY list;
    // on ties, the smallest lo
```

Lists `[4 10 15 24 26]`, `[0 9 12 20]`, `[5 18 22 30]`: the smallest range is `[20, 24]`.

Each list is sorted in non-decreasing order and non-empty. Use a min-heap over the **current front** of each list: O(N log k) for N total elements.

**Input:** cases until the end of input: `k`, then `k` lines `m x1 … xm` (N ≤ 10⁶ in total, |x| ≤ 10¹⁸). Print the merged list on one line, then `lo hi`.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

vector<long long> merge_k(const vector<vector<long long>>& lists) {
    vector<long long> all;
    for (auto& l : lists) all.insert(all.end(), l.begin(), l.end());
    sort(all.begin(), all.end());
    return all;
}
pair<long long,long long> smallest_range(const vector<vector<long long>>& lists) {
    return {0, 0};
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int k;
    while (cin >> k) {
        vector<vector<long long>> L(k);
        for (auto& l : L) { int m; cin >> m; l.resize(m); for (auto& x : l) cin >> x; }
        auto m = merge_k(L);
        string out;
        for (size_t i = 0; i < m.size(); ++i) { if (i) out += ' '; out += to_string(m[i]); }
        auto [lo, hi] = smallest_range(L);
        out += "\n" + to_string(lo) + " " + to_string(hi) + "\n";
        cout << out;
    }
}
```

## Tests
=== sample
3
5 4 10 15 24 26
4 0 9 12 20
4 5 18 22 30
---
0 4 5 9 10 12 15 18 20 22 24 26 30
20 24
=== hidden
1
3 1 2 3
---
1 2 3
1 1
=== hidden
2
1 5
1 5
---
5 5
5 5
=== hidden
3
2 1 1
2 1 2
1 3
---
1 1 1 2 3
1 3
=== hidden
2
2 -1000000000000000000 1000000000000000000
1 0
---
-1000000000000000000 0 1000000000000000000
-1000000000000000000 0
=== hidden
3
3 -2 6 7
4 -8 1 3 4
3 -6 -3 5
2
1 -1
5 -7 -4 -3 -3 1
4
2 2 2
3 -8 -1 5
3 -3 2 5
2 -3 6
4
2 6 8
1 -4
3 -4 1 5
5 -7 -7 -5 -4 7
3
1 -8
1 -2
1 8
2
5 -5 -4 -2 2 5
4 -1 1 6 6
---
-8 -6 -3 -2 1 3 4 5 6 7
4 6
-7 -4 -3 -3 -1 1
-3 -1
-8 -3 -3 -1 2 2 2 5 5 6
2 6
-7 -7 -5 -4 -4 -4 1 5 6 7 8
-4 6
-8 -2 8
-8 8
-5 -4 -2 -1 1 2 5 6 6
-2 -1
=== hidden
1
5 -8 -7 -4 -2 2
4
4 -6 -2 3 3
5 -4 -4 -2 1 1
2 -3 6
3 -7 -5 -1
2
2 -7 -6
2 -8 3
1
1 5
4
3 -8 -8 -7
5 -7 -7 -6 0 6
1 -7
1 -2
2
3 -8 1 5
3 -6 0 8
---
-8 -7 -4 -2 2
-8 -8
-7 -6 -5 -4 -4 -3 -2 -2 -1 1 1 3 3 6
-3 -1
-8 -7 -6 3
-8 -7
5
5 5
-8 -8 -7 -7 -7 -7 -6 -2 0 6
-7 -2
-8 -6 0 1 5 8
0 1
=== hidden
3
2 -1 3
1 -5
4 -6 -1 1 4
1
5 -3 -2 0 4 7
1
3 -1 1 4
3
4 5 5 5 8
5 -5 -3 1 2 6
2 -6 0
1
3 -8 7 8
4
3 -5 -4 3
4 -8 -8 -7 7
5 -7 -7 -2 1 4
4 -8 -4 2 8
---
-6 -5 -1 -1 1 3 4
-5 -1
-3 -2 0 4 7
-3 -3
-1 1 4
-1 -1
-6 -5 -3 0 1 2 5 5 5 6 8
0 5
-8 7 8
-8 -8
-8 -8 -8 -7 -7 -7 -5 -4 -4 -2 1 2 3 4 7 8
-8 -5
=== hidden
@gen 2365146788 big
=== hidden
@gen 2365146789 big
=== hidden
@gen 2365146790 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 1):
    k = r.randint(1, 4) if not big else r.choice([3, 1000])
    print(k)
    total = 1000000 if big else 0
    for _ in range(k):
        m = r.randint(1, 5) if not big else total // k
        l = sorted(r.randint(-8, 8) if not big else r.randint(-10**18, 10**18) for _ in range(m))
        print(m, *l)
```

## Hints
- The next element of the merged output is the smallest of the k current list fronts. Keep those fronts in a min-heap.
- Store `(value, list, index)` in the heap so you know which list to advance after popping.
- For the range: the fronts always cover every list. Record `[min, max]`, then advance the list holding the min; stop when that list is exhausted.

## Solution
**K-way merge.** The smallest remaining element overall is the smallest of the k list **fronts**. Keep the fronts in a min-heap of `(value, list, index)`; pop the minimum, output it, and push the next element of the same list. The heap never holds more than k items, so each of the N steps costs O(log k): **O(N log k)**, better than sorting everything (O(N log N)) when k is small, and it works on streams that don't fit in memory (external sorting).

**Smallest covering range.** Keep one pointer per list. The k pointed-to values cover every list, and the range they span is `[min, max]`. To shrink it, the only useful move is to advance the list holding the **minimum** (advancing any other pointer can only raise the max). So: track `hi` = the max of the fronts, pop the min from the heap, record `[min, hi]`, then advance that list and update `hi`. Stop as soon as the list holding the minimum runs out.

```text
fronts 4 0 5 -> [0,5]  advance list 2: 9  -> fronts 4 9 5 [4,9]
advance list 1: 10 -> [5,10]   advance list 3: 18 -> [9,18]  ...
... [20,24] has width 4: the best
```

Ties: the comparison keeps the earlier `lo` only when a strictly better width or an equal width with smaller `lo` appears.

```cpp
#include <bits/stdc++.h>
using namespace std;

using Item = tuple<long long,int,int>;          // (value, list, position in list)

vector<long long> merge_k(const vector<vector<long long>>& lists) {
    priority_queue<Item, vector<Item>, greater<Item>> pq;
    size_t total = 0;
    for (int i = 0; i < (int)lists.size(); ++i) { pq.push({lists[i][0], i, 0}); total += lists[i].size(); }
    vector<long long> out;
    out.reserve(total);
    while (!pq.empty()) {
        auto [v, i, j] = pq.top(); pq.pop();
        out.push_back(v);
        if (j + 1 < (int)lists[i].size()) pq.push({lists[i][j + 1], i, j + 1});   // that list's next front
    }
    return out;
}

pair<long long,long long> smallest_range(const vector<vector<long long>>& lists) {
    priority_queue<Item, vector<Item>, greater<Item>> pq;
    long long hi = LLONG_MIN;
    for (int i = 0; i < (int)lists.size(); ++i) { pq.push({lists[i][0], i, 0}); hi = max(hi, lists[i][0]); }
    long long best_lo = get<0>(pq.top()), best_hi = hi;
    for (;;) {
        auto [v, i, j] = pq.top(); pq.pop();           // v = current minimum of the k fronts
        if (hi - v < best_hi - best_lo || (hi - v == best_hi - best_lo && v < best_lo)) { best_lo = v; best_hi = hi; }
        if (j + 1 == (int)lists[i].size()) break;      // list i is exhausted: no range can cover it any more
        long long nx = lists[i][j + 1];
        hi = max(hi, nx);
        pq.push({nx, i, j + 1});
    }
    return {best_lo, best_hi};
}
```
