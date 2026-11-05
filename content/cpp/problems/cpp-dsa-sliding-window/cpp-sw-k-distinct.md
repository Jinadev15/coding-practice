---
id: cpp-sw-k-distinct
title: Longest Window with at Most K Distinct Values
difficulty: Medium
order: 4
tags: sliding window, hashing, frequency map
time_limit: 2
---
## Statement
```cpp
int longest_k_distinct(const std::vector<int>& a, int K);
    // length of the longest subarray containing at most K distinct values (K >= 0)
```

This problem also appears as "Fruit Into Baskets" (K = 2: you have two baskets, each holding one kind of fruit).

Keep a frequency map of the window and the number of distinct values in it. When adding `a[R]` makes the distinct count exceed `K`, shrink from the left until it doesn't. A value leaves the window when its count drops to 0.

Values are arbitrary 32-bit integers, so use `std::unordered_map` (or compress the values first, then use a plain vector, which is faster).

**Input:** cases until the end of input: `n K` + n values (n ≤ 10⁶).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

int longest_k_distinct(const vector<int>& a, int K) { return 0; }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n, K;
    while (cin >> n >> K) {
        vector<int> a(n);
        for (auto& x : a) cin >> x;
        cout << longest_k_distinct(a, K) << '\n';
    }
}
```

## Tests
=== sample
5 2
1 2 1 2 3
7 2
3 3 3 1 2 1 1
---
4
4
=== hidden
1 0
5
1 1
5
6 3
1 2 3 4 5 6
5 10
1 1 2 2 3
---
0
1
3
5
=== hidden
1 3
2
1 4
4
12 2
3 4 4 2 4 3 2 5 4 2 4 2
9 1
2 3 2 1 3 2 3 3 5
10 0
5 4 5 2 1 3 5 3 5 4
1 2
2
---
1
1
4
2
0
1
=== hidden
12 2
2 3 3 4 3 3 4 5 4 5 5 3
12 3
4 5 1 1 3 1 3 5 5 3 5 4
3 0
5 1 4
12 1
5 4 5 2 3 3 1 1 2 4 5 4
9 1
4 2 5 2 2 2 2 5 5
10 1
5 2 2 1 4 4 4 5 4 4
---
6
10
0
2
4
3
=== hidden
2 0
5 1
11 2
5 2 4 3 5 5 2 3 4 3 1
7 2
1 2 5 1 3 1 4
4 0
1 3 1 1
5 2
3 1 5 4 3
12 1
2 4 3 3 4 2 1 4 5 2 1 1
---
0
3
3
0
2
2
=== hidden
@gen 2824635464 big
=== hidden
@gen 2824635465 big
=== hidden
@gen 2824635466 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 1):
    n = r.randint(1, 12) if not big else 1000000
    print(n, r.randint(0, 4) if not big else r.randint(1, 1000)); print(*[r.randint(1, 5) if not big else r.randint(-2**31, 2**31 - 1) % 5000 * 858993 for _ in range(n)])
```

## Hints
- Keep `cnt[value]` for the window, and a `distinct` counter that changes only when a count goes 0→1 or 1→0.
- After adding `a[R]`, shrink while `distinct > K`.
- Values are up to 2³¹: either use `unordered_map`, or compress them to `0..m−1` first.

## Solution
"At most K distinct" is monotone: removing elements can only reduce the number of distinct values. So the grow/shrink window applies. Track `distinct` incrementally:

- it rises when a value's count goes from 0 to 1;
- it falls when a count goes from 1 to 0.

**Coordinate compression** (sort the distinct values, then map each value to its rank with `lower_bound`) turns arbitrary integers into indices `0..m−1`. That lets a `vector<int>` replace the hash map, which is deterministic and several times faster. An `unordered_map<int,int>` works too.

With `K = 0` the shrink loop empties every window, and the answer is 0.

Complexity: O(n log n) for the compression plus O(n) for the window.

```cpp
#include <bits/stdc++.h>
using namespace std;

int longest_k_distinct(const vector<int>& a, int K) {
    // compress values to 0..m-1 so a vector can hold the counts
    vector<int> vals(a.begin(), a.end());
    sort(vals.begin(), vals.end());
    vals.erase(unique(vals.begin(), vals.end()), vals.end());
    vector<int> id(a.size());
    for (size_t i = 0; i < a.size(); ++i) id[i] = lower_bound(vals.begin(), vals.end(), a[i]) - vals.begin();

    vector<int> cnt(vals.size(), 0);
    int distinct = 0, best = 0, L = 0;
    for (int R = 0; R < (int)a.size(); ++R) {
        if (cnt[id[R]]++ == 0) ++distinct;                 // a new value entered
        while (distinct > K) if (--cnt[id[L++]] == 0) --distinct;   // a value fully left
        best = max(best, R - L + 1);
    }
    return best;
}
```
