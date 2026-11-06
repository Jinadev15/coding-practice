---
id: cpp-merge-sort-trace
title: Merge Sort and Its Comparisons
difficulty: Medium
order: 2
tags: sorting, merge sort, divide and conquer, stability
time_limit: 2
---
## Statement
Implement top-down merge sort:

```cpp
long long merge_sort(std::vector<int>& a, std::vector<std::string>& trace);
```

Follow these rules exactly, because the outputs depend on them:

- Sort the half-open range `[l, r)`. If `r − l ≤ 1`, return. Otherwise `m = l + (r − l) / 2`: sort `[l, m)`, then `[m, r)`, then merge.
- When merging, compare the front elements of the two halves, and take from the **left** half when they are equal (this is what makes it stable). Count **one comparison** each time you compare two elements. Copying the leftovers costs nothing.
- When `n ≤ 16`, after each merge append `"[l,r) v1 v2 ..."` with the merged values to `trace`.
- Return the total number of comparisons.

Allocate the temporary buffer **once** and reuse it. Allocating inside every call is a common performance bug.

**Input:** cases until the end of input: `n` followed by `n` integers (n ≤ 10⁶).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

long long merge_sort(vector<int>& a, vector<string>& trace) {
    sort(a.begin(), a.end());
    return 0;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n;
    while (cin >> n) {
        vector<int> a(n);
        for (auto& x : a) cin >> x;
        vector<string> trace;
        long long c = merge_sort(a, trace);
        for (auto& t : trace) cout << t << '\n';
        bool ok = is_sorted(a.begin(), a.end());
        long long h = 0;
        for (int i = 0; i < n; ++i) h = (h * 31 + a[i] + 1000000000LL) % 1000000007;
        cout << "comparisons: " << c << (ok ? " sorted" : " NOT sorted") << " checksum " << h << '\n';
    }
}
```

## Tests
=== sample
7
38 27 43 3 9 82 10
---
[1,3) 27 43
[0,3) 27 38 43
[3,5) 3 9
[5,7) 10 82
[3,7) 3 9 10 82
[0,7) 3 9 10 27 38 43 82
comparisons: 13 sorted checksum 510640971
=== hidden
1
5
2
2 1
8
1 2 3 4 5 6 7 8
8
8 7 6 5 4 3 2 1
6
3 3 3 3 3 3
---
comparisons: 0 sorted checksum 1000000005
[0,2) 1 2
comparisons: 1 sorted checksum 999999816
[0,2) 1 2
[2,4) 3 4
[0,4) 1 2 3 4
[4,6) 5 6
[6,8) 7 8
[4,8) 5 6 7 8
[0,8) 1 2 3 4 5 6 7 8
comparisons: 12 sorted checksum 369450410
[0,2) 7 8
[2,4) 5 6
[0,4) 5 6 7 8
[4,6) 3 4
[6,8) 1 2
[4,8) 1 2 3 4
[0,8) 1 2 3 4 5 6 7 8
comparisons: 12 sorted checksum 369450410
[1,3) 3 3
[0,3) 3 3 3
[4,6) 3 3
[3,6) 3 3 3
[0,6) 3 3 3 3 3 3
comparisons: 7 sorted checksum 881666183
=== hidden
16
0 9 -3 6 5 -3 9 0 -7 0 -3 7 -7 -7 -1 -6
17
17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1
---
[0,2) 0 9
[2,4) -3 6
[0,4) -3 0 6 9
[4,6) -3 5
[6,8) 0 9
[4,8) -3 0 5 9
[0,8) -3 -3 0 0 5 6 9 9
[8,10) -7 0
[10,12) -3 7
[8,12) -7 -3 0 7
[12,14) -7 -7
[14,16) -6 -1
[12,16) -7 -7 -6 -1
[8,16) -7 -7 -7 -6 -3 -1 0 7
[0,16) -7 -7 -7 -6 -3 -3 -3 -1 0 0 0 5 6 7 9 9
comparisons: 46 sorted checksum 178821583
comparisons: 37 sorted checksum 101394004
=== hidden
7
-9 8 2 3 1 -3 -5
10
-4 2 2 2 8 -1 9 7 -9 -6
5
6 0 6 -3 -2
1
7
---
[1,3) 2 8
[0,3) -9 2 8
[3,5) 1 3
[5,7) -5 -3
[3,7) -5 -3 1 3
[0,7) -9 -5 -3 1 2 3 8
comparisons: 12 sorted checksum 446972513
[0,2) -4 2
[3,5) 2 8
[2,5) 2 2 8
[0,5) -4 2 2 2 8
[5,7) -1 9
[8,10) -9 -6
[7,10) -9 -6 7
[5,10) -9 -6 -1 7 9
[0,10) -9 -6 -4 -1 2 2 2 7 8 9
comparisons: 22 sorted checksum 578286604
[0,2) 0 6
[3,5) -3 -2
[2,5) -3 -2 6
[0,5) -3 -2 0 6 6
comparisons: 8 sorted checksum 990489919
comparisons: 0 sorted checksum 0
=== hidden
15
-4 -7 -1 -2 2 3 -3 9 1 -4 5 6 9 -9 -2
13
3 5 -9 -2 -9 -9 -4 5 -5 -4 8 -5 -7
12
6 0 7 -8 -4 8 -6 7 9 0 -5 -1
2
-8 6
---
[1,3) -7 -1
[0,3) -7 -4 -1
[3,5) -2 2
[5,7) -3 3
[3,7) -3 -2 2 3
[0,7) -7 -4 -3 -2 -1 2 3
[7,9) 1 9
[9,11) -4 5
[7,11) -4 1 5 9
[11,13) 6 9
[13,15) -9 -2
[11,15) -9 -2 6 9
[7,15) -9 -4 -2 1 5 6 9 9
[0,15) -9 -7 -4 -4 -3 -2 -2 -1 1 2 3 5 6 9 9
comparisons: 40 sorted checksum 737605079
[1,3) -9 5
[0,3) -9 3 5
[4,6) -9 -9
[3,6) -9 -9 -2
[0,6) -9 -9 -9 -2 3 5
[7,9) -5 5
[6,9) -5 -4 5
[9,11) -4 8
[11,13) -7 -5
[9,13) -7 -5 -4 8
[6,13) -7 -5 -5 -4 -4 5 8
[0,13) -9 -9 -9 -7 -5 -5 -4 -4 -2 3 5 5 8
comparisons: 34 sorted checksum 967515747
[1,3) 0 7
[0,3) 0 6 7
[4,6) -4 8
[3,6) -8 -4 8
[0,6) -8 -4 0 6 7 8
[7,9) 7 9
[6,9) -6 7 9
[10,12) -5 -1
[9,12) -5 -1 0
[6,12) -6 -5 -1 0 7 9
[0,12) -8 -6 -5 -4 -1 0 0 6 7 7 8 9
comparisons: 30 sorted checksum 785835440
[0,2) -8 6
comparisons: 1 sorted checksum 999999541
=== hidden
1
-7
12
0 7 0 -1 4 -3 -8 -5 8 -7 7 5
15
0 1 2 -8 -4 8 7 -6 -7 5 8 -2 -1 -3 -8
5
0 3 -1 -7 -8
---
comparisons: 0 sorted checksum 999999993
[1,3) 0 7
[0,3) 0 0 7
[4,6) -3 4
[3,6) -3 -1 4
[0,6) -3 -1 0 0 4 7
[7,9) -5 8
[6,9) -8 -5 8
[10,12) 5 7
[9,12) -7 5 7
[6,12) -8 -7 -5 5 7 8
[0,12) -8 -7 -5 -3 -1 0 0 4 5 7 7 8
comparisons: 29 sorted checksum 393716849
[1,3) 1 2
[0,3) 0 1 2
[3,5) -8 -4
[5,7) 7 8
[3,7) -8 -4 7 8
[0,7) -8 -4 0 1 2 7 8
[7,9) -7 -6
[9,11) 5 8
[7,11) -7 -6 5 8
[11,13) -2 -1
[13,15) -8 -3
[11,15) -8 -3 -2 -1
[7,15) -8 -7 -6 -3 -2 -1 5 8
[0,15) -8 -8 -7 -6 -4 -3 -2 -1 0 1 2 5 7 8 8
comparisons: 39 sorted checksum 322099895
[0,2) 0 3
[3,5) -8 -7
[2,5) -8 -7 -1
[0,5) -8 -7 -1 0 3
comparisons: 7 sorted checksum 985722209
=== hidden
@gen 2719491700 big
=== hidden
@gen 2719491701 big
=== hidden
@gen 2719491702 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
if sys.argv[2] == "small":
    for _ in range(4):
        n = r.randint(0, 16); print(n); print(*[r.randint(-9, 9) for _ in range(n)])
else:
    n = 1000000; print(n); print(" ".join(str(r.randint(-10**9, 10**9)) for _ in range(n)))
```

