---
id: cpp-bs-peaks-bitonic
title: Peaks and Bitonic Arrays
difficulty: Medium
order: 5
tags: binary search, peak finding, bitonic arrays
time_limit: 2
---
## Statement
```cpp
int find_peak(const std::vector<int>& a);
    // ANY index i with a[i] > a[i-1] and a[i] > a[i+1] (outside the array counts as -infinity);
    // neighbours are always different; O(log n)
int bitonic_search(const std::vector<int>& a, int x);
    // a strictly increases, then strictly decreases (a "mountain"); return an index of x or -1; O(log n)
```

- **Peak:** if `a[mid] < a[mid+1]`, the values climb to the right, so a peak must exist to the right (the climb must stop somewhere, at the latest at the edge). Otherwise a peak exists at `mid` or to its left.
- **Bitonic search:** find the summit with the same idea, then run one ascending binary search on the left part and one descending binary search on the right part.

The driver checks `find_peak` with a validity test, because there may be many peaks.

**Input:** cases until the end of input: `peak n` + values, or `bit n q` + n values + q targets (n, q ≤ 10⁶).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

int find_peak(const vector<int>& a) { return int(max_element(a.begin(), a.end()) - a.begin()); }   // O(n)
int bitonic_search(const vector<int>& a, int x) { auto it = find(a.begin(), a.end(), x); return it == a.end() ? -1 : int(it - a.begin()); }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string cmd;
    while (cin >> cmd) {
        if (cmd == "peak") {
            int n; cin >> n; vector<int> a(n); for (auto& x : a) cin >> x;
            int p = find_peak(a);
            bool ok = p >= 0 && p < n && (p == 0 || a[p] > a[p - 1]) && (p == n - 1 || a[p] > a[p + 1]);
            cout << (ok ? "valid peak" : "INVALID") << '\n';
        } else {
            int n, q; cin >> n >> q; vector<int> a(n); for (auto& x : a) cin >> x;
            unsigned long long h = 0; int shown = 0;
            while (q--) { int x; cin >> x; int r = bitonic_search(a, x); bool ok = (r == -1) ? (n > 5000 || find(a.begin(), a.end(), x) == a.end()) : (r >= 0 && r < n && a[r] == x);
                int show = r == -1 ? -1 : 1; if (shown++ < 15) cout << show << ' '; h = h * 3 + (r != -1) + (ok ? 0 : 1000); }
            cout << "| " << h << '\n';
        }
    }
}
```

## Tests
=== sample
peak 4
1 2 3 1
peak 7
1 2 1 3 5 6 4
bit 6 3
1 3 8 12 4 2
4 12 5
---
valid peak
valid peak
1 1 -1 | 12
=== hidden
peak 1
5
peak 2
2 1
peak 2
1 2
bit 1 2
5
5 6
bit 3 3
3 2 1
1 2 4
---
valid peak
valid peak
valid peak
1 -1 | 3
1 1 -1 | 12
=== hidden
bit 5 5
1 3 5 4 2
4 2 5 1 3
bit 9 6
1 14 19 26 30 45 48 96 82
82 96 1 48 45 50
bit 2 2
1 9
9 1
bit 2 2
9 1
9 1
---
1 1 1 1 1 | 121
1 1 1 1 1 -1 | 363
1 1 | 4
1 1 | 4
=== hidden
bit 1 15
13
13 2 13 13 13 8 13 13 19 13 13 13 13 13 92
peak 10
1 6 5 3 5 4 2 1 0 4
peak 4
3 5 3 4
peak 3
2 1 5
---
1 -1 1 1 1 -1 1 1 -1 1 1 1 1 1 -1 | 5559717
valid peak
valid peak
valid peak
=== hidden
peak 6
0 4 1 2 6 5
peak 1
0
bit 2 15
39 83
39 39 83 47 83 23 83 39 26 83 39 101 83 50 39
bit 7 15
8 14 42 59 78 87 88
78 59 76 21 59 67 22 59 42 77 14 61 78 42 78
---
valid peak
valid peak
1 1 1 -1 1 -1 1 1 -1 1 1 -1 1 -1 1 | 6976864
1 1 -1 -1 1 -1 -1 1 1 -1 1 -1 1 1 1 | 6439351
=== hidden
bit 8 15
63 65 72 57 44 35 33 18
33 35 33 18 44 18 44 72 33 63 33 6 44 57 57
bit 9 15
1 3 12 24 66 68 71 92 16
26 80 3 72 68 16 71 74 69 12 66 1 86 71 12
bit 1 15
30
61 30 30 30 30 30 68 30 52 39 1 30 30 30 30
peak 6
4 0 3 2 3 1
---
1 1 1 1 1 1 1 1 1 1 1 -1 1 1 1 | 7174426
-1 -1 1 -1 1 1 1 -1 -1 1 1 1 -1 1 1 | 617089
-1 1 1 1 1 1 -1 1 -1 -1 -1 1 1 1 1 | 2383870
valid peak
=== hidden
@gen 4201209736 big
=== hidden
@gen 4201209737 big
=== hidden
@gen 4201209738 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(4 if not big else 2):
    n = r.randint(1, 10) if not big else 1000000
    if r.random() < 0.5:
        a = [r.randint(0, 5)]
        for _ in range(n - 1):
            v = r.randint(0, 5 if not big else 10**9)
            while v == a[-1]: v = r.randint(0, 6 if not big else 10**9)
            a.append(v)
        print("peak", n); print(*a)
    else:
        vals = sorted(r.sample(range(0, 100 if not big else 4 * 10**9, 1), n)) if not big else sorted(r.sample(range(0, 4 * 10**6), n))
        t = r.randint(0, n - 1); left = sorted(r.sample(vals, t + 1)) if n > 0 else []
        rest = sorted(set(vals) - set(left), reverse=True)
        a = left + [x for x in rest if x < left[-1]] if left else rest
        q = 15 if not big else 300000
        print("bit", len(a), q); print(*a); print(" ".join(str(r.choice(a) if r.random() < 0.6 else r.randint(-1, 101 if not big else 4 * 10**6)) for _ in range(q)))
```

