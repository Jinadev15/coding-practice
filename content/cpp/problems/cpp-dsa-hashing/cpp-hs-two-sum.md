---
id: cpp-hs-two-sum
title: Two Sum and Pairs with Difference k
difficulty: Easy
order: 1
tags: hashing, complements, counting pairs
time_limit: 2
---
## Statement
The array is **not** sorted.

```cpp
std::pair<int,int> two_sum(const std::vector<int>& a, long long target);
    // indices i < j with a[i] + a[j] == target; among all such pairs return the one with the
    // SMALLEST j, and for that j the smallest i. {-1, -1} if none.
long long pairs_with_difference(const std::vector<int>& a, long long k);
    // number of index pairs i < j with |a[i] - a[j]| == k  (k >= 0)
```

Scan left to right. Before inserting `a[j]`, look up the complement `target − a[j]` among the elements already seen. Storing the **first** index of each value gives the smallest `i`.

For differences, an earlier `x` pairs with `a[j]` when `x = a[j] − k` or `x = a[j] + k`. When `k = 0`, those are the same value, so don't count it twice.

**Input:** cases until the end of input: `sum n target` or `diff n k`, followed by `n` values (n ≤ 10⁶, |a[i]| ≤ 10⁹).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

pair<int,int> two_sum(const vector<int>& a, long long target) {
    for (size_t j = 0; j < a.size(); ++j)
        for (size_t i = 0; i < j; ++i)
            if ((long long)a[i] + a[j] == target) return {(int)i, (int)j};
    return {-1, -1};
}
long long pairs_with_difference(const vector<int>& a, long long k) { return 0; }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string cmd; int n; long long t;
    while (cin >> cmd >> n >> t) {
        vector<int> a(n);
        for (auto& x : a) cin >> x;
        if (cmd == "sum") { auto [i, j] = two_sum(a, t); cout << i << ' ' << j << '\n'; }
        else cout << pairs_with_difference(a, t) << '\n';
    }
}
```

## Tests
=== sample
sum 4 9
2 7 11 15
sum 3 6
3 2 4
diff 5 2
1 5 3 4 2
---
0 1
1 2
3
=== hidden
sum 1 2
1
sum 2 6
3 3
diff 4 0
1 1 1 1
diff 3 1000000000
-1000000000 0 1000000000
---
-1 -1
0 1
6
2
=== hidden
sum 6 -7
2 -2 0 5 5 -2
sum 8 -3
5 -5 3 1 3 1 1 -3
diff 8 1
4 -1 -4 1 -1 -3 -2 3
diff 7 1
4 4 -4 3 0 -2 5
sum 8 -3
0 2 -2 0 -6 4 -5 -2
sum 7 0
-3 -3 -1 3 -4 -3 -5
---
-1 -1
-1 -1
5
4
1 6
0 3
=== hidden
sum 7 -3
4 0 0 5 2 -6 -4
diff 10 4
2 -4 0 -1 0 -5 1 4 0 -6
sum 5 8
4 0 4 5 4
sum 2 2
5 1
sum 2 -10
1 2
sum 9 2
5 0 -6 1 -4 2 -3 0 1
---
-1 -1
7
0 2
-1 -1
-1 -1
1 5
=== hidden
sum 5 8
5 1 1 -4 3
diff 1 4
4
sum 10 -7
2 5 4 -4 5 -1 3 2 -6 -5
sum 3 -8
2 -2 -5
diff 3 4
-4 4 -3
diff 4 1
3 3 2 4
---
0 4
0
5 8
-1 -1
0
4
=== hidden
@gen 1870194982 big
=== hidden
@gen 1870194983 big
=== hidden
@gen 1870194984 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 2):
    n = r.randint(1, 10) if not big else 1000000
    a = [r.randint(-6, 6) if not big else r.randint(-10**9, 10**9) % 200000 for _ in range(n)]
    if r.random() < 0.5: print("sum", n, r.randint(-10, 10) if not big else r.randint(0, 400000))
    else: print("diff", n, r.randint(0, 4) if not big else r.randint(0, 50))
    print(*a)
```

## Hints
- For each element, which value would complete the pair? Look it up among the elements you've already seen.
- Store the first index of each value, and check for the complement before inserting the current element.
- For differences, count the earlier occurrences of `x − k` and `x + k`, which are the same thing when `k = 0`.

## Solution
**Complement lookup.** For each `j`, the partner must equal `target − a[j]`. A hash map from value to earliest index answers "did I see it, and where first?" in O(1) expected. The first `j` with any partner is the smallest `j`, and the stored first index is the smallest `i` for it.

Checking **before** inserting prevents an element from pairing with itself (for example `a[j] = 3` and `target = 6`).

**Difference counting.** Count, for each element, how many earlier elements are exactly `k` below or above it. Counting only earlier elements makes each pair count once (as `i < j`). For `k = 0` the two complements coincide, so do one lookup. Otherwise every equal pair would count twice.

The counts reach about n²/2 when many values repeat, so use `long long`.

Complexity: O(n) expected for both.

```cpp
#include <bits/stdc++.h>
using namespace std;

pair<int,int> two_sum(const vector<int>& a, long long target) {
    unordered_map<long long, int> first;              // value -> first index seen
    first.reserve(a.size() * 2 + 1);
    for (int j = 0; j < (int)a.size(); ++j) {
        auto it = first.find(target - a[j]);          // check the complement BEFORE inserting a[j]
        if (it != first.end()) return {it->second, j};
        first.try_emplace(a[j], j);                   // keep the earliest index of each value
    }
    return {-1, -1};
}

long long pairs_with_difference(const vector<int>& a, long long k) {
    unordered_map<long long, long long> cnt;
    cnt.reserve(a.size() * 2 + 1);
    long long pairs = 0;
    for (int x : a) {
        auto f = [&](long long v) { auto it = cnt.find(v); return it == cnt.end() ? 0LL : it->second; };
        pairs += f((long long)x - k);
        if (k != 0) pairs += f((long long)x + k);     // k == 0: both lookups are the same value
        ++cnt[x];
    }
    return pairs;
}
```
