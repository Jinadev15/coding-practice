---
id: cpp-iv-smallest-covering
title: Smallest Interval Covering Each Query
difficulty: Hard
order: 8
tags: offline queries, sweep line, priority queue, sorting
time_limit: 1
---
## Statement
You get closed intervals `[l, r]` and query points `q`. For each query, report the **length** (`r − l + 1`) of the shortest interval that contains it, or −1 if none does.

```cpp
std::vector<long long> smallest_covering(std::vector<std::pair<long long,long long>> iv, const std::vector<long long>& queries);
```

Answering each query by scanning every interval is O(n·q), up to 4·10¹⁰ steps. Answer them **offline** instead:

1. Sort the intervals by left end, and process the queries in increasing order (remember each query's original index).
2. For the current query `q`, push every interval with `l ≤ q` into a min-heap keyed by `(length, r)`.
3. Pop heap tops whose `r < q`. They ended before `q`, and since the queries only increase, they can never cover a later query either.
4. The heap's top is now the answer.

**Input:** cases until the end of input: `n m`, n intervals, then m queries (n, m ≤ 2·10⁵, coordinates ≤ 10⁹).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

vector<long long> smallest_covering(vector<pair<long long,long long>> iv, const vector<long long>& q) {
    vector<long long> ans;
    for (long long x : q) {
        long long best = -1;
        for (auto& [l, r] : iv) if (l <= x && x <= r && (best < 0 || r - l + 1 < best)) best = r - l + 1;
        ans.push_back(best);
    }
    return ans;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n, m;
    while (cin >> n >> m) {
        vector<pair<long long,long long>> iv(n);
        for (auto& [l, r] : iv) cin >> l >> r;
        vector<long long> q(m);
        for (auto& x : q) cin >> x;
        auto a = smallest_covering(iv, q);
        long long h = 0;
        for (auto x : a) h = (h * 1000003 + x + 2) % 998244353;
        for (int i = 0; i < min(m, 12); ++i) cout << a[i] << ' ';
        cout << "| " << h << '\n';
    }
}
```

## Tests
=== sample
4 4
1 4
2 4
3 6
4 4
2 3 4 5
4 4
2 3
2 5
1 8
20 25
2 19 5 22
---
3 3 1 4 | 690468562
2 -1 4 6 | 62606731
=== hidden
1 2
5 5
5 6
2 3
1 10
1 10
0 1 10
---
1 -1 | 3000010
-1 10 10 | 775402704
=== hidden
3 6
3 4
14 17
1 5
17 20 8 18 10 12
4 3
7 9
6 10
4 10
12 15
2 19 5
1 3
2 6
18 17 0
6 4
9 9
5 6
11 14
7 7
15 15
3 3
1 19 13 8
5 1
10 16
13 14
6 7
3 3
2 4
13
---
4 -1 -1 -1 -1 -1 | 447552355
-1 -1 7 | 764402668
-1 -1 -1 | 764402660
-1 -1 4 -1 | 343142599
2 | 4
=== hidden
5 3
15 21
10 10
13 14
2 3
5 9
2 17 11
3 1
2 2
15 19
15 17
13
4 2
2 2
7 10
14 15
7 12
13 14
5 6
11 13
6 9
12 13
1 6
0 3
17 7 19 15 12 20
2 4
0 1
10 15
16 18 1 5
---
2 7 -1 | 67877593
-1 | 1
-1 2 | 1000007
-1 4 -1 -1 2 -1 | 485851160
-1 -1 2 -1 | 341142593
=== hidden
3 4
2 3
13 18
0 2
18 8 6 1
5 4
8 10
0 5
0 5
10 16
11 14
15 11 2 3
4 4
3 5
12 16
4 8
8 9
10 9 15 14
5 5
8 9
6 11
3 9
12 14
9 15
7 3 6 6 8
5 2
5 11
3 4
15 17
11 15
6 7
3 11
---
6 -1 -1 3 | 349055115
7 4 6 6 | 752075284
-1 2 5 5 | 637861870
6 7 6 6 2 | 997745479
2 5 | 4000019
=== hidden
@gen 3635521168 big
=== hidden
@gen 3635521169 big
=== hidden
@gen 3635521170 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(5 if not big else 1):
    n = r.randint(1, 6) if not big else 200000; m = r.randint(1, 6) if not big else 200000
    print(n, m)
    for _ in range(n):
        l = r.randint(0, 15) if not big else r.randint(0, 10**9 - 10**5); print(l, l + r.randint(0, 6 if not big else 10**5))
    print(*[r.randint(0, 20) if not big else r.randint(0, 10**9) for _ in range(m)])
```

## Hints
- Sorting the queries lets you sweep: process them from the smallest point to the largest.
- Add the intervals whose left end is `≤ q` to a min-heap ordered by length.
- Before answering, pop heap tops whose right end is `< q`. They can't cover this query or any later one.

## Solution
**Offline processing.** When all the queries are known in advance, you can answer them in whatever order is convenient, here increasing `q`. Then both "has this interval started?" and "has it ended?" become monotone:

- An interval with `l ≤ q` has started for this query **and every later one**, so push it once.
- An interval with `r < q` has ended for this query **and every later one**, so lazy deletion from the heap top is safe.

The heap is keyed by length, so after discarding the expired tops, the top is the shortest interval covering `q`. Expired intervals deeper in the heap don't matter until they surface.

Each interval is pushed and popped at most once. Restore the answers to the input order through the saved indices.

Complexity: O((n + m) log n).

```cpp
#include <bits/stdc++.h>
using namespace std;

vector<long long> smallest_covering(vector<pair<long long,long long>> iv, const vector<long long>& q) {
    sort(iv.begin(), iv.end());                                   // by left end
    vector<int> order(q.size());
    iota(order.begin(), order.end(), 0);
    sort(order.begin(), order.end(), [&](int a, int b) { return q[a] < q[b]; });
    using Item = pair<long long,long long>;                       // (length, right end)
    priority_queue<Item, vector<Item>, greater<>> heap;
    vector<long long> ans(q.size(), -1);
    size_t i = 0;
    for (int qi : order) {
        long long x = q[qi];
        while (i < iv.size() && iv[i].first <= x) {               // intervals that have started by x
            heap.push({iv[i].second - iv[i].first + 1, iv[i].second});
            ++i;
        }
        while (!heap.empty() && heap.top().second < x) heap.pop();   // ended before x: useless forever
        if (!heap.empty()) ans[qi] = heap.top().first;
    }
    return ans;
}
```
