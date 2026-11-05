---
id: cpp-tp-trapping-rain
title: Trapping Rain Water
difficulty: Hard
order: 8
tags: two pointers, prefix maximum, arrays
time_limit: 2
---
## Statement
Bars of width 1 have heights `h[i]`. After rain, water fills every dip. The water above bar `i` is `min(highest bar to its left, highest bar to its right) − h[i]` (never negative).

```cpp
long long trapped_water(const std::vector<int>& h);       // total units of water, O(n) time, O(1) extra memory
int wet_positions(const std::vector<int>& h);             // number of bars with at least one unit of water above them
```

`[0,1,0,2,1,0,1,3,2,1,2,1]` traps 6 units, over 5 positions.

The easy O(n)-memory solution stores prefix maxima and suffix maxima arrays. Do it with **two pointers** and two running maxima instead: always process the side whose running maximum is smaller, because that side's water level is already determined.

**Input:** cases until the end of input: `n` + heights (n ≤ 10⁶, h ≤ 10⁹).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

long long trapped_water(const vector<int>& h) {
    long long w = 0;
    for (size_t i = 0; i < h.size(); ++i) {
        int lm = 0, rm = 0;
        for (size_t j = 0; j <= i; ++j) lm = max(lm, h[j]);
        for (size_t j = i; j < h.size(); ++j) rm = max(rm, h[j]);
        w += min(lm, rm) - h[i];
    }
    return w;
}
int wet_positions(const vector<int>& h) { return 0; }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n;
    while (cin >> n) {
        vector<int> h(n);
        for (auto& x : h) cin >> x;
        cout << trapped_water(h) << ' ' << wet_positions(h) << '\n';
    }
}
```

## Tests
=== sample
12
0 1 0 2 1 0 1 3 2 1 2 1
6
4 2 0 3 2 5
---
6 5
9 4
=== hidden
1
5
2
3 3
5
5 4 3 2 1
5
3 0 3 0 3
---
0 0
0 0
0 0
6 2
=== hidden
11
0 3 6 0 5 5 4 1 1 1 4
5
2 1 3 3 1
9
4 3 3 2 2 0 4 0 5
8
3 0 4 5 6 1 5 4
7
1 1 3 4 3 2 5
9
1 0 5 2 4 6 6 6 0
---
14 4
1 1
14 6
7 2
3 2
5 3
=== hidden
11
4 0 4 3 6 2 6 6 3 1 4
4
5 4 4 4
9
4 0 6 2 6 1 4 0 4
3
1 6 4
7
2 3 3 1 4 1 4
8
0 3 1 5 4 5 2 2
---
13 5
0 0
15 4
0 0
5 2
3 2
=== hidden
9
1 6 6 6 0 0 1 0 3
10
3 2 5 2 3 0 1 2 3 4
4
1 3 3 1
7
3 2 0 0 6 3 6
11
4 0 0 0 1 5 4 4 4 5 2
5
2 2 6 3 5
---
11 4
14 7
0 0
10 4
18 7
2 1
=== hidden
@gen 110216029 big
=== hidden
@gen 110216030 big
=== hidden
@gen 110216031 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 1):
    n = r.randint(1, 12) if not big else 1000000
    print(n); print(*[r.randint(0, 6) if not big else r.randint(0, 10**9) for _ in range(n)])
```

## Hints
- The water at `i` = min(max on the left, max on the right) − h[i]. Precomputing both arrays works, but uses O(n) memory.
- Keep `leftMax` and `rightMax` while moving `L` and `R` toward each other.
- Process the side whose running max is **smaller**: its water level is already known.

## Solution
**Why the smaller side is safe.** Suppose `leftMax ≤ rightMax`. The water at `L` is `min(maxLeft(L), maxRight(L)) − h[L]`. We know `maxLeft(L) = max(leftMax, h[L])` exactly. We don't know `maxRight(L)` exactly, but it is at least `rightMax ≥ leftMax`. So the minimum is decided by the left side, and `L` can be finalised now. The right side is symmetric.

Every bar is finalised once, so the scan is O(n) with O(1) memory. A shared `scan` helper with a callback avoids duplicating the pointer logic for the two questions.

**Other solutions:**

- prefix and suffix max arrays (O(n) memory)
- a monotonic stack that adds water layer by layer (the Stacks topic)

All are O(n).

Complexity: O(n) time, O(1) space.

```cpp
#include <bits/stdc++.h>
using namespace std;

template <class F>
static void scan(const vector<int>& h, F on_bar) {      // calls on_bar(water above bar)
    int L = 0, R = (int)h.size() - 1;
    long long leftMax = 0, rightMax = 0;
    while (L <= R) {
        if (leftMax <= rightMax) {                       // left level is decided by leftMax
            leftMax = max(leftMax, (long long)h[L]);
            on_bar(leftMax - h[L]); ++L;
        } else {                                         // right level is decided by rightMax
            rightMax = max(rightMax, (long long)h[R]);
            on_bar(rightMax - h[R]); --R;
        }
    }
}

long long trapped_water(const vector<int>& h) {
    long long w = 0;
    scan(h, [&](long long x) { w += x; });
    return w;
}

int wet_positions(const vector<int>& h) {
    int c = 0;
    scan(h, [&](long long x) { c += x > 0; });
    return c;
}
```
