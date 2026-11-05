---
id: cpp-hs-longest-consecutive
title: Longest Consecutive Sequence in O(n)
difficulty: Medium
order: 3
tags: hashing, sets, sequences
time_limit: 2
---
## Statement
```cpp
std::pair<int,int> longest_consecutive(const std::vector<int>& a);
    // {length, first value} of the longest run of consecutive integers x, x+1, ..., x+len-1
    // that are ALL present in a (order and duplicates don't matter); smallest first value on ties
```

`[100, 4, 200, 1, 3, 2]` gives `{4, 1}` (1, 2, 3, 4).

Sorting gives O(n log n). Do it in **O(n) expected** with a hash set. Only start walking a run from a value `x` whose predecessor `x − 1` is **absent**, so that every run is walked exactly once.

**Input:** cases until the end of input: `n` + values (n ≤ 10⁶, values are any 32-bit integers). For n = 0 print `0 0`.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

pair<int,int> longest_consecutive(const vector<int>& a) {
    unordered_set<int> s(a.begin(), a.end());
    int best = 0, start = 0;
    for (int x : a) {                                   // walks from EVERY element: O(n^2) on long runs
        int len = 0;
        while (s.count(x + len)) ++len;
        if (len > best || (len == best && x < start)) { best = len; start = x; }
    }
    return {best, start};
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
        auto [len, st] = longest_consecutive(a);
        cout << len << ' ' << st << '\n';
    }
}
```

## Tests
=== sample
6
100 4 200 1 3 2
10
0 3 7 2 5 8 4 6 0 1
---
4 1
9 0
=== hidden
0

1
5
2
2147483647 -2147483648
4
5 5 5 6
6
10 11 1 2 20 21
---
0 0
1 5
1 -2147483648
2 5
2 1
=== hidden
4
1 6 -5 2
0

9
0 0 7 7 -2 3 0 4 -1
8
-1 4 6 4 4 -8 -5 -6
4
7 2 4 -3
0

---
2 1
0 0
3 -2
2 -6
1 -3
0 0
=== hidden
7
-7 -6 4 -4 1 -4 -2
5
-4 1 3 7 7
9
-1 5 0 -6 -4 0 -7 -2 -3
5
-8 7 -1 8 -7
11
-3 -2 0 -6 -2 -8 6 2 7 -6 -7
11
3 3 -1 -5 4 -6 3 5 -5 4 -8
---
2 -7
1 -4
5 -4
2 -8
3 -8
3 3
=== hidden
7
1 7 -5 3 -7 4 -5
7
7 -5 1 -4 2 -8 5
5
2 6 -5 -2 5
1
-5
10
1 1 4 -1 -2 -4 7 2 -2 -8
6
-5 5 6 -6 -3 -2
---
2 3
2 -5
2 5
1 -5
2 -2
2 -6
=== hidden
@gen 448002510 big
=== hidden
@gen 448002511 big
=== hidden
@gen 448002512 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 2):
    n = r.randint(0, 12) if not big else 1000000
    if big and r.random() < 0.5:
        a = list(range(1, n + 1)); r.shuffle(a)
    else:
        a = [r.randint(-8, 8) if not big else r.randint(-2**31, 2**31 - 1) for _ in range(n)]
    print(n); print(*a)
```

## Hints
- A hash set gives O(1) membership tests, so you can ask "is x+1 present?" cheaply.
- Walking a run from every element repeats work. Which element should you start from?
- Only start from `x` when `x − 1` is absent. Watch for overflow at `x = INT_MAX`.

## Solution
Put every value in a hash set. A value `x` **starts** a run when `x − 1` is not in the set. Walk forward from starts only: `x, x+1, …` while present.

**Why O(n):** every value belongs to exactly one run, and every run is walked once, from its unique start. So the total number of walking steps is at most n. Non-start values cost one O(1) check each.

The starter walks from **every** element. On the input `1..n`, that's n + (n−1) + … = O(n²).

`long long` keys avoid overflow at `INT_MAX + 1` when walking past the largest int.

Complexity: O(n) expected time, O(n) space.

```cpp
#include <bits/stdc++.h>
using namespace std;

pair<int,int> longest_consecutive(const vector<int>& a) {
    unordered_set<long long> s;
    s.reserve(a.size() * 2 + 1);                        // avoid repeated rehashing
    s.insert(a.begin(), a.end());
    int best = 0; long long start = 0;
    for (long long x : s) {
        if (s.count(x - 1)) continue;                   // not the start of a run
        long long len = 1;
        while (s.count(x + len)) ++len;                 // each run is walked once, from its start
        if (len > best || (len == best && x < start)) { best = (int)len; start = x; }
    }
    return {best, (int)start};
}
```
