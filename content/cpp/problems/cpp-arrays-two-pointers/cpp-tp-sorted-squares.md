---
id: cpp-tp-sorted-squares
title: Squares of a Sorted Array and Merging from the Back
difficulty: Easy
order: 3
tags: two pointers, merging, sorted arrays
time_limit: 2
---
## Statement
Two classic "fill from the end" problems:

```cpp
std::vector<long long> sorted_squares(const std::vector<int>& a);
    // a is sorted ascending (negatives allowed); return the squares sorted ascending, in O(n)
void merge_into(std::vector<int>& a, int m, const std::vector<int>& b);
    // a holds m sorted values followed by b.size() unused slots; b is sorted.
    // Merge b into a so that a is fully sorted. O(m + n) time, O(1) extra memory.
```

For the squares: the largest square is at **one of the two ends** (the most negative or the most positive value), so fill the output from the back with converging pointers. For the merge: filling `a` from the front would overwrite values you haven't read, but filling from the back is safe.

**Input:** cases until the end of input: `squares n` + values, or `merge m k` + `m` values + `k` values. n ≤ 10⁶.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

vector<long long> sorted_squares(const vector<int>& a) {
    vector<long long> r; for (int x : a) r.push_back(1LL * x * x); return r;   // not sorted
}
void merge_into(vector<int>& a, int m, const vector<int>& b) {
    for (size_t j = 0; j < b.size(); ++j) a[m + j] = b[j];                     // not merged
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string cmd;
    while (cin >> cmd) {
        long long h = 0; vector<long long> out;
        if (cmd == "squares") {
            int n; cin >> n; vector<int> a(n); for (auto& x : a) cin >> x;
            out = sorted_squares(a);
        } else {
            int m, k; cin >> m >> k;
            vector<int> a(m + k), b(k);
            for (int i = 0; i < m; ++i) cin >> a[i];
            for (auto& x : b) cin >> x;
            merge_into(a, m, b);
            out.assign(a.begin(), a.end());
        }
        for (auto x : out) h = (h * 31 + (x % 1000000007 + 1000000007)) % 1000000007;
        for (size_t i = 0; i < min<size_t>(out.size(), 12); ++i) cout << out[i] << ' ';
        cout << "| " << h << '\n';
    }
}
```

## Tests
=== sample
squares 5
-4 -1 0 3 10
merge 3 3
1 2 3
2 5 6
---
0 1 9 16 100 | 39036
1 2 2 3 5 6 | 30538819
=== hidden
squares 1
-7
merge 0 2
4 5
merge 2 0
1 9
squares 4
-3 -3 -2 -1
---
49 | 49
4 5 | 129
1 9 | 40
1 4 9 9 | 33923
=== hidden
merge 2 0
-6 5

squares 5
-5 -3 -2 1 9
merge 1 1
6
-3
squares 3
-9 -7 3
squares 5
-8 0 2 7 7
squares 2
0 4
---
-6 5 | 999999826
1 4 9 25 81 | 1052190
-3 6 | 999999920
9 49 81 | 10249
0 4 49 49 64 | 167836
0 16 | 16
=== hidden
squares 10
-10 -7 -5 -4 -3 -3 0 1 5 8
merge 3 2
-8 6 8
-8 -6
merge 3 5
-5 -1 -1
-8 -8 -5 -2 1
squares 2
-5 -5
merge 6 2
-3 2 3 6 9 9
-4 8
squares 10
-9 -2 -1 -1 2 4 5 6 8 9
---
0 1 9 9 16 25 25 49 64 100 | 974038202
-8 -8 -6 6 8 | 992367939
-8 -8 -5 -5 -2 -1 -1 1 | 651235327
25 25 | 800
-4 -3 2 3 6 8 9 9 | 347248891
1 1 4 4 16 25 36 64 81 81 | 595768451
=== hidden
merge 6 0
-9 -8 -6 -5 -2 9

squares 4
-10 -7 7 8
merge 2 1
1 7
-2
squares 2
4 10
squares 4
-9 -6 7 9
merge 6 3
-8 -5 -4 0 5 5
-5 -2 6
---
-9 -8 -6 -5 -2 9 | 734765876
49 49 64 100 | 1508932
-2 1 7 | 999998123
16 100 | 596
36 49 81 81 | 1122157
-8 -5 -5 -4 -2 0 5 5 6 | 754801594
=== hidden
@gen 3800089572 big
=== hidden
@gen 3800089573 big
=== hidden
@gen 3800089574 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 2):
    if r.random() < 0.5:
        n = r.randint(1, 10) if not big else 1000000
        print("squares", n); print(*sorted(r.randint(-10, 10) if not big else r.randint(-10**9, 10**9) for _ in range(n)))
    else:
        m = r.randint(0, 6) if not big else 500000; k = r.randint(0, 6) if not big else 500000
        print("merge", m, k); print(*sorted(r.randint(-9, 9) for _ in range(m))); print(*sorted(r.randint(-9, 9) for _ in range(k)))
```

## Hints
- Where is the largest square of a sorted array with negatives? It's at one of the ends.
- Fill the output from index `n−1` down, taking the bigger square from `L` or `R`.
- For the merge, start three indices at the ends (`m−1`, `k−1`, `m+k−1`) and write the larger value at the back. Stop when `b` is exhausted.

## Solution
**Squares.** A sorted array with negatives has squares that are large at both ends and small in the middle (a "valley"). So the largest remaining square is always at `L` or `R`. Write it at the next free slot from the back. Each element is placed once, so it's O(n), with no sorting needed.

**Merge from the back.** Slot `k` (the end of the free space) is never occupied by an unread value of `a`, because `k ≥ i` always holds. Writing there can't destroy anything. When `b` runs out, whatever remains of `a` is already in its sorted place, which is why the loop condition is only `j >= 0`.

Complexity: O(n) and O(m + k), with O(1) extra space for the merge.

```cpp
#include <bits/stdc++.h>
using namespace std;

vector<long long> sorted_squares(const vector<int>& a) {
    int n = a.size(), L = 0, R = n - 1;
    vector<long long> out(n);
    for (int k = n - 1; k >= 0; --k) {                 // biggest square first, written at the back
        long long l2 = 1LL * a[L] * a[L], r2 = 1LL * a[R] * a[R];
        if (l2 > r2) { out[k] = l2; ++L; }
        else { out[k] = r2; --R; }
    }
    return out;
}

void merge_into(vector<int>& a, int m, const vector<int>& b) {
    int i = m - 1, j = (int)b.size() - 1, k = m + (int)b.size() - 1;
    while (j >= 0) {                                   // once b is used up, a's prefix is already in place
        if (i >= 0 && a[i] > b[j]) a[k--] = a[i--];
        else a[k--] = b[j--];
    }
}
```
