---
id: cpp-bs-rotated
title: Searching a Rotated Sorted Array
difficulty: Medium
order: 3
tags: binary search, rotated array, invariants
time_limit: 2
---
## Statement
A sorted array of **distinct** values was rotated at an unknown pivot: `[0 1 2 4 5 6 7]` might become `[4 5 6 7 0 1 2]`.

```cpp
int rotation_point(const std::vector<int>& a);   // index of the minimum element (0 if not rotated)
int search_rotated(const std::vector<int>& a, int x);   // index of x, or -1
```

Both must be O(log n).

- **Minimum:** the predicate `a[i] <= a[n−1]` is false on the left (higher) part and true on the right part, so the first true index is the minimum.
- **Search:** at every `mid`, one half is sorted. Decide whether `x` lies within that sorted half's range. If so, search there, otherwise in the other half. (Or find the rotation point first, then do an ordinary binary search on the correct side.)

**Input:** `n`, n values, `q`, then q targets (n, q ≤ 10⁶).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

int rotation_point(const vector<int>& a) { return int(min_element(a.begin(), a.end()) - a.begin()); }   // O(n)
int search_rotated(const vector<int>& a, int x) { auto it = find(a.begin(), a.end(), x); return it == a.end() ? -1 : int(it - a.begin()); }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n; cin >> n;
    vector<int> a(n); for (auto& x : a) cin >> x;
    int q; cin >> q;
    cout << "min at " << rotation_point(a) << " |";
    unsigned long long h = 0; int shown = 0;
    while (q--) { int x; cin >> x; int r = search_rotated(a, x); if (shown++ < 15) cout << ' ' << r; h = h * 1000003 + (unsigned)(r + 1); }
    cout << " | " << h << '\n';
}
```

## Tests
=== sample
7
4 5 6 7 0 1 2
3
0 3 7
---
min at 4 | 4 -1 3 | 5000030000049
=== hidden
1
5
2
5 3
2
2 1
2
1 2
---
min at 0 | 0 -1 | 1000003
=== hidden
5
24 28 -39 -14 22
20
28 -60 -14 -14 -14 -46 30 -14 24 -18 27 22 24 -8 -39 22 28 20 20 -19
---
min at 2 | 1 -1 3 3 3 -1 -1 3 0 -1 -1 4 0 -1 2 | 13003788887229507781
=== hidden
1
-27
20
-32 -27 -27 -51 -27 -27 -27 -27 -24 -29 -27 -27 -27 -27 -27 3 -27 -23 -27 -21
---
min at 0 | -1 0 0 -1 0 0 0 0 -1 -1 0 0 0 0 0 | 2055554962109456045
=== hidden
9
5 16 18 33 -29 -26 -24 -23 4
20
-26 -29 16 16 33 18 16 33 -26 -15 33 18 -45 33 6 -26 -26 16 4 -3
---
min at 4 | 5 4 1 1 3 2 1 3 5 -1 3 2 -1 3 -1 | 11264838229689200194
=== hidden
@gen 440066742 big
=== hidden
@gen 440066743 big
=== hidden
@gen 440066744 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
n = r.randint(1, 10) if not big else 1000000
a = sorted(r.sample(range(-50, 50) if not big else range(-2*10**9, 2*10**9, 3), n))
k = r.randrange(n); a = a[k:] + a[:k]
q = 20 if not big else 1000000
print(n); print(*a); print(q)
print(" ".join(str(r.choice(a) if r.random() < 0.6 else r.randint(-60, 60) if not big else r.randint(-2*10**9, 2*10**9)) for _ in range(q)))
```

## Hints
- Every element of the "low" block is ≤ the last element, and every element of the "high" block is bigger. That gives you a monotone condition for the minimum.
- At any mid, one of the halves `[lo, mid]` or `[mid, hi]` is sorted. Check `a[lo] <= a[mid]`.
- If x lies within the sorted half's endpoints, continue there. Otherwise continue in the other half.

## Solution
**Rotation point.** The array consists of two increasing blocks, a high block and a low block, and every element of the low block is `≤ a[n−1]`, while every element of the high block is greater. So `a[i] <= a[n−1]` is a monotone predicate, and its first true index is the minimum. (For an unrotated array it's true everywhere, giving 0.)

**Search.** In `[lo, hi]`, the elements on one side of `mid` are guaranteed to be sorted. That's the left side if `a[lo] <= a[mid]`, because the drop isn't between them. Range-checking `x` against a **sorted** half is reliable. If `x` isn't in it, it must be in the other half (or nowhere). Each step halves the range.

This uses the closed-interval form with an equality exit, which is natural when you look for an exact value. For boundary searches, stick to the half-open "first true" form.

Complexity: O(log n) per query.

```cpp
#include <bits/stdc++.h>
using namespace std;

int rotation_point(const vector<int>& a) {
    int n = a.size(), lo = 0, hi = n - 1;            // a[n-1] itself satisfies the predicate
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (a[mid] <= a[n - 1]) hi = mid;            // mid is in the lower (rotated-around) block
        else lo = mid + 1;                            // mid is in the higher block: the minimum is to the right
    }
    return lo;
}

int search_rotated(const vector<int>& a, int x) {
    int lo = 0, hi = (int)a.size() - 1;
    while (lo <= hi) {                                // classic closed-interval search with an exact match
        int mid = lo + (hi - lo) / 2;
        if (a[mid] == x) return mid;
        if (a[lo] <= a[mid]) {                        // left half [lo, mid] is sorted
            if (a[lo] <= x && x < a[mid]) hi = mid - 1; else lo = mid + 1;
        } else {                                      // right half [mid, hi] is sorted
            if (a[mid] < x && x <= a[hi]) lo = mid + 1; else hi = mid - 1;
        }
    }
    return -1;
}
```
