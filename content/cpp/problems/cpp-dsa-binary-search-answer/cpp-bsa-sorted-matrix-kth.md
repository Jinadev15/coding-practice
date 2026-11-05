---
id: cpp-bsa-sorted-matrix-kth
title: k-th Smallest in a Sorted Matrix and Row-Sorted Median
difficulty: Medium
order: 5
tags: binary search on value, staircase counting, upper_bound
time_limit: 2
---
## Statement
```cpp
long long kth_sorted_matrix(const std::vector<std::vector<long long>>& m, long long k);
    // rows AND columns sorted ascending (n x n); k-th smallest (1-based)
long long median_row_sorted(const std::vector<std::vector<long long>>& m);
    // only each ROW is sorted; R*C is odd; the median of all entries
```

Both are "binary search on the value plus a fast count":

- **Sorted matrix:** count the entries `≤ v` with a **staircase** walk from the bottom-left, O(n) per count.
- **Row-sorted:** count with `upper_bound` in every row, O(R log C) per count. The median is the smallest `v` with `count(v) ≥ (R·C + 1) / 2`.

**Input:** cases until the end of input: `kth n k` + an n×n matrix, or `med R C` + the matrix (cells ≤ 10⁶ for kth, R·C ≤ 10⁶; values up to ±10⁹).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

long long kth_sorted_matrix(const vector<vector<long long>>& m, long long k) { vector<long long> a; for (auto& r : m) a.insert(a.end(), r.begin(), r.end()); sort(a.begin(), a.end()); return a[k - 1]; }
long long median_row_sorted(const vector<vector<long long>>& m) { return m[m.size() / 2][m[0].size() / 2]; }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string cmd;
    while (cin >> cmd) {
        if (cmd == "kth") {
            int n; long long k; cin >> n >> k;
            vector<vector<long long>> m(n, vector<long long>(n));
            for (auto& r : m) for (auto& x : r) cin >> x;
            cout << kth_sorted_matrix(m, k) << '\n';
        } else {
            int R, C; cin >> R >> C;
            vector<vector<long long>> m(R, vector<long long>(C));
            for (auto& r : m) for (auto& x : r) cin >> x;
            cout << median_row_sorted(m) << '\n';
        }
    }
}
```

## Tests
=== sample
kth 3 8
1 5 9
10 11 13
12 13 15
med 3 3
1 3 5
2 6 9
3 6 9
---
13
5
=== hidden
kth 1 1
-5
med 1 1
7
med 1 5
-3 -1 0 4 4
kth 2 3
-2 -1
-1 0
---
-5
7
0
-1
=== hidden
kth 3 2
-500000000 -499999999 -499999997
-499999999 -499999996 -499999995
-499999997 -499999995 -499999995
med 3 3
-6 0 7
-2 -1 2
4 6 9
kth 3 7
-499999997 -499999996 -499999995
-499999997 -499999995 -499999992
-499999994 -499999994 -499999992
kth 4 9
-499999999 -499999997 -499999994 -499999994
-499999998 -499999996 -499999993 -499999991
-499999997 -499999993 -499999991 -499999989
-499999995 -499999990 -499999990 -499999989
---
-499999999
2
-499999994
-499999993
=== hidden
med 5 3
-1 0 9
-9 -3 3
-5 -4 4
-7 3 5
-8 2 9
kth 4 15
-500000000 -499999999 -499999999 -499999996
-499999997 -499999997 -499999994 -499999994
-499999994 -499999992 -499999990 -499999990
-499999994 -499999990 -499999990 -499999990
kth 4 12
-499999997 -499999997 -499999997 -499999996
-499999995 -499999995 -499999993 -499999990
-499999994 -499999993 -499999992 -499999988
-499999994 -499999991 -499999988 -499999986
med 5 5
-4 -2 1 2 7
0 1 3 7 8
-9 1 2 4 9
-8 -6 -3 1 9
-9 -2 3 6 9
---
0
-499999990
-499999991
1
=== hidden
med 1 3
-8 0 9
kth 1 1
-500000000
med 1 1
-4
med 5 3
-1 0 5
-7 1 4
-5 3 6
-6 5 7
-3 3 5
---
0
-500000000
-4
3
=== hidden
@gen 3617175523 big
=== hidden
@gen 3617175524 big
=== hidden
@gen 3617175525 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(4 if not big else 2):
    if r.random() < 0.5:
        n = r.randint(1, 5) if not big else 1000
        m = [[0]*n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                base = max(m[i-1][j] if i else -10**9 // 2, m[i][j-1] if j else -10**9 // 2)
                m[i][j] = base + r.randint(0, 3 if not big else 1000)
        print("kth", n, r.randint(1, n * n))
        for row in m: print(*row)
    else:
        R = r.randint(1, 5) if not big else 999; C = r.randint(1, 5) if not big else 1001
        R |= 1; C |= 1                       # the median needs an odd number of cells
        print("med", R, C)
        for _ in range(R): print(*sorted(r.randint(-9, 9) if not big else r.randint(-10**9, 10**9) for _ in range(C)))
```

## Hints
- Selection via counting: the k-th smallest is the smallest v with count(≤ v) ≥ k.
- Rows and columns sorted: count with a staircase walk from the bottom-left corner.
- Only rows sorted: count with upper_bound in each row. The median needs count ≥ (R·C+1)/2.

## Solution
Both reduce **selection** (find the k-th) to **counting** (how many are ≤ v), which is monotone in `v`. The binary search ranges over **values**, so the number of iterations depends on the value range (about 31 for ±10⁹), not on the matrix size.

- With rows **and** columns sorted, the staircase counts in O(n): each step either takes a whole column segment or drops a row.
- With only rows sorted, each row is counted with `upper_bound`, which is O(R log C) per iteration.

The minimum and maximum come from the corners or row ends, giving tight starting bounds. `lo + (hi − lo)/2` stays correct for negative values. Plain `(lo + hi) / 2` would round toward zero and can misbehave with negative bounds, as well as overflow.

Complexity: O(n log V) and O(R log C log V).

```cpp
#include <bits/stdc++.h>
using namespace std;

long long kth_sorted_matrix(const vector<vector<long long>>& m, long long k) {
    int n = m.size();
    auto count_le = [&](long long v) {                   // staircase from the bottom-left
        long long c = 0; int r = n - 1, col = 0;
        while (r >= 0 && col < n) {
            if (m[r][col] <= v) { c += r + 1; ++col; }
            else --r;
        }
        return c;
    };
    long long lo = m[0][0], hi = m[n - 1][n - 1];
    while (lo < hi) {
        long long mid = lo + (hi - lo) / 2;              // values may be negative: still no overflow
        if (count_le(mid) >= k) hi = mid; else lo = mid + 1;
    }
    return lo;
}

long long median_row_sorted(const vector<vector<long long>>& m) {
    long long lo = LLONG_MAX, hi = LLONG_MIN, R = m.size(), C = m[0].size();
    for (auto& row : m) { lo = min(lo, row.front()); hi = max(hi, row.back()); }
    long long need = (R * C + 1) / 2;
    while (lo < hi) {
        long long mid = lo + (hi - lo) / 2, c = 0;
        for (auto& row : m) c += upper_bound(row.begin(), row.end(), mid) - row.begin();
        if (c >= need) hi = mid; else lo = mid + 1;
    }
    return lo;
}
```
