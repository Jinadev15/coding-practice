---
id: cpp-bs-k-closest
title: K Closest Elements
difficulty: Medium
order: 8
tags: binary search, windows, sorted arrays
time_limit: 2
---
## Statement
`a` is sorted. Return the `k` elements closest to `x`, in sorted order. Element `u` is closer than `v` if `|u − x| < |v − x|`, or if they are equally far and `u < v`.

```cpp
std::vector<int> k_closest(const std::vector<int>& a, int k, int x);
```

The answer is always a **contiguous window** `a[L..L+k−1]`. Binary search for its start `L` in `[0, n − k]`:

- if `x − a[mid] > a[mid + k] − x`, the window starting at `mid` is worse than shifting right, so `lo = mid + 1`;
- otherwise `hi = mid`.

That's O(log(n − k) + k).

**Input:** `n`, the array, `q`, then q queries `k x` (n ≤ 10⁶, q ≤ 10⁵, total k ≤ 10⁶). The driver prints the first window's elements and a checksum.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> k_closest(const vector<int>& a, int k, int x) {
    vector<int> b = a;
    stable_sort(b.begin(), b.end(), [&](int u, int v) { return abs(u - x) < abs(v - x); });   // O(n log n) per query
    b.resize(k); sort(b.begin(), b.end()); return b;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n; cin >> n; vector<int> a(n); for (auto& v : a) cin >> v;
    int q; cin >> q;
    unsigned long long h = 0; bool first = true;
    while (q--) {
        int k, x; cin >> k >> x;
        auto r = k_closest(a, k, x);
        if (first) { for (int v : r) cout << v << ' '; cout << "| "; first = false; }
        for (int v : r) h = h * 1000003 + (unsigned)(v + 1000000000);
    }
    cout << h << '\n';
}
```

## Tests
=== sample
5
1 2 3 4 5
3
4 3
4 -1
2 6
---
1 2 3 4 | 2596694333942567237
=== hidden
1
7
2
1 7
1 -1000000000
6
1 1 2 2 2 3
3
3 2
4 1
2 3
---
7 | 1000004007000028
=== hidden
6
-3 -2 1 1 2 6
10
1 7
4 10
3 -4
5 -9
3 0
3 0
5 10
6 -5
1 -7
6 1
---
6 | 12244662451409674030
=== hidden
2
1 2
10
2 -6
2 0
2 2
2 -4
1 1
2 -3
2 -4
1 -8
1 0
2 3
---
1 2 | 3878102496867440808
=== hidden
6
-8 1 2 4 7 8
10
2 -10
4 1
1 -8
3 7
4 -9
2 -2
2 -9
1 7
4 1
6 -6
---
-8 1 | 12272512469255345552
=== hidden
@gen 4072827930 big
=== hidden
@gen 4072827931 big
=== hidden
@gen 4072827932 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
n = r.randint(1, 10) if not big else 1000000
a = sorted(r.randint(-8, 8) if not big else r.randint(-10**9, 10**9) for _ in range(n))
q = 10 if not big else 100000
print(n); print(*a); print(q)
for _ in range(q): print(r.randint(1, n if not big else min(n, 10)), r.randint(-10, 10) if not big else r.randint(-10**9, 10**9))
```

## Hints
- The k closest elements always form a contiguous block of the sorted array.
- Binary search the block's start L in [0, n − k] by comparing the element that would leave (`a[mid]`) with the one that would enter (`a[mid+k]`).
- Shift right only if `x − a[mid] > a[mid+k] − x` (strictly), which keeps smaller values on ties.

## Solution
**Why a window.** If a value `v` is among the k closest, every value between `v` and `x` is at least as close, so the chosen set has no gaps in sorted order.

**Searching for the window's start.** Compare window `[mid, mid+k−1]` with window `[mid+1, mid+k]`. They differ only by dropping `a[mid]` and adding `a[mid+k]`.

- If `x − a[mid] > a[mid+k] − x`, then `a[mid+k]` is strictly closer than `a[mid]`, so the optimum starts after `mid`.
- Otherwise starting at `mid` (or earlier) is at least as good. On ties the smaller value, `a[mid]`, wins, so stay.

This "is shifting right better?" test is monotone in `mid`, which makes it binary-searchable. Writing it without `abs` also handles `x` outside the array's range correctly.

Complexity: O(log(n − k) + k) per query.

```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> k_closest(const vector<int>& a, int k, int x) {
    int lo = 0, hi = (int)a.size() - k;                // candidate window starts
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        // compare the element leaving (a[mid]) with the one entering (a[mid+k]) if we shift right
        if ((long long)x - a[mid] > (long long)a[mid + k] - x) lo = mid + 1;
        else hi = mid;
    }
    return vector<int>(a.begin() + lo, a.begin() + lo + k);
}
```
