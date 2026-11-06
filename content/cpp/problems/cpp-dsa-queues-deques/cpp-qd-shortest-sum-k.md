---
id: cpp-qd-shortest-sum-k
title: Shortest Subarray with Sum at Least K (Negatives Allowed)
difficulty: Hard
order: 8
tags: deque, monotonic deque, prefix sums
time_limit: 1
---
## Statement
```cpp
int shortest_at_least(const std::vector<int>& a, long long K);   // length of the shortest non-empty
                                                                 // subarray with sum >= K, or -1
```

Values can be **negative**, so the two-pointer sliding window does not work (adding an element can lower the sum).

- `[2, -1, 2]`, K = 3 → **3**. `[1, 2]`, K = 4 → **−1**. `[84, -37, 32, 40, 95]`, K = 167 → **3** (32 + 40 + 95).

Required: **O(n)** with a monotonic deque over prefix sums.

**Input:** cases until the end of input: `n K`, then `n` values (1 ≤ n ≤ 10⁶ in total, |a[i]| ≤ 10⁹, 1 ≤ K ≤ 10¹⁵).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

int shortest_at_least(const vector<int>& a, long long K) {
    return -1;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n; long long K;
    while (cin >> n >> K) {
        vector<int> a(n); for (auto& x : a) cin >> x;
        cout << shortest_at_least(a, K) << '\n';
    }
}
```

## Tests
=== sample
3 3
2 -1 2
2 4
1 2
5 167
84 -37 32 40 95
---
3
-1
3
=== hidden
1 5
5
1 6
5
4 10
10 -100 4 6
5 3
-1 -1 3 -1 -1
6 1000000000000
1000000000 -1 1000000000 1000000000 -1000000000 1000000000
4 7
4 -2 -2 7
---
1
-1
1
1
-1
1
=== hidden
8 3
-5 5 -2 2 4 1 2 3
4 7
-5 4 -4 2
7 6
-3 -1 4 -1 2 -4 2
5 10
5 3 3 4 -5
1 4
-4
7 10
1 1 -3 1 -1 -4 3
5 3
-1 5 -4 2 6
2 3
-2 1
---
1
-1
-1
3
-1
-1
1
-1
=== hidden
3 3
3 -2 4
4 4
-1 -3 5 1
7 2
0 6 -2 2 -4 -5 4
7 1
3 -2 -2 1 -1 0 -3
4 11
4 6 -5 -4
6 3
-3 3 -2 0 -1 -1
5 2
6 0 6 -1 6
5 12
-2 0 -1 -5 -1
---
1
1
1
1
-1
1
1
-1
=== hidden
2 2
3 3
2 6
5 1
9 4
2 -4 4 -2 5 -5 -5 1 6
7 4
2 1 -2 6 6 0 3
5 10
4 4 2 -4 1
8 1
-1 -2 -1 -4 1 -4 -4 2
3 5
0 4 5
3 2
2 5 4
---
1
2
1
1
3
1
1
1
=== hidden
@gen 3784424282 big
=== hidden
@gen 3784424283 big
=== hidden
@gen 3784424284 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(8 if not big else 1):
    n = r.randint(1, 10) if not big else 1000000
    if big:
        a = [r.randint(-10**9, 10**9) for _ in range(n)]
        K = r.choice([10**12, 3 * 10**12, 10**15])
    else:
        a = [r.randint(-5, 6) for _ in range(n)]; K = r.randint(1, 12)
    print(n, K); print(*a)
```

## Hints
- Rewrite subarray sums as differences of prefix sums: you need `P[j] − P[i] ≥ K` with `j − i` minimal.
- If `i1 < i2` and `P[i1] ≥ P[i2]`, the start `i1` is never better than `i2`. Drop it.
- Once a start satisfies the condition for some `j`, later ends only make it longer: record the length and pop it from the front.

## Solution
With prefix sums `P`, the subarray `a[i..j−1]` has sum `P[j] − P[i]`. We want the smallest `j − i` with `P[j] − P[i] ≥ K`.

Process `j = 0 … n`, keeping a deque of **candidate start indices** `i`. Two pruning rules make it monotonic:

1. **Front: a start is used up.** If `P[j] − P[front] ≥ K`, record `j − front` and pop the front. Any later `j` would give that start a *longer* subarray, so it can never do better.
2. **Back: a start is dominated.** If `P[back] ≥ P[j]`, then `j` is a better start than `back` for every future end: it is later (shorter) and its prefix is lower (bigger sum). Pop `back`.

After rule 2, the prefix values in the deque increase from front to back, so rule 1 only ever needs to look at the front.

```text
a = 2 -1 2, K = 3      P = 0 2 1 3
j=0 P=0: deque [0]
j=1 P=2: 2-0 < 3; push         [0 1]
j=2 P=1: pop 1 (P=2 >= 1)      [0 2]
j=3 P=3: 3-0 >= 3 -> len 3, pop 0; 3-1 < 3; push   [2 3]   answer 3
```

With only non-negative values, the prefix sums are already increasing and this reduces to the ordinary sliding window. Use `long long` for prefix sums (up to 10¹⁵).

Each index enters and leaves the deque once: O(n).

```cpp
#include <bits/stdc++.h>
using namespace std;

int shortest_at_least(const vector<int>& a, long long K) {
    int n = a.size();
    vector<long long> P(n + 1, 0);                  // P[i] = a[0] + ... + a[i-1]
    for (int i = 0; i < n; ++i) P[i + 1] = P[i] + a[i];
    deque<int> dq;                                  // candidate starts, P increasing front to back
    int best = INT_MAX;
    for (int j = 0; j <= n; ++j) {
        while (!dq.empty() && P[j] - P[dq.front()] >= K) {   // best possible end for this start
            best = min(best, j - dq.front());
            dq.pop_front();
        }
        while (!dq.empty() && P[dq.back()] >= P[j]) dq.pop_back();   // j is a later AND lower start
        dq.push_back(j);
    }
    return best == INT_MAX ? -1 : best;
}
```
