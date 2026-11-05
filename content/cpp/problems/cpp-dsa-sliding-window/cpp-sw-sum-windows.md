---
id: cpp-sw-sum-windows
title: Longest and Shortest Windows by Sum
difficulty: Medium
order: 3
tags: sliding window, monotonicity, non-negative arrays
time_limit: 2
---
## Statement
The values are **non-negative**, which is what makes sum windows monotone.

```cpp
int longest_at_most(const std::vector<int>& a, long long S);    // longest subarray with sum <= S (0 if none)
int shortest_at_least(const std::vector<int>& a, long long S);  // shortest subarray with sum >= S (0 if none)
long long count_at_most(const std::vector<int>& a, long long S);// number of subarrays with sum <= S
```

- **Longest ≤ S:** after adding `a[R]`, shrink while the sum exceeds `S`. Then the window is valid.
- **Shortest ≥ S:** after adding `a[R]`, **while** the sum is still ≥ S, record the length and shrink.
- **Count ≤ S:** after shrinking, every subarray ending at `R` and starting in `[L, R]` is valid, so add `R − L + 1`.

**Input:** cases until the end of input: `n S` + n values (0 ≤ a[i] ≤ 10⁹, n ≤ 10⁶).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

int longest_at_most(const vector<int>& a, long long S) { return 0; }
int shortest_at_least(const vector<int>& a, long long S) { return 0; }
long long count_at_most(const vector<int>& a, long long S) { return 0; }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n; long long S;
    while (cin >> n >> S) {
        vector<int> a(n);
        for (auto& x : a) cin >> x;
        cout << longest_at_most(a, S) << ' ' << shortest_at_least(a, S) << ' ' << count_at_most(a, S) << '\n';
    }
}
```

## Tests
=== sample
6 7
2 3 1 2 4 3
5 4
1 4 4 1 1
---
3 2 14
2 1 6
=== hidden
1 0
0
1 5
6
4 100
1 2 3 4
5 0
0 0 1 0 0
---
1 1 1
0 1 0
4 0 10
2 1 6
=== hidden
5 0
0 1 4 3 4
7 0
0 5 0 1 4 3 0
1 1
0
4 14
6 6 1 5
9 1
3 3 3 0 4 5 2 1 1
4 0
1 1 6 1
---
1 1 1
1 1 3
1 0 1
3 4 9
1 1 3
0 1 0
=== hidden
3 5
5 6 5
3 6
2 0 4
6 -1
2 2 5 3 4 4
5 10
1 4 3 2 0
10 11
6 5 3 0 5 1 2 0 2 1
1 0
6
---
1 1 2
3 3 6
0 1 0
5 4 15
7 2 39
0 1 0
=== hidden
5 13
4 3 2 2 6
9 15
0 0 4 6 6 5 3 2 6
2 4
6 6
2 4
0 5
2 5
6 1
5 15
3 5 3 4 1
---
4 4 14
4 3 23
0 1 0
1 1 1
1 1 1
4 4 14
=== hidden
@gen 4071776078 big
=== hidden
@gen 4071776079 big
=== hidden
@gen 4071776080 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 1):
    n = r.randint(1, 10) if not big else 1000000
    a = [r.randint(0, 6) if not big else r.randint(0, 10**9) for _ in range(n)]
    print(n, r.randint(-1, 15) if not big else r.randint(0, 10**14)); print(*a)
```

## Hints
- Non-negative values mean that growing the window only increases the sum. That makes shrinking from the left safe.
- For the shortest window, record the length **inside** the shrinking loop, before removing `a[L]`.
- For counting, after shrinking, add the number of valid starting points for this `R`: `R − L + 1`.

## Solution
With non-negative numbers, extending a window never decreases the sum, and shrinking never increases it. That monotonicity is what makes all three windows correct.

- **Longest ≤ S:** sub-windows of a valid window are valid, so after shrinking to validity, `[L, R]` is the longest valid window ending at `R`.
- **Shortest ≥ S:** super-windows of a valid window are valid. Shrink while still valid, recording at each step. The last valid window before the sum drops below `S` is the shortest ending at `R`. The `L <= R` guard handles `S ≤ 0`, where even the empty window is "valid".
- **Counting:** for each `R`, the valid starts form the contiguous range `[L, R]`.

If `S < a[R]` (or `S` is negative), the shrink loop empties the window completely (`L = R + 1`), which correctly contributes 0. The `L <= R` guard stops it from reading past `R`.

Complexity: O(n) each.

```cpp
#include <bits/stdc++.h>
using namespace std;

int longest_at_most(const vector<int>& a, long long S) {
    long long sum = 0; int L = 0, best = 0;
    for (int R = 0; R < (int)a.size(); ++R) {
        sum += a[R];
        while (L <= R && sum > S) sum -= a[L++];   // restore validity (may empty the window)
        best = max(best, R - L + 1);
    }
    return best;
}

int shortest_at_least(const vector<int>& a, long long S) {
    long long sum = 0; int L = 0, best = INT_MAX;
    for (int R = 0; R < (int)a.size(); ++R) {
        sum += a[R];
        while (L <= R && sum >= S) {           // valid: record, then try shorter
            best = min(best, R - L + 1);
            sum -= a[L++];
        }
    }
    return best == INT_MAX ? 0 : best;
}

long long count_at_most(const vector<int>& a, long long S) {
    long long sum = 0, cnt = 0; int L = 0;
    for (int R = 0; R < (int)a.size(); ++R) {
        sum += a[R];
        while (L <= R && sum > S) sum -= a[L++];
        cnt += R - L + 1;                      // starts L..R all work for this end
    }
    return cnt;
}
```
