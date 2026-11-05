---
id: cpp-bs-median-two-arrays
title: Median of Two Sorted Arrays
difficulty: Hard
order: 7
tags: binary search, partitioning, divide and conquer
time_limit: 2
---
## Statement
Given two sorted arrays `A` (size n) and `B` (size m), find the k-th smallest element of their union, and the median, in **O(log(min(n, m)))** time, without merging.

```cpp
long long kth_of_two(const std::vector<int>& A, const std::vector<int>& B, long long k);   // 1-based k
double median_of_two(const std::vector<int>& A, const std::vector<int>& B);                // n + m >= 1
```

**Partition idea.** Choose how many elements `i` to take from A and `j = k − i` from B. The choice is right when `A[i−1] ≤ B[j]` and `B[j−1] ≤ A[i]`, using −∞ and +∞ off the ends. If `A[i−1] > B[j]`, you took too many from A, so decrease `i`. Otherwise increase it. Binary search on `i`.

The median is the `((n+m+1)/2)`-th element, or the average of the two middle elements when `n + m` is even. Print it with one decimal.

**Input:** `n m`, A, B, `q`, then q values of k, repeated as cases until the end of input (n, m ≤ 10⁶, q ≤ 10⁵).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

long long kth_of_two(const vector<int>& A, const vector<int>& B, long long k) {
    vector<int> c; merge(A.begin(), A.end(), B.begin(), B.end(), back_inserter(c)); return c[k - 1];   // O(n+m) per call
}
double median_of_two(const vector<int>& A, const vector<int>& B) {
    long long t = A.size() + B.size();
    return t % 2 ? kth_of_two(A, B, t / 2 + 1) : (kth_of_two(A, B, t / 2) + kth_of_two(A, B, t / 2 + 1)) / 2.0;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n, m;
    while (cin >> n >> m) {
        vector<int> A(n), B(m);
        for (auto& x : A) cin >> x;
        for (auto& x : B) cin >> x;
        int q; cin >> q;
        unsigned long long h = 0; int shown = 0;
        while (q--) { long long k; cin >> k; long long r = kth_of_two(A, B, k); if (shown++ < 10) cout << r << ' '; h = h * 1000003 + (unsigned long long)r; }
        cout << fixed << setprecision(1) << "| " << h << " | median " << median_of_two(A, B) << '\n';
    }
}
```

## Tests
=== sample
2 1
1 3
2
3
1 2 3
2 2
1 2
3 4
2
1 4
---
1 2 3 | 1000008000018 | median 2.0
1 4 | 1000007 | median 2.5
=== hidden
0 1

5
1
1
3 3
1 1 1
1 1 1
3
1 3 6
1 0
-7

1
1
---
5 | 5 | median 5.0
1 1 1 | 1000007000013 | median 1.0
-7 | 18446744073709551609 | median -7.0
=== hidden
6 4
-3 -3 -2 0 3 3
-4 -3 1 4
6
9 8 4 5 1 4
6 4
-4 -4 -1 -1 0 3
-1 1 2 3
6
9 4 6 8 3 7
3 0
-4 3 4

6
3 1 2 2 2 3
1 4
-4
-2 -1 3 4
6
3 2 4 4 5 5
---
3 3 -3 -2 -4 -3 | 8584088040678694874 | median -1.0
3 -1 0 2 -1 1 | 10909078440655762968 | median -0.5
4 -4 3 3 3 4 | 4797608805068028289 | median 3.0
-1 -2 3 3 4 4 | 15879412904045457767 | median -1.0
=== hidden
1 0
-4

6
1 1 1 1 1 1
1 1
-1
3
6
1 1 1 1 1 1
5 0
-5 2 3 4 4

6
4 3 3 1 5 5
2 6
-2 -2
-4 0 0 0 2 5
6
7 1 4 3 1 1
---
-4 -4 -4 -4 -4 -4 | 11299044068345659216 | median -4.0
-1 -1 -1 -1 -1 -1 | 7436447035513802708 | median 1.0
4 3 3 -5 4 4 | 10590607873677547187 | median 3.0
2 -4 0 -2 -4 -4 | 9784639139256323840 | median 0.0
=== hidden
0 4

-4 4 5 5
6
2 2 3 2 1 2
2 3
-1 0
-5 -2 4
6
2 5 4 3 2 2
2 3
-5 -2
-4 -4 -2
6
3 2 3 4 5 3
1 5
1
-3 -2 3 5 5
6
1 5 2 1 1 3
---
4 4 5 4 -4 4 | 8147709005382892403 | median 4.5
-2 4 0 -1 -2 -2 | 8662101934429227725 | median -1.0
-4 -4 -4 -2 -2 -4 | 11299046068359659240 | median -4.0
-3 5 -2 -3 -3 1 | 6212687233120720611 | median 2.0
=== hidden
@gen 221543640 big
=== hidden
@gen 221543641 big
=== hidden
@gen 221543642 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(4 if not big else 1):
    n = r.randint(0, 6) if not big else 1000000; m = r.randint(0 if n else 1, 6) if not big else 1000000
    A = sorted(r.randint(-5, 5) if not big else r.randint(-10**9, 10**9) for _ in range(n))
    B = sorted(r.randint(-5, 5) if not big else r.randint(-10**9, 10**9) for _ in range(m))
    q = 6 if not big else 100000
    print(n, m); print(*A); print(*B); print(q); print(*[r.randint(1, n + m) for _ in range(q)])
```

