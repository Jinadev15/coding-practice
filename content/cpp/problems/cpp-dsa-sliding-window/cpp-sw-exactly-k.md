---
id: cpp-sw-exactly-k
title: Counting Subarrays with Exactly K Distinct Values
difficulty: Hard
order: 5
tags: sliding window, counting, at-most trick, hashing
time_limit: 2
---
## Statement
```cpp
long long count_exactly_k(const std::vector<int>& a, int K);   // subarrays with EXACTLY K distinct values
long long count_k_odd(const std::vector<int>& a, int K);       // subarrays with exactly K odd numbers ("nice subarrays")
```

"Exactly K" isn't monotone: extending a window can push the count from K to K+1, and shrinking can take it from K to K−1. So no single window works. But **"at most K" is monotone**, and

**exactly(K) = atMost(K) − atMost(K − 1)**

For `atMost`, after shrinking for each `R`, all `R − L + 1` subarrays ending at `R` qualify.

`[1,2,1,2,3]` with K = 2 gives 7 subarrays: [1,2], [2,1], [1,2], [2,3], [1,2,1], [2,1,2], [1,2,1,2].

**Input:** cases until the end of input: `distinct n K` or `odd n K`, followed by values (1 ≤ a[i] ≤ n ≤ 10⁶).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

long long count_exactly_k(const vector<int>& a, int K) { return 0; }
long long count_k_odd(const vector<int>& a, int K) { return 0; }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string cmd; int n, K;
    while (cin >> cmd >> n >> K) {
        vector<int> a(n);
        for (auto& x : a) cin >> x;
        cout << (cmd == "distinct" ? count_exactly_k(a, K) : count_k_odd(a, K)) << '\n';
    }
}
```

## Tests
=== sample
distinct 5 2
1 2 1 2 3
odd 5 3
1 1 2 1 1
---
7
2
=== hidden
distinct 1 1
1
distinct 3 0
1 2 3
odd 3 0
2 4 6
odd 4 5
1 1 1 1
distinct 5 5
1 2 3 4 5
---
1
0
6
0
1
=== hidden
odd 6 1
5 1 2 4 1 2
odd 11 4
5 5 3 2 4 5 3 5 3 5 5
odd 2 0
1 2
odd 4 1
4 1 3 1
odd 4 2
4 1 1 2
odd 5 3
4 4 1 4 5
---
10
8
1
4
4
0
=== hidden
odd 12 0
2 3 1 1 5 1 1 1 1 1 3 4
distinct 12 3
2 2 3 2 5 4 5 3 1 5 5 1
odd 5 3
3 2 3 2 3
odd 12 4
3 1 3 1 3 4 2 2 5 1 3 4
odd 2 2
1 1
distinct 8 2
5 5 1 1 5 4 1 1
---
2
14
1
9
1
11
=== hidden
odd 6 0
5 3 3 5 1 4
odd 11 2
4 2 4 2 4 3 4 1 2 1 5
odd 10 0
4 5 5 1 5 2 2 1 2 1
odd 10 0
2 1 1 5 2 3 2 3 4 2
distinct 6 0
1 2 2 4 2 5
odd 2 0
1 1
---
1
16
5
6
0
0
=== hidden
@gen 1778458529 big
=== hidden
@gen 1778458530 big
=== hidden
@gen 1778458531 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 2):
    n = r.randint(1, 12) if not big else 1000000
    print(r.choice(["distinct", "odd"]), n, r.randint(0, 4) if not big else r.randint(1, 300)); print(*[r.randint(1, min(n, 5)) if not big else r.randint(1, 1000) for _ in range(n)])
```

## Hints
- Can you count subarrays with **at most** K distinct values with a window? For each R, how many valid starts are there?
- exactly(K) = atMost(K) − atMost(K−1).
- The same trick works for "exactly K odd numbers": only the quantity the window tracks changes.

## Solution
**The at-most trick.** Every subarray with at most K distinct values has either exactly K or at most K−1. Subtracting the two monotone counts leaves exactly K.

Each `atMost` is a standard counting window: after shrinking, the valid starts for end `R` are exactly `L..R`, so add `R − L + 1`. `atMost(−1)` is 0, which handles `K = 0` correctly.

The "nice subarrays" version is the same idea with a different measure (the number of odd elements instead of distinct values). Recognising that the *measure* is interchangeable is the real skill here.

The answers can reach n²/2 ≈ 5·10¹¹, so use `long long`.

Complexity: O(n) per call.

```cpp
#include <bits/stdc++.h>
using namespace std;

static long long at_most_distinct(const vector<int>& a, int K) {
    if (K < 0) return 0;
    vector<int> cnt(a.size() + 2, 0);                  // values are 1..n
    long long res = 0; int distinct = 0, L = 0;
    for (int R = 0; R < (int)a.size(); ++R) {
        if (cnt[a[R]]++ == 0) ++distinct;
        while (distinct > K) if (--cnt[a[L++]] == 0) --distinct;
        res += R - L + 1;                              // every start in [L, R] works
    }
    return res;
}

long long count_exactly_k(const vector<int>& a, int K) {
    return at_most_distinct(a, K) - at_most_distinct(a, K - 1);
}

static long long at_most_odd(const vector<int>& a, int K) {
    if (K < 0) return 0;
    long long res = 0; int odd = 0, L = 0;
    for (int R = 0; R < (int)a.size(); ++R) {
        odd += a[R] & 1;
        while (odd > K) odd -= a[L++] & 1;
        res += R - L + 1;
    }
    return res;
}

long long count_k_odd(const vector<int>& a, int K) { return at_most_odd(a, K) - at_most_odd(a, K - 1); }
```