## Hints
- Compare `a[mid]` with `a[mid+1]`. If the next value is bigger, some peak must lie to the right.
- That gives a "first index where a[i] > a[i+1]" search. The last index counts as a peak too.
- For the mountain array, find the summit, then search the ascending side normally and the descending side with the comparisons flipped.

## Solution
**Why binary search works without sortedness.** If `a[mid] < a[mid+1]`, walk right from `mid + 1`. Either the values eventually drop, and the last value before the drop is a peak, or they climb to the last index, which is a peak because the outside counts as −∞. Either way a peak exists in `(mid, hi]`. The symmetric argument covers `[lo, mid]`. So each step keeps a range that is **guaranteed to contain a peak**. That invariant replaces sortedness.

**Bitonic arrays** have exactly one peak (the summit). Splitting there gives two monotone arrays, each searched in O(log n). Note the reversed comparison on the descending side.

Complexity: O(log n) per call.

```cpp
#include <bits/stdc++.h>
using namespace std;

int find_peak(const vector<int>& a) {
    int lo = 0, hi = (int)a.size() - 1;
    while (lo < hi) {                                   // first i with a[i] > a[i+1] (or the last index)
        int mid = lo + (hi - lo) / 2;
        if (a[mid] < a[mid + 1]) lo = mid + 1;          // climbing: a peak lies to the right
        else hi = mid;                                  // descending: mid or something left is a peak
    }
    return lo;
}

int bitonic_search(const vector<int>& a, int x) {
    int top = find_peak(a);                             // in a mountain the peak is unique
    int lo = 0, hi = top;
    while (lo <= hi) {                                  // ascending part [0, top]
        int mid = lo + (hi - lo) / 2;
        if (a[mid] == x) return mid;
        if (a[mid] < x) lo = mid + 1; else hi = mid - 1;
    }
    lo = top + 1; hi = (int)a.size() - 1;
    while (lo <= hi) {                                  // descending part (top, n-1]
        int mid = lo + (hi - lo) / 2;
        if (a[mid] == x) return mid;
        if (a[mid] > x) lo = mid + 1; else hi = mid - 1;
    }
    return -1;
}
```
