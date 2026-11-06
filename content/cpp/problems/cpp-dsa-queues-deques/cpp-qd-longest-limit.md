---
id: cpp-qd-longest-limit
title: Longest Subarray with Max - Min at Most L
difficulty: Medium
order: 6
tags: deque, monotonic deque, sliding window, two pointers
time_limit: 1
---
## Statement
```cpp
std::pair<int,int> longest_within(const std::vector<int>& a, long long L);
    // {length, start} of the longest contiguous subarray with max - min <= L; smallest start on ties
```

`a = [8, 2, 4, 7]`, `L = 4` → `{2, 1}` (`[2, 4]`; `[4, 7]` also has length 2 but starts later). `a = [10, 1, 2, 4, 7, 2]`, `L = 5` → `{4, 2}` (`[2, 4, 7, 2]`).

The window is variable-size, so you need the max **and** the min of a window that shrinks from the left. Use **two monotonic deques**. O(n).

**Input:** cases until the end of input: `n L`, then `n` values (1 ≤ n ≤ 10⁶ in total, |a[i]| ≤ 10⁹, 0 ≤ L ≤ 4·10⁹).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

pair<int,int> longest_within(const vector<int>& a, long long L) {
    int best = 0, start = 0;
    for (int i = 0; i < (int)a.size(); ++i) {                 // O(n^2) on long valid runs
        int mx = a[i], mn = a[i];
        for (int j = i; j < (int)a.size(); ++j) {
            mx = max(mx, a[j]); mn = min(mn, a[j]);
            if ((long long)mx - mn > L) break;
            if (j - i + 1 > best) { best = j - i + 1; start = i; }
        }
    }
    return {best, start};
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n; long long L;
    while (cin >> n >> L) {
        vector<int> a(n); for (auto& x : a) cin >> x;
        auto [len, st] = longest_within(a, L);
        cout << len << ' ' << st << '\n';
    }
}
```

## Tests
=== sample
4 4
8 2 4 7
6 5
10 1 2 4 7 2
---
2 1
4 2
=== hidden
1 0
5
5 0
3 3 1 3 3
5 0
1 2 3 4 5
4 4000000000
-1000000000 1000000000 0 7
6 1
5 6 5 6 9 9
---
1 0
2 0
1 0
4 0
4 0
=== hidden
10 1
2 -3 2 -1 -4 3 4 0 0 -2
5 3
-1 0 -2 2 -4
8 3
4 1 -4 -2 0 0 3 -4
9 0
-2 0 -4 -2 -1 -3 3 -1 0
6 0
-3 2 0 3 0 -4
10 1
-1 -4 -2 -3 0 3 2 -1 3 -1
2 3
-4 -2
9 0
1 -2 1 1 4 3 -1 -1 -3
---
2 5
3 0
3 3
1 0
1 0
2 2
2 0
2 2
=== hidden
3 5
-4 -4 -1
10 3
4 1 1 -3 3 2 -3 2 -3 0
6 2
-2 4 1 -2 -1 3
9 4
-4 2 -2 1 2 -3 4 -4 4
5 3
2 -2 -2 -1 -1
9 3
3 0 -4 -1 -2 4 -4 4 1
8 5
1 2 4 1 -1 -4 -4 -1
5 5
0 -2 -1 -1 -3
---
3 0
3 0
2 3
4 1
4 1
3 2
5 0
5 0
=== hidden
10 1
2 3 4 -2 0 -3 -3 0 4 0
7 4
4 4 -2 -2 -2 -3 3
4 0
1 -2 -3 2
3 4
-2 2 0
3 3
-4 -2 3
4 3
1 -3 -4 -3
2 0
-4 -2
6 4
0 -2 3 -2 1 2
---
2 0
4 2
1 0
3 0
2 0
3 1
1 0
3 3
=== hidden
@gen 278100198 big
=== hidden
@gen 278100199 big
=== hidden
@gen 278100200 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(8 if not big else 1):
    n = r.randint(1, 10) if not big else 1000000
    if big:
        a = [r.randint(0, 1000) for _ in range(n)]; L = r.choice([1000, 990, 500])
    else:
        a = [r.randint(-4, 4) for _ in range(n)]; L = r.randint(0, 5)
    print(n, L); print(*a)
```

## Hints
- If a window is valid, are its sub-windows valid? Then a grow/shrink sliding window works.
- You need the window max and min after removals from the left: keep one decreasing deque and one increasing deque.
- Shrink while `max − min > L`, popping deque fronts whose index is now left of the window. Update the answer only on strictly longer windows.

## Solution
"max − min ≤ L" is **monotone**: if a window is valid, every sub-window is valid. So the usual grow-right / shrink-left sliding window works, as long as you can read the window's max and min in O(1) while it shrinks from the left.

That is two sliding-window-maximum structures at once:

- `mx`: indices with **decreasing** values; the front is the window maximum.
- `mn`: indices with **increasing** values; the front is the window minimum.

After adding `hi`, while `a[mx.front()] − a[mn.front()] > L`, advance `lo` and pop any front index that fell out of the window. Then `[lo, hi]` is the longest valid window ending at `hi`.

```text
a = 8 2 4 7, L = 4
hi=0: [8]        max 8 min 8           best 1 @0
hi=1: [8 2]      8-2=6 > 4: lo=1       best 1
hi=2: [2 4]      4-2=2                  best 2 @1
hi=3: [2 4 7]    7-2=5 > 4: lo=2 [4 7] 3, not longer
```

Updating `best` only on a strictly longer window keeps the earliest start, as the tie rule requires. Use `long long` for the difference: values span 2·10⁹.

Each index enters and leaves each deque once: O(n).

```cpp
#include <bits/stdc++.h>
using namespace std;

pair<int,int> longest_within(const vector<int>& a, long long L) {
    deque<int> mx, mn;                   // window indices: values decreasing (mx) / increasing (mn)
    int best = 0, start = 0, lo = 0;
    for (int hi = 0; hi < (int)a.size(); ++hi) {
        while (!mx.empty() && a[mx.back()] <= a[hi]) mx.pop_back();
        while (!mn.empty() && a[mn.back()] >= a[hi]) mn.pop_back();
        mx.push_back(hi); mn.push_back(hi);
        while ((long long)a[mx.front()] - a[mn.front()] > L) {   // shrink until valid again
            ++lo;
            if (mx.front() < lo) mx.pop_front();
            if (mn.front() < lo) mn.pop_front();
        }
        if (hi - lo + 1 > best) { best = hi - lo + 1; start = lo; }   // strict: keeps the smallest start
    }
    return {best, start};
}
```
