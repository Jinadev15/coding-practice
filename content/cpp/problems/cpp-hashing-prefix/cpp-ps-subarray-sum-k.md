---
id: cpp-ps-subarray-sum-k
title: Subarray Sum Equals K (Negatives Allowed)
difficulty: Medium
order: 4
tags: prefix sums, hashing, counting subarrays
time_limit: 2
---
## Statement
```cpp
long long count_sum_k(const std::vector<int>& a, long long k);   // number of subarrays with sum exactly k
int longest_sum_k(const std::vector<int>& a, long long k);       // length of the longest such subarray (0 if none)
```

Values can be **negative**, so a sliding window doesn't work here.

A subarray `(l, r]` has sum `P[r] − P[l]`. You want `P[l] = P[r] − k`. While scanning, keep a hash map of how many times each prefix value has appeared (for counting), or the **first** index where it appeared (for the longest subarray). Seed it with the empty prefix: value 0, count 1, at index −1.

**Input:** cases until the end of input: `n k` + n values (n ≤ 10⁶, |a[i]| ≤ 10⁴).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

long long count_sum_k(const vector<int>& a, long long k) {
    long long c = 0;
    for (size_t i = 0; i < a.size(); ++i) { long long s = 0; for (size_t j = i; j < a.size(); ++j) { s += a[j]; if (s == k) ++c; } }
    return c;
}
int longest_sum_k(const vector<int>& a, long long k) { return 0; }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n; long long k;
    while (cin >> n >> k) {
        vector<int> a(n);
        for (auto& x : a) cin >> x;
        cout << count_sum_k(a, k) << ' ' << longest_sum_k(a, k) << '\n';
    }
}
```

## Tests
=== sample
3 2
1 1 1
5 3
1 -1 5 -2 3
---
2 2
3 4
=== hidden
1 0
0
4 0
0 0 0 0
3 10
1 2 3
6 0
1 -1 1 -1 1 -1
---
1 1
10 4
0 0
9 6
=== hidden
1 -2
2
5 0
2 -3 -3 3 -2
11 0
2 3 2 -2 0 3 -3 -3 1 -1 0
3 -2
2 -1 -2
10 0
-1 1 -1 0 0 2 -1 -1 1 -1
1 -3
-3
---
0 0
1 2
12 10
1 1
21 9
1 1
=== hidden
8 -4
1 2 2 1 -2 -1 1 1
8 -2
-3 1 2 -1 -3 -3 -3 0
2 -4
-2 2
6 -3
1 -3 3 2 1 0
6 -4
-2 -3 0 -3 1 -3
4 0
0 2 1 -3
---
0 0
2 3
0 0
1 1
0 0
3 4
=== hidden
5 4
0 1 1 0 2
12 4
3 1 -1 0 2 1 0 0 -1 1 3 1
12 -3
2 0 -1 -3 2 -3 3 3 2 1 -2 2
1 1
3
6 -3
-1 2 -2 -2 -2 -2
9 1
1 1 1 2 3 -3 1 3 1
---
2 5
7 6
3 6
0 0
1 4
7 3
=== hidden
@gen 2317651531 big
=== hidden
@gen 2317651532 big
=== hidden
@gen 2317651533 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 1):
    n = r.randint(1, 12) if not big else 1000000
    print(n, r.randint(-4, 4) if not big else r.randint(-50, 50)); print(*[r.randint(-3, 3) if not big else r.randint(-10, 10) for _ in range(n)])
```

## Hints
- `sum(l..r) = P[r+1] − P[l]`, so you're looking for earlier prefixes equal to `current − k`.
- Keep `unordered_map<long long,long long>` counts of the prefix values seen so far, seeded with `{0: 1}`. Look up before inserting.
- For the longest subarray, store the first index of each prefix value (seed `0 → −1`), and never overwrite it.

## Solution
**Counting.** For each end `r`, the subarrays ending at `r` with sum `k` correspond one-to-one with earlier prefixes equal to `P[r] − k`. The map accumulates the counts of the prefixes seen so far. Query *before* inserting the current prefix, so a zero-length subarray can't count itself when `k = 0`.

**Longest.** For the longest subarray ending at `r`, you want the *earliest* `l` with `P[l] = P[r] − k`. Store each prefix value's first occurrence only. `try_emplace` does nothing if the key already exists.

The empty prefix `(0 → count 1 / index −1)` represents "start from the beginning". Without it, subarrays that start at index 0 are missed.

Complexity: O(n) expected time, O(n) space.

```cpp
#include <bits/stdc++.h>
using namespace std;

long long count_sum_k(const vector<int>& a, long long k) {
    unordered_map<long long, long long> seen;
    seen.reserve(a.size() * 2 + 1);
    seen[0] = 1;                                   // the empty prefix
    long long pre = 0, cnt = 0;
    for (int x : a) {
        pre += x;
        auto it = seen.find(pre - k);              // earlier prefixes that complete a sum of k
        if (it != seen.end()) cnt += it->second;
        ++seen[pre];                               // insert AFTER querying
    }
    return cnt;
}

int longest_sum_k(const vector<int>& a, long long k) {
    unordered_map<long long, int> first;
    first.reserve(a.size() * 2 + 1);
    first[0] = -1;
    long long pre = 0; int best = 0;
    for (int i = 0; i < (int)a.size(); ++i) {
        pre += a[i];
        auto it = first.find(pre - k);
        if (it != first.end()) best = max(best, i - it->second);
        first.try_emplace(pre, i);                 // keep the EARLIEST index only
    }
    return best;
}
```
