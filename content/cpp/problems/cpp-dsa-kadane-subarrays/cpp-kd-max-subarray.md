---
id: cpp-kd-max-subarray
title: Maximum Subarray (Kadane) with Its Position
difficulty: Easy
order: 1
tags: Kadane, dynamic programming, arrays
time_limit: 2
---
## Statement
```cpp
std::tuple<long long, int, int> max_subarray(const std::vector<int>& a);
    // {best sum, l, r} over NON-EMPTY subarrays a[l..r]; on ties choose the smallest l, then the smallest r
```

Use Kadane's algorithm: `cur = max(a[i], cur + a[i])`, and remember where the current run started.

**Tie rule details:** when `cur + a[i] == a[i]` (the carried prefix sums to exactly 0), keep **extending**. The longer run starts earlier, which gives the smaller `l`. Only replace the best when the new sum is **strictly** greater. Ties in `l` then resolve to the smallest `r` automatically. Think about why.

**Input:** cases until the end of input: `n` + values (n ≤ 10⁶, |a[i]| ≤ 10⁹).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

tuple<long long, int, int> max_subarray(const vector<int>& a) {
    long long best = LLONG_MIN; int bl = 0, br = 0;
    for (size_t l = 0; l < a.size(); ++l) {
        long long s = 0;
        for (size_t r = l; r < a.size(); ++r) { s += a[r]; if (s > best) { best = s; bl = l; br = r; } }
    }
    return {best, bl, br};
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
        auto [s, l, r] = max_subarray(a);
        cout << s << ' ' << l << ' ' << r << '\n';
    }
}
```

## Tests
=== sample
9
-2 1 -3 4 -1 2 1 -5 4
3
-3 -1 -2
---
6 3 6
-1 1 1
=== hidden
1
-5
4
0 0 0 0
5
2 -2 2 -2 2
6
-1 0 3 -3 3 0
---
-5 0 0
0 0 0
2 0 0
3 1 2
=== hidden
9
4 -2 -1 -3 -3 -1 1 0 -1
5
3 4 -1 2 0
6
1 -4 2 -2 -1 2
9
1 2 4 2 -3 1 -2 1 -1
3
1 0 4
10
1 -2 0 -2 3 3 2 -1 -4 2
---
4 0 0
8 0 3
2 2 2
9 0 3
5 0 2
8 4 6
=== hidden
3
0 -4 1
3
4 0 0
10
4 2 1 4 4 3 1 1 4 -2
9
3 2 -4 -2 -2 -2 4 4 -1
3
1 -3 -1
8
-1 1 1 -4 0 2 -2 -1
---
1 2 2
4 0 0
24 0 8
8 6 7
1 0 0
2 1 2
=== hidden
2
-2 4
6
2 -2 -4 4 1 -1
1
-4
10
2 -4 4 -4 -4 -3 -4 -3 -1 -4
10
1 0 4 4 1 -2 -3 -3 -3 -1
3
-4 1 0
---
4 1 1
5 3 4
-4 0 0
4 2 2
10 0 4
1 1 1
=== hidden
@gen 2653189521 big
=== hidden
@gen 2653189522 big
=== hidden
@gen 2653189523 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 1):
    n = r.randint(1, 10) if not big else 1000000
    print(n); print(*[r.randint(-4, 4) if not big else r.randint(-10**9, 10**9) for _ in range(n)])
```

## Hints
- Keep `cur`, the best sum ending at the current index, and the index where that run started.
- When `cur` is negative, start a new run at `i`. Otherwise extend.
- Update the overall best only when `cur` is strictly larger, to keep the earliest answer.

## Solution
`cur` is the best sum of a subarray ending at `i`, and `start` is where that subarray begins.

- If the carried sum is **negative**, dropping it strictly helps.
- If it is **non-negative**, extending is at least as good, and keeps the earlier start.

That implements `max(a[i], cur + a[i])` with the required tie-breaking.

The best is replaced only on a **strictly** greater sum. So among equal sums the first one found wins, which has the smallest right end for the run that started earliest. Every subarray is "the best ending at its right end" or worse, so scanning every `i` covers all candidates.

Complexity: O(n) time, O(1) space.

```cpp
#include <bits/stdc++.h>
using namespace std;

tuple<long long, int, int> max_subarray(const vector<int>& a) {
    long long cur = a[0], best = a[0];
    int start = 0, bl = 0, br = 0;
    for (int i = 1; i < (int)a.size(); ++i) {
        if (cur < 0) { cur = a[i]; start = i; }      // a negative prefix only hurts: start fresh
        else cur += a[i];                            // cur >= 0: extending is at least as good (and earlier)
        if (cur > best) { best = cur; bl = start; br = i; }
    }
    return {best, bl, br};
}
```
