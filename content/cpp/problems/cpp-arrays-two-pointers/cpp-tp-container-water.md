---
id: cpp-tp-container-water
title: Container With Most Water
difficulty: Medium
order: 6
tags: two pointers, greedy, elimination argument
time_limit: 2
---
## Statement
Vertical walls stand at positions `0..n−1` with heights `h[i]`. Pick two walls `L < R`. Together with the ground they hold `min(h[L], h[R]) × (R − L)` units of water.

```cpp
long long max_container(const std::vector<int>& h);           // the maximum amount of water
long long max_container_k_apart(const std::vector<int>& h, int k);
    // the same, but the two walls must be at least k positions apart (R - L >= k); -1 if impossible
```

n ≥ 2, n ≤ 10⁶, h[i] ≤ 10⁹. Checking every pair is O(n²), so do both in O(n).

For the second function, the converging scan still works: stop as soon as the walls get closer than `k`. Think about why discarding the shorter wall stays safe when there is a minimum width.

**Input:** cases until the end of input: `n k` + heights. Print both answers.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

long long max_container(const vector<int>& h) {
    long long best = 0;
    for (size_t i = 0; i < h.size(); ++i)
        for (size_t j = i + 1; j < h.size(); ++j) best = max(best, 1LL * min(h[i], h[j]) * (long long)(j - i));
    return best;
}
long long max_container_k_apart(const vector<int>& h, int k) { return -1; }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n, k;
    while (cin >> n >> k) {
        vector<int> h(n);
        for (auto& x : h) cin >> x;
        cout << max_container(h) << ' ' << max_container_k_apart(h, k) << '\n';
    }
}
```

## Tests
=== sample
9 1
1 8 6 2 5 4 8 3 7
9 7
1 8 6 2 5 4 8 3 7
---
49 49
49 49
=== hidden
2 1
1 1
2 2
5 5
3 1
5 5 5
6 6
3 1 2 2 1 3
---
1 1
5 -1
10 10
15 -1
=== hidden
9 6
4 1 6 0 4 1 4 1 2
8 2
6 4 3 2 6 2 1 6
8 7
4 3 0 3 0 5 6 4
7 2
0 2 0 3 2 2 1
5 3
0 6 2 6 5
4 1
3 5 3 3
---
24 24
42 42
28 28
8 8
15 15
9 9
=== hidden
6 1
3 4 5 2 0 0
10 7
1 0 0 1 2 1 1 5 4 4
6 5
1 6 2 3 3 6
4 1
2 2 1 1
5 4
0 1 0 2 0
7 2
5 6 6 6 2 1 3
---
6 6
10 9
24 5
3 3
2 0
18 18
=== hidden
2 3
2 5
9 4
2 0 4 3 1 6 3 1 0
6 3
5 1 6 2 3 0
2 1
4 6
5 2
6 0 3 5 6
9 10
0 2 6 6 3 1 2 6 6
---
2 -1
12 12
12 12
4 4
24 24
36 -1
=== hidden
@gen 2616947141 big
=== hidden
@gen 2616947142 big
=== hidden
@gen 2616947143 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 1):
    n = r.randint(2, 10) if not big else 1000000
    k = r.randint(1, n + 1) if not big else r.randint(1, n)
    print(n, k); print(*[r.randint(0, 6) if not big else r.randint(0, 10**9) for _ in range(n)])
```

## Hints
- Start with the widest container. Which wall limits the area?
- Moving the taller wall inward can never help: the width shrinks and the height stays capped by the shorter wall.
- For the minimum-width version, run the same scan and stop when `R − L < k`.

## Solution
The area is limited by the **shorter** wall. Say `h[L] ≤ h[R]`. Every other container that uses wall `L` has its partner strictly inside `(L, R)`, so it is **narrower** and still **no taller** than `h[L]`. So `L` has already achieved its best possible area, and it can be discarded (`++L`). Symmetrically, discard `R` when it is the shorter one. Each step removes one wall that can't beat what has been recorded, so the scan never misses the optimum, and it takes n−1 steps.

**Minimum width k.** The same argument holds, because every container that uses the discarded wall is narrower, and a narrower container also has a smaller (or equal) width ≥ k. Once `R − L < k`, every remaining pair is too narrow, so stop.

Note: the scan finds the maximum **area**, but it doesn't necessarily visit every pair that achieves it. That's fine here, because only the value is asked for.

Complexity: O(n) time, O(1) space.

```cpp
#include <bits/stdc++.h>
using namespace std;

long long max_container(const vector<int>& h) {
    int L = 0, R = (int)h.size() - 1;
    long long best = 0;
    while (L < R) {
        best = max(best, 1LL * min(h[L], h[R]) * (R - L));
        if (h[L] < h[R]) ++L;            // the shorter wall can't do better with any narrower partner
        else --R;
    }
    return best;
}

long long max_container_k_apart(const vector<int>& h, int k) {
    int L = 0, R = (int)h.size() - 1;
    long long best = -1;
    while (R - L >= k && L < R) {
        best = max(best, 1LL * min(h[L], h[R]) * (R - L));
        if (h[L] < h[R]) ++L; else --R;
    }
    return best;
}
```
