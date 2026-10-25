---
id: cpp-pair-sum-count
title: Counting Pair Sums Under a Time Limit
difficulty: Easy
order: 2
tags: complexity, constraints, sorting, hashing
time_limit: 1
---
## Statement
Count the pairs of positions `i < j` with `a[i] + a[j] == k`.

```cpp
long long count_pairs(const std::vector<int>& a, long long k);
```

The starter code is correct, but it checks every pair: **O(n²)**. With n up to 2·10⁵ that's 2·10¹⁰ checks, far too slow for the 1-second limit. Use the constraints table from the lesson to choose a better complexity, then implement it.

**Input:** either `n k` followed by `n` integers, or a line `gen n seed maxv k`, in which case the driver generates `n` values in `[-maxv, maxv]`. There are several cases until the end of input, and you print one answer per case.

Constraints: n ≤ 2·10⁵, |a[i]| ≤ 10⁹, |k| ≤ 2·10⁹. The answer can exceed 2³¹.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

long long count_pairs(const vector<int>& a, long long k) {
    long long c = 0;
    for (size_t i = 0; i < a.size(); ++i)
        for (size_t j = i + 1; j < a.size(); ++j)
            if ((long long)a[i] + a[j] == k) ++c;
    return c;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string first;
    while (cin >> first) {
        vector<int> a; long long k;
        if (first == "gen") {
            int n; unsigned long long seed; long long maxv;
            cin >> n >> seed >> maxv >> k;
            mt19937_64 rng(seed);
            a.resize(n);
            for (auto& x : a) x = (int)((long long)(rng() % (2 * maxv + 1)) - maxv);
        } else {
            int n = stoi(first); cin >> k;
            a.resize(n);
            for (auto& x : a) cin >> x;
        }
        cout << count_pairs(a, k) << '\n';
    }
}
```

## Tests
=== sample
5 6
1 5 3 3 7
4 4
2 2 2 2
---
2
6
=== hidden
1 2
1
---
0
=== hidden
0 5
---
0
=== hidden
6 0
-3 3 0 0 -3 3
---
5
=== hidden
gen 200000 7 1000000000 12345
---
11
=== hidden
gen 200000 9 3 0
---
2857178714
=== hidden
gen 200000 11 0 0
---
19999900000
=== hidden
3 10
-2 -3 1
---
0
=== hidden
5 -3
2 1 -1 1 1
---
0
=== hidden
11 1756
-215 -290 -11 990 835 557 -982 679 966 986 570
---
0
=== hidden
gen 200000 126432455 1000 -7
---
9956300
=== hidden
gen 200000 512902307 5 5
---
985724470
=== hidden
gen 200000 306208117 1000 5
---
9975287

## Hints
- n = 2·10⁵ means you need about O(n log n). An O(n²) loop can't pass.
- Sort the values. Now the smallest and largest elements tell you which way to move.
- Be careful with duplicates: count equal runs at both ends, and handle the case where the two ends hold the same value.

## Solution
**Sort, then walk two pointers.** After sorting, put `i` at the smallest value and `j` at the largest.

- If `v[i] + v[j] < k`, the sum must grow, and only moving `i` right can do that.
- If the sum is too big, move `j` left.
- When the sum equals `k`, duplicates matter. A run of `x` repeated `li` times on the left and `k − x` repeated `rj` times on the right gives `li · rj` pairs. If `v[i] == v[j]`, every pair inside the window works, which gives `m(m−1)/2` pairs.

An `unordered_map` that counts the values seen so far also works in expected O(n). Sorting is deterministic, though, and can't be slowed down by hash collisions.

Complexity: O(n log n) time, O(n) space for the copy.

```cpp
#include <bits/stdc++.h>
using namespace std;

long long count_pairs(const vector<int>& a, long long k) {
    vector<long long> v(a.begin(), a.end());
    sort(v.begin(), v.end());                       // O(n log n)
    long long c = 0;
    size_t i = 0, j = v.size();
    if (j == 0) return 0;
    --j;
    while (i < j) {                                 // O(n) two-pointer walk
        long long s = v[i] + v[j];
        if (s < k) ++i;
        else if (s > k) --j;
        else if (v[i] == v[j]) {                    // every pair inside [i, j] works
            long long m = (long long)(j - i + 1);
            c += m * (m - 1) / 2;
            break;
        } else {                                    // count equal runs on both ends
            long long li = 1, rj = 1;
            while (i + 1 < j && v[i + 1] == v[i]) ++i, ++li;
            while (j - 1 > i && v[j - 1] == v[j]) --j, ++rj;
            c += li * rj;
            ++i; --j;
        }
    }
    return c;
}
```
