---
id: cpp-bs-rotated-duplicates
title: Rotated Arrays with Duplicates
difficulty: Hard
order: 4
tags: binary search, rotated array, duplicates, worst case analysis
time_limit: 1
---
## Statement
Now the rotated sorted array may contain **duplicates**: `[2 5 6 0 0 1 2]` or `[1 1 1 1 0 1 1]`.

```cpp
bool contains(const std::vector<int>& a, int x);
int find_min(const std::vector<int>& a);          // the minimum VALUE
```

When `a[lo] == a[mid] == a[hi]`, you **can't tell** which half is sorted. `[1 1 1 0 1]` and `[1 0 1 1 1]` look the same at those three positions. The safe move is to shrink both ends (`++lo; --hi`), which removes no possible answer, because the removed values equal `a[mid]`, which is still inside the range. In the worst case (almost all elements equal) the search degrades to O(n). That is unavoidable.

For `find_min`: compare `a[mid]` with `a[hi]`.

- If `a[mid] > a[hi]`, the minimum is to the right.
- If `a[mid] < a[hi]`, it is at `mid` or to the left.
- If they are equal, `hi--`.

**Input:** `n`, n values, `q`, then q targets (n ≤ 2·10⁵, q ≤ 2·10⁵). Most arrays have few duplicates, so a linear scan per query is too slow.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

bool contains(const vector<int>& a, int x) { return find(a.begin(), a.end(), x) != a.end(); }
int find_min(const vector<int>& a) { return *min_element(a.begin(), a.end()); }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n; cin >> n;
    vector<int> a(n); for (auto& x : a) cin >> x;
    int q; cin >> q;
    cout << "min " << find_min(a) << " |";
    unsigned long long h = 0; int shown = 0;
    while (q--) { int x; cin >> x; bool r = contains(a, x); if (shown++ < 20) cout << ' ' << r; h = h * 3 + r; }
    cout << " | " << h << '\n';
}
```

## Tests
=== sample
7
2 5 6 0 0 1 2
2
0 3
5
1 1 1 0 1
2
0 2
---
min 0 | 1 0 | 3
=== hidden
1
3
1
3
3
1 0 1
3
0 1 2
5
1 1 1 1 1
1
1
---
min 3 | 1 | 1
=== hidden
9
0 0 1 1 1 2 3 3 4
4
0 4 5 2
2
1 1
2
1 0
4
2 2 0 2
3
0 2 1
5
3 1 2 3 3
2
1 3
---
min 0 | 1 1 0 1 | 37
=== hidden
1
2
20
2 5 2 2 2 2 2 0 -1 1 2 2 3 2 4 4 4 2 2 2
---
min 2 | 1 0 1 1 1 1 1 0 0 0 1 1 0 1 0 0 0 1 1 1 | 1355201536
=== hidden
2
0 4
20
2 4 4 4 0 4 0 4 4 4 0 4 0 0 4 0 0 0 -1 4
---
min 0 | 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 0 1 | 581130730
=== hidden
10
0 0 0 0 4 4 0 0 0 0
20
0 0 0 0 5 0 3 3 5 2 0 4 0 0 0 3 -1 0 4 4
---
min 0 | 1 1 1 1 0 1 0 0 0 0 1 1 1 1 1 0 0 1 1 1 | 1726681225
=== hidden
@gen 3016532099 big
=== hidden
@gen 3016532100 big
=== hidden
@gen 3016532101 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
n = r.randint(1, 10) if not big else 200000
a = sorted(r.randint(0, 4) if not big else r.randint(0, 10**9) for _ in range(n))
k = r.randrange(n); a = a[k:] + a[:k]
q = 20 if not big else 200000
print(n); print(*a); print(q)
print(" ".join(str(r.choice(a) if r.random() < 0.6 else r.randint(-1, 5) if not big else r.randint(0, 10**9)) for _ in range(q)))
```

## Hints
- Duplicates make `a[lo] == a[mid] == a[hi]` ambiguous. In that case, shrink both ends by one.
- Otherwise, use the distinct-values logic: one half is sorted, so range-check x against it.
- For the minimum, compare `a[mid]` with `a[hi]`. When they are equal, decrement `hi`.

## Solution
**What duplicates break.** With distinct values, `a[lo] <= a[mid]` proves the left half is sorted. With duplicates, `a[lo] == a[mid]` could happen with the rotation point *inside* the left half (`[1 1 1 0 1]`, lo = 0, mid = 2). Only when all three probes are equal is the situation truly ambiguous. Then discarding `a[lo]` and `a[hi]` is safe, because a copy of their value remains at `mid`.

When the probes aren't all equal, the usual reasoning still holds. If `a[lo] == a[mid] != a[hi]`, the left half consists entirely of copies of `a[lo]` (otherwise the values would have to drop and come back up twice), so it can be treated as sorted.

**Minimum.** Comparing with `a[hi]` is the cleanest. On equality, `hi` can go: if `a[hi]` was the minimum, `a[mid]` is an equal minimum that is still in range.

**Complexity:** O(log n) on typical inputs, O(n) in the worst case (e.g. `[1 1 1 … 1 0 1 … 1]`). No algorithm can do better there, because it must find the single different element.

```cpp
#include <bits/stdc++.h>
using namespace std;

bool contains(const vector<int>& a, int x) {
    int lo = 0, hi = (int)a.size() - 1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        if (a[mid] == x) return true;
        if (a[lo] == a[mid] && a[mid] == a[hi]) { ++lo; --hi; continue; }   // ambiguous: trim both ends
        if (a[lo] <= a[mid]) {                                              // left half sorted
            if (a[lo] <= x && x < a[mid]) hi = mid - 1; else lo = mid + 1;
        } else {                                                            // right half sorted
            if (a[mid] < x && x <= a[hi]) lo = mid + 1; else hi = mid - 1;
        }
    }
    return false;
}

int find_min(const vector<int>& a) {
    int lo = 0, hi = (int)a.size() - 1;
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (a[mid] > a[hi]) lo = mid + 1;        // drop is to the right of mid
        else if (a[mid] < a[hi]) hi = mid;       // mid..hi is increasing: min is at mid or left
        else --hi;                               // equal: a[hi] has a copy at mid, safe to discard
    }
    return a[lo];
}
```
