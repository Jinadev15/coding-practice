---
id: cpp-tp-dedup-k
title: Remove Duplicates, Keeping at Most k
difficulty: Medium
order: 4
tags: two pointers, read/write pointer, in-place, sorted arrays
time_limit: 2
---
## Statement
The array is sorted. Remove duplicates **in place** so that each value appears **at most k times**, preserving order. Return the new length `w`. The first `w` slots must hold the answer.

```cpp
int keep_at_most(std::vector<int>& a, int k);    // 1 <= k
```

`[1,1,1,2,2,3]` with `k = 2` gives `w = 5` and `[1,1,2,2,3]`. With `k = 1` the result is `[1,2,3]`.

Use a write pointer `w`. An element is kept when `w < k`, or when it differs from `a[w − k]`, the element written k positions earlier. Think about why that single comparison is enough in a sorted array.

**Input:** cases until the end of input: `n k` + `n` sorted values (n ≤ 10⁶). Print `w`, the first 20 kept values, and a checksum.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

int keep_at_most(vector<int>& a, int k) {
    a.erase(unique(a.begin(), a.end()), a.end());     // keeps only ONE copy, ignores k
    return (int)a.size();
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n, k;
    while (cin >> n >> k) {
        vector<int> a(n);
        for (auto& x : a) cin >> x;
        int w = keep_at_most(a, k);
        long long h = 0;
        for (int i = 0; i < w; ++i) h = (h * 1000003 + a[i] + 1000000000LL) % 998244353;
        cout << w << ':';
        for (int i = 0; i < min(w, 20); ++i) cout << ' ' << a[i];
        cout << " | " << h << '\n';
    }
}
```

## Tests
=== sample
6 2
1 1 1 2 2 3
6 1
1 1 1 2 2 3
---
5: 1 1 2 2 3 | 944185797
3: 1 2 3 | 262448839
=== hidden
1 1
5
5 3
7 7 7 7 7
4 10
1 1 1 1
8 2
0 0 1 1 1 1 2 3
---
1: 5 | 1755652
3: 7 7 7 | 854887382
4: 1 1 1 1 | 439852273
6: 0 0 1 1 2 3 | 546858822
=== hidden
6 2
0 1 2 3 4 4
3 3
1 3 4
7 4
0 1 3 3 4 4 4
11 2
0 1 1 1 2 2 2 4 4 4 4
8 4
1 1 2 3 4 4 4 4
8 3
0 0 1 2 3 3 3 4
---
6: 0 1 2 3 4 4 | 615798367
3: 1 3 4 | 263448843
7: 0 1 3 3 4 4 4 | 209577708
7: 0 1 1 2 2 4 4 | 177999515
8: 1 1 2 3 4 4 4 4 | 815750853
8: 0 0 1 2 3 3 3 4 | 551053032
=== hidden
6 2
1 1 2 2 2 2
11 3
0 1 2 2 2 3 3 3 4 4 4
5 3
0 0 0 3 4
10 4
0 0 1 1 2 3 3 4 4 4
5 4
0 2 3 4 4
12 1
0 0 1 1 1 1 2 3 4 4 4 4
---
4: 1 1 2 2 | 440852277
11: 0 1 2 2 2 3 3 3 4 4 4 | 179373850
5: 0 0 0 3 4 | 878246263
10: 0 0 1 1 2 3 3 4 4 4 | 591672727
5: 0 2 3 4 4 | 320445376
5: 0 1 2 3 4 | 980547146
=== hidden
10 2
0 1 1 2 2 2 2 3 3 3
6 3
1 1 2 2 2 3
12 3
0 0 0 0 1 2 2 3 3 3 3 4
2 2
0 2
12 4
0 0 0 0 1 2 2 3 3 3 4 4
1 3
3
---
7: 0 1 1 2 2 3 3 | 176999511
6: 1 1 2 2 2 3 | 207272341
10: 0 0 0 1 2 2 3 3 3 4 | 617802113
2: 0 2 | 740450016
12: 0 0 0 0 1 2 2 3 3 3 4 4 | 614599915
1: 3 | 1755650
=== hidden
@gen 3431805423 big
=== hidden
@gen 3431805424 big
=== hidden
@gen 3431805425 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 1):
    n = r.randint(1, 12) if not big else 1000000
    a = sorted(r.randint(0, 4) if not big else r.randint(0, 100000) for _ in range(n))
    print(n, r.randint(1, 4)); print(*a)
```

## Hints
- Keep a write index `w`. Elements before `w` form the answer so far.
- An element is safe to keep if fewer than k copies of it are already among the last k written elements.
- In a sorted array, that is exactly `w < k || a[r] != a[w − k]`.

## Solution
In a sorted array, copies of a value are contiguous, and the kept prefix `a[0..w)` is sorted too. If `a[r] == a[w − k]`, then the last `k` kept elements (`a[w−k..w−1]`) are all equal to `a[r]`. They're sandwiched between equal values in sorted order. So `k` copies are already kept and `a[r]` must be skipped. Otherwise there are fewer than `k` copies, so keep it.

This one comparison replaces any counting. The `w < k` clause covers the start, when there's nothing `k` places back yet. With `k = 1` it reduces to the classic `std::unique`.

Complexity: O(n) time, O(1) space.

```cpp
#include <bits/stdc++.h>
using namespace std;

int keep_at_most(vector<int>& a, int k) {
    int w = 0;                                          // a[0..w) is the compacted answer
    for (int r = 0; r < (int)a.size(); ++r)
        if (w < k || a[r] != a[w - k]) a[w++] = a[r];   // fewer than k copies of a[r] kept so far
    return w;
}
```
