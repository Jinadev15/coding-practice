---
id: cpp-kd-circular-max
title: Maximum Circular Subarray Sum
difficulty: Medium
order: 2
tags: Kadane, circular arrays, complement trick
time_limit: 2
---
## Statement
The array is **circular**: after the last element comes the first again. A subarray may wrap around, but it can use each element at most once.

```cpp
long long max_circular(const std::vector<int>& a);   // best non-empty circular subarray sum
long long min_subarray(const std::vector<int>& a);   // smallest non-empty (non-circular) subarray sum
```

`[5, −3, 5]` gives 10 (wrap: 5 + 5). `[−3, −2, −3]` gives −2.

A wrapping subarray = everything **except** a middle block. So the best wrapping sum is `total − (minimum subarray)`. The answer is `max(normal Kadane, total − min subarray)`, but if **all** elements are negative, the second option would mean taking nothing, so use plain Kadane then.

**Input:** cases until the end of input: `n` + values (n ≤ 10⁶, |a[i]| ≤ 10⁹).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

long long max_circular(const vector<int>& a) {
    long long cur = a[0], best = a[0];
    for (size_t i = 1; i < a.size(); ++i) { cur = max<long long>(a[i], cur + a[i]); best = max(best, cur); }
    return best;                                   // ignores wrap-around
}
long long min_subarray(const vector<int>& a) { return 0; }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n;
    while (cin >> n) {
        vector<int> a(n);
        for (auto& x : a) cin >> x;
        cout << max_circular(a) << ' ' << min_subarray(a) << '\n';
    }
}
```

## Tests
=== sample
3
5 -3 5
3
-3 -2 -3
4
1 -2 3 -2
---
10 -3
-2 -8
3 -2
=== hidden
1
7
2
-1 -1
5
3 -1 2 -1 4
5
-2 4 -5 4 -5
---
7 7
-1 -2
8 -1
4 -6
=== hidden
8
2 -5 2 -3 -2 -3 -4 5
9
2 -1 2 -4 3 -1 0 0 1
2
5 -2
9
-3 -4 -2 -1 -1 0 -5 -1 0
8
3 -2 -5 -3 3 5 4 2
3
2 -2 5
---
7 -15
6 -4
5 -2
0 -17
17 -10
7 -2
=== hidden
5
-2 -4 1 -2 5
5
4 -2 0 3 -5
5
0 -2 1 0 5
7
-3 4 1 -1 1 5 0
8
-3 -5 -2 5 5 1 -4 2
5
-2 5 5 3 0
---
5 -7
5 -5
6 -2
10 -3
11 -10
13 -2
=== hidden
2
1 1
5
4 1 0 2 -5
1
-3
2
4 2
3
4 2 -3
3
-5 -1 5
---
2 1
7 -5
-3 -3
6 2
6 -3
5 -6
=== hidden
@gen 2364711878 big
=== hidden
@gen 2364711879 big
=== hidden
@gen 2364711880 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 1):
    n = r.randint(1, 9) if not big else 1000000
    print(n); print(*[r.randint(-5, 5) if not big else r.randint(-10**9, 10**9) for _ in range(n)])
```

## Hints
- A subarray that wraps around consists of a prefix and a suffix. What is left out?
- The left-out part is a contiguous middle block, so maximise `total − (that block)` by finding the minimum subarray.
- Handle the case where all values are negative separately.

## Solution
Any circular subarray either doesn't cross the boundary, which Kadane finds, or it does. A crossing subarray is a prefix plus a suffix, which equals the total minus a contiguous **middle** block. Maximising it means minimising the removed block: `total − min_subarray` (Kadane with `min`).

**The exception:** if every element is negative, the minimum subarray is the whole array, and `total − min = 0` would represent the empty subarray, which isn't allowed. In that case `best < 0`, so return it directly. If `best ≥ 0`, removing the whole array gives 0 ≤ best, so it never wins incorrectly.

Complexity: O(n) time, O(1) space.

```cpp
#include <bits/stdc++.h>
using namespace std;

long long min_subarray(const vector<int>& a) {
    long long cur = a[0], best = a[0];
    for (size_t i = 1; i < a.size(); ++i) { cur = min<long long>(a[i], cur + a[i]); best = min(best, cur); }
    return best;
}

long long max_circular(const vector<int>& a) {
    long long cur = a[0], best = a[0], total = 0;
    for (size_t i = 1; i < a.size(); ++i) { cur = max<long long>(a[i], cur + a[i]); best = max(best, cur); }
    for (int x : a) total += x;
    if (best < 0) return best;                      // all negative: wrapping would take nothing
    return max(best, total - min_subarray(a));      // non-wrapping vs. wrapping (drop the worst middle)
}
```