## Hints
- Recursion on `[l, r)`: stop when `r − l ≤ 1`, split at `m = l + (r − l)/2`.
- During the merge, increment the counter once per comparison of two elements, and take the right element only if it is **strictly** smaller.
- Copy the merged range from the buffer back into `a` before recording the trace line.

## Solution
**Divide:** split at the midpoint. **Conquer:** sort both halves recursively. **Combine:** merge.

Each merge of `k` elements makes at most `k − 1` comparisons, and every level of the recursion handles all `n` elements. There are `log₂ n` levels, so the total is O(n log n) comparisons and moves, in **every** case. That guarantee is the reason to choose merge sort over quicksort.

Taking from the left half on ties keeps equal elements in their original order. Swap the condition to `a[j] <= a[i]` and the sort becomes unstable.

The single `tmp` buffer makes the extra space O(n) overall. Allocating a fresh vector per call is O(n log n) allocations' worth of work.

Complexity: Θ(n log n) time, O(n) extra space.

```cpp
#include <bits/stdc++.h>
using namespace std;

static long long comps;

static void msort(vector<int>& a, vector<int>& tmp, int l, int r, vector<string>& trace) {
    if (r - l <= 1) return;
    int m = l + (r - l) / 2;
    msort(a, tmp, l, m, trace);
    msort(a, tmp, m, r, trace);
    int i = l, j = m, k = l;
    while (i < m && j < r) {
        ++comps;
        if (a[j] < a[i]) tmp[k++] = a[j++];     // strictly smaller on the right: take it
        else tmp[k++] = a[i++];                 // ties go left: stable
    }
    while (i < m) tmp[k++] = a[i++];
    while (j < r) tmp[k++] = a[j++];
    copy(tmp.begin() + l, tmp.begin() + r, a.begin() + l);
    if (a.size() <= 16) {
        string s = "[" + to_string(l) + "," + to_string(r) + ")";
        for (int t = l; t < r; ++t) s += " " + to_string(a[t]);
        trace.push_back(s);
    }
}

long long merge_sort(vector<int>& a, vector<string>& trace) {
    comps = 0;
    vector<int> tmp(a.size());                  // one buffer for the whole sort
    msort(a, tmp, 0, (int)a.size(), trace);
    return comps;
}
```
