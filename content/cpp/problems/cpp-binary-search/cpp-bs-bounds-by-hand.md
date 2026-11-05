---
id: cpp-bs-bounds-by-hand
title: lower_bound and upper_bound by Hand
difficulty: Easy
order: 1
tags: binary search, lower bound, upper bound, counting
time_limit: 2
---
## Statement
Implement the two fundamental searches yourself (no `std::lower_bound`/`upper_bound`/`equal_range`), then use them:

```cpp
int my_lower_bound(const std::vector<long long>& a, long long x);   // first index with a[i] >= x (n if none)
int my_upper_bound(const std::vector<long long>& a, long long x);   // first index with a[i] >  x (n if none)
long long count_in_range(const std::vector<long long>& a, long long lo, long long hi);   // #elements in [lo, hi]
```

`a` is sorted ascending and may contain duplicates. Use the "first true" template from the lesson: `lo = 0`, `hi = n`, `while (lo < hi)`.

**Input:** `n`, n sorted values, `q`, then q queries `L x`, `U x` or `C lo hi` (n, q ≤ 10⁶, |values| ≤ 10¹⁸).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

int my_lower_bound(const vector<long long>& a, long long x) { int i = 0; while (i < (int)a.size() && a[i] < x) ++i; return i; }
int my_upper_bound(const vector<long long>& a, long long x) { int i = 0; while (i < (int)a.size() && a[i] <= x) ++i; return i; }
long long count_in_range(const vector<long long>& a, long long lo, long long hi) { return my_upper_bound(a, hi) - my_lower_bound(a, lo); }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n; cin >> n;
    vector<long long> a(n);
    for (auto& x : a) cin >> x;
    int q; cin >> q;
    unsigned long long h = 0; int shown = 0;
    while (q--) {
        char t; cin >> t;
        long long r;
        if (t == 'L') { long long x; cin >> x; r = my_lower_bound(a, x); }
        else if (t == 'U') { long long x; cin >> x; r = my_upper_bound(a, x); }
        else { long long lo, hi; cin >> lo >> hi; r = count_in_range(a, lo, hi); }
        if (shown < 20) { cout << r << ' '; ++shown; }
        h = h * 1000003 + (unsigned long long)r;
    }
    cout << "| " << h << '\n';
}
```

## Tests
=== sample
5
1 2 2 2 3
6
L 2
U 2
L 4
U 0
C 2 2
C 0 5
---
1 4 5 0 3 5 | 1681554433115784332
=== hidden
1
7
4
L 7
U 7
C 8 9
C 7 7
---
0 1 0 1 | 1000006000010
=== hidden
7
-5 -2 -2 1 2 3 4
20
U 0
L -6
C -6 -5
L -5
C -2 -4
C -3 0
L 0
U 2
U 1
C 2 8
U -2
L -6
L -1
C -5 -5
U 4
L 4
U -6
U 0
L -6
L -4
---
3 0 1 0 0 2 3 5 4 3 3 0 3 1 7 6 0 3 0 1 | 11606830247472577189
=== hidden
4
-3 -3 2 4
20
C 2 5
U 0
C -6 -4
L 5
U -2
U 6
U 5
C -5 -2
C -3 -1
L -4
L 6
C 3 3
L 3
L 3
U 4
L -4
L -3
U -6
C 4 10
C 4 10
---
2 2 0 4 2 4 4 2 2 0 4 0 3 3 4 0 0 0 1 1 | 7130151630817418290
=== hidden
7
-5 -3 -1 -1 -1 0 5
20
L -2
U 3
L 3
C -2 4
C 5 10
C -1 3
L -3
L 2
C 0 4
C -6 -7
C -3 -2
L -2
U 6
C 1 0
C 4 6
C 3 8
C 5 7
L -1
C -1 -1
L 4
---
2 6 6 4 1 4 1 6 1 0 1 2 7 0 1 1 1 2 3 6 | 8114372364351327543
=== hidden
@gen 3802361216 big
=== hidden
@gen 3802361217 big
=== hidden
@gen 3802361218 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
n = r.randint(0, 10) if not big else 1000000
a = sorted(r.randint(-5, 5) if not big else r.randint(-10**18, 10**18) for _ in range(n))
print(n); print(*a)
q = 20 if not big else 1000000
print(q)
out = []
for _ in range(q):
    t = r.choice("LUC")
    if big and a and r.random() < 0.5: x = r.choice(a)
    else: x = r.randint(-6, 6) if not big else r.randint(-10**18, 10**18)
    if t == "C": y = x + r.randint(-2, 6) if not big else x + r.randint(0, 10**17); out.append(f"C {x} {y}")
    else: out.append(f"{t} {x}")
print("\n".join(out))
```

## Hints
- Keep `lo = 0` and `hi = n`, and loop while `lo < hi`. Look at `mid = lo + (hi − lo)/2`.
- If the condition holds at `mid`, the answer is at `mid` or to its left (`hi = mid`). Otherwise it is to the right (`lo = mid + 1`).
- Count in a range: `upper_bound(hi) − lower_bound(lo)`. An empty range gives 0.

## Solution
One generic `first_true` routine answers every "first index where a monotone condition holds" question:

- `a[i] >= x` is false for small indices and true from some point on, so its first true index is `lower_bound`.
- `a[i] > x` gives `upper_bound`.

**Counting values in `[lo, hi]`:** the elements `< lo` occupy indices `[0, lower_bound(lo))`, and the elements `≤ hi` occupy `[0, upper_bound(hi))`. Subtracting gives the count, in two O(log n) searches.

The half-open range `[lo, hi)` with `hi = n` returns `n` naturally when no element qualifies, with no special case.

Complexity: O(log n) per query.

```cpp
#include <bits/stdc++.h>
using namespace std;

template <class P>
static int first_true(int n, P pred) {          // pred is false...false true...true over [0, n)
    int lo = 0, hi = n;
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (pred(mid)) hi = mid; else lo = mid + 1;
    }
    return lo;
}

int my_lower_bound(const vector<long long>& a, long long x) {
    return first_true((int)a.size(), [&](int i) { return a[i] >= x; });
}
int my_upper_bound(const vector<long long>& a, long long x) {
    return first_true((int)a.size(), [&](int i) { return a[i] > x; });
}
long long count_in_range(const vector<long long>& a, long long lo, long long hi) {
    if (lo > hi) return 0;
    return my_upper_bound(a, hi) - my_lower_bound(a, lo);
}
```