## Hints
- The k smallest elements are a prefix of A (length i) plus a prefix of B (length k − i).
- The split is valid when A[i−1] ≤ B[k−i] and B[k−i−1] ≤ A[i]. Treat out-of-range values as −∞/+∞.
- Binary search i over [max(0, k−m), min(k, n)]: if A[i−1] > B[j], decrease i, otherwise increase it.

## Solution
**The k smallest elements of the union** consist of some prefix `A[0..i)` and some prefix `B[0..j)` with `i + j = k`. The split is correct exactly when nothing on the left side is bigger than anything on the right side, which means checking the two "crossing" pairs: `A[i−1] ≤ B[j]` and `B[j−1] ≤ A[i]`.

If `A[i−1] > B[j]`, a too-big A element is on the left, so `i` must shrink. If `B[j−1] > A[i]`, `i` must grow. These moves are monotone in `i`, so binary search finds the split in `O(log min(n, m))`. The k-th element is then the largest of the two left boundary values.

The valid range of `i` is `[max(0, k−m), min(k, n)]`, because `j` must stay within `0..m`. Sentinels (−∞/+∞) handle empty prefixes and suffixes without special cases.

Complexity: O(log min(n, m)) per query.

```cpp
#include <bits/stdc++.h>
using namespace std;

long long kth_of_two(const vector<int>& A, const vector<int>& B, long long k) {
    if (A.size() > B.size()) return kth_of_two(B, A, k);          // binary search over the smaller array
    long long n = A.size(), m = B.size();
    long long lo = max(0LL, k - m), hi = min(k, n);               // i = how many come from A
    const long long NEG = LLONG_MIN, POS = LLONG_MAX;
    while (lo <= hi) {
        long long i = lo + (hi - lo) / 2, j = k - i;
        long long aL = i > 0 ? A[i - 1] : NEG, aR = i < n ? A[i] : POS;
        long long bL = j > 0 ? B[j - 1] : NEG, bR = j < m ? B[j] : POS;
        if (aL > bR) hi = i - 1;                                  // took too many from A
        else if (bL > aR) lo = i + 1;                             // took too few from A
        else return max(aL, bL);                                  // valid split: the k-th is the larger left max
    }
    return -1;                                                    // unreachable for valid k
}

double median_of_two(const vector<int>& A, const vector<int>& B) {
    long long t = (long long)A.size() + B.size();
    if (t % 2) return (double)kth_of_two(A, B, t / 2 + 1);
    return (kth_of_two(A, B, t / 2) + kth_of_two(A, B, t / 2 + 1)) / 2.0;
}
```
