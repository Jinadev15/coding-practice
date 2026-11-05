---
id: cpp-frequency-sort
title: Sort by Frequency, and a Custom Order
difficulty: Easy
order: 6
tags: sorting, hashing, comparators, counting
time_limit: 1
---
## Statement
Two comparator exercises driven by precomputed data:

```cpp
std::vector<int> by_frequency(std::vector<int> a);
    // most frequent values first; equal frequency -> smaller value first; equal values stay together
std::vector<int> relative_order(std::vector<int> a, const std::vector<int>& order);
    // values that appear in `order` come first, in that order (all copies of each);
    // the remaining values follow in ascending order
```

Example: `by_frequency([4,6,2,6,4,4,2])` gives `[4,4,4,2,2,6,6]`, since 4 appears 3 times, and 2 and 6 tie at 2 times with 2 < 6. Also, `relative_order([2,3,1,3,2,4,6,7,9,2,19], [2,1,4,3,9,6])` gives `[2,2,2,1,4,3,3,9,6,7,19]`.

Count frequencies, or build a rank table, **before** sorting, so each comparison is O(1).

**Input:** cases until the end of input: `freq n` + values, or `rel n m` + `n` values + `m` order values (the order values are distinct). n ≤ 2·10⁵.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> by_frequency(vector<int> a) { sort(a.begin(), a.end()); return a; }
vector<int> relative_order(vector<int> a, const vector<int>& order) { sort(a.begin(), a.end()); return a; }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string cmd; int n;
    while (cin >> cmd >> n) {
        vector<int> r;
        if (cmd == "freq") {
            vector<int> a(n); for (auto& x : a) cin >> x;
            r = by_frequency(a);
        } else {
            int m; cin >> m;
            vector<int> a(n), o(m);
            for (auto& x : a) cin >> x;
            for (auto& x : o) cin >> x;
            r = relative_order(a, o);
        }
        long long h = 0;
        for (int x : r) h = (h * 1000003 + x + 1000000007LL) % 998244353;
        for (size_t i = 0; i < min<size_t>(r.size(), 20); ++i) cout << r[i] << ' ';
        cout << "| " << h << '\n';
    }
}
```

## Tests
=== sample
freq 7
4 6 2 6 4 4 2
rel 11 6
2 3 1 3 2 4 6 7 9 2 19
2 1 4 3 9 6
---
4 4 4 2 2 6 6 | 740268460
2 2 2 1 4 3 3 9 6 7 19 | 48864213
=== hidden
freq 1
5
freq 6
-1 -1 3 3 0 0
rel 3 2
5 4 3
9 8
rel 4 4
1 2 3 4
4 3 2 1
---
5 | 1755659
-1 -1 0 0 3 3 | 513828673
3 4 5 | 154362308
4 3 2 1 | 61142389
=== hidden
freq 2
4 -5
freq 10
-3 2 1 0 -3 2 0 3 -5 -4
rel 12 0
2 -2 0 0 0 0 -1 -4 0 4 -4 1

freq 4
2 -2 -3 -2
rel 4 0
2 1 -3 -3

---
-5 4 | 742450031
-3 -3 0 0 2 2 -5 -4 1 3 | 801290025
-4 -4 -2 -1 0 0 0 0 0 1 2 4 | 906992832
-2 -2 -3 2 | 793178257
-3 -3 1 2 | 460035689
=== hidden
rel 2 0
1 -4

freq 10
-5 5 -1 4 -1 5 -4 -1 -1 -4
freq 8
-2 2 -2 3 2 5 2 1
rel 9 3
-5 1 -5 -2 -4 -4 5 0 -2
-6 2 -3
freq 2
1 4
---
-4 1 | 743450031
-1 -1 -1 -1 -4 -4 5 5 -5 4 | 685090822
2 2 2 -2 -2 1 3 5 | 720346058
-5 -5 -4 -4 -2 -2 0 1 5 | 320827759
1 4 | 748450049
=== hidden
rel 12 1
5 0 1 -1 -2 -4 5 -5 -5 -5 2 -4
2
freq 12
0 1 0 -2 -3 -2 1 0 0 4 1 0
freq 11
-3 4 1 -5 3 -2 5 -3 2 -3 -5
rel 3 4
2 5 2
2 6 4 -4
rel 11 2
3 4 3 2 4 2 -4 0 5 -1 4
-1 -2
---
2 -5 -5 -5 -4 -4 -2 -1 0 1 5 5 | 460268380
0 0 0 0 0 1 1 1 -2 -2 -3 4 | 195545396
-3 -3 -3 -5 -5 -2 1 2 3 4 5 | 616091594
2 2 5 | 387203999
-1 -4 0 2 2 3 3 4 4 4 5 | 874347266
=== hidden
@gen 3850165186 big
=== hidden
@gen 3850165187 big
=== hidden
@gen 3850165188 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(5 if not big else 2):
    n = r.randint(1, 12) if not big else 200000
    a = [r.randint(-5, 5) if not big else r.randint(-1000, 1000) for _ in range(n)]
    if r.random() < 0.5:
        print("freq", n); print(*a)
    else:
        pool = list(range(-6, 7)) if not big else list(range(-1000, 1001))
        r.shuffle(pool); o = pool[:r.randint(0, 6 if not big else 500)]
        print("rel", n, len(o)); print(*a); print(*o)
```

## Hints
- Count each value's frequency with an `unordered_map` before sorting.
- Comparator for frequency sort: compare counts (larger first), then values (smaller first).
- For the relative order, map each value to a key pair: `(0, position in order)` if it's listed, else `(1, value)`. Then compare the keys.

## Solution
**Precompute, then compare.** The comparator is called O(n log n) times, so it must be cheap. Counting with a hash map first makes each comparison two lookups.

**Ties define the result.** "Equal frequency → smaller value first" also guarantees that copies of the same value end up adjacent, because they have equal keys and nothing else sorts between them.

**Key functions.** Mapping each value to a `pair` (group, position-or-value) turns a complicated rule into ordinary lexicographic comparison. Listed values get group 0, ordered by their index in `order`. Everything else gets group 1, ordered by value.

Complexity: O(n log n) time, O(n) space.

```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> by_frequency(vector<int> a) {
    unordered_map<int, int> cnt;
    cnt.reserve(a.size() * 2);
    for (int x : a) ++cnt[x];
    sort(a.begin(), a.end(), [&](int x, int y) {
        int cx = cnt[x], cy = cnt[y];
        if (cx != cy) return cx > cy;      // more frequent first
        return x < y;                      // then smaller value (keeps equal values adjacent)
    });
    return a;
}

vector<int> relative_order(vector<int> a, const vector<int>& order) {
    unordered_map<int, int> rank;
    for (int i = 0; i < (int)order.size(); ++i) rank[order[i]] = i;
    auto key = [&](int x) {
        auto it = rank.find(x);
        return it != rank.end() ? pair<int, long long>{0, it->second}   // listed: by position
                                : pair<int, long long>{1, x};           // unlisted: by value, after
    };
    sort(a.begin(), a.end(), [&](int x, int y) { return key(x) < key(y); });
    return a;
}
```
