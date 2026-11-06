---
id: cpp-ms-trap-rain
title: Trapping Rain Water, Layer by Layer
difficulty: Medium
order: 5
tags: monotonic stack, trapping rain water, two pointers
time_limit: 1
---
## Statement
```cpp
long long trapped_water(const std::vector<int>& h);
```

Bars of width 1 and heights `h[i] ≥ 0` stand side by side. After heavy rain, how many unit squares of water are trapped between them? Water falls off both ends.

`[0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]` → **6**. `[4, 2, 0, 3, 2, 5]` → **9**.

Solve it with a **monotonic stack** that fills water in horizontal layers (the explanation also shows the two-pointer method). O(n).

**Input:** cases until the end of input: `n` + heights (n ≤ 10⁶ in total, 0 ≤ h ≤ 10⁹).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

long long trapped_water(const vector<int>& h) {
    long long total = 0;
    int n = h.size();
    for (int i = 0; i < n; ++i) {                  // O(n^2): rescan both sides for every bar
        int L = 0, R = 0;
        for (int j = 0; j <= i; ++j) L = max(L, h[j]);
        for (int j = i; j < n; ++j) R = max(R, h[j]);
        total += min(L, R) - h[i];
    }
    return total;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n;
    while (cin >> n) {
        vector<int> h(n); for (auto& x : h) cin >> x;
        cout << trapped_water(h) << '\n';
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
6
9
=== hidden
1
5
2
3 0
3
5 0 5
5
1 2 3 2 1
5
5 1 1 1 5
4
1000000000 0 0 1000000000
---
0
0
5
0
12
2000000000
=== hidden
4
2 5 1 2
6
5 4 4 0 5 0
9
3 3 3 2 6 3 4 1 0
7
1 6 5 3 0 2 1
4
5 2 2 4
5
3 6 6 6 5
---
1
7
2
2
4
0
=== hidden
1
2
4
2 2 1 5
10
6 2 0 1 3 6 0 0 2 0
7
6 1 2 3 1 4 1
1
2
4
3 4 2 0
---
0
1
22
9
0
0
=== hidden
6
2 1 0 4 6 3
4
4 3 2 2
1
3
10
4 2 5 3 3 0 3 5 5 1
1
6
4
3 5 4 6
---
3
0
0
13
0
1
=== hidden
@gen 4080562046 big
=== hidden
@gen 4080562047 big
=== hidden
@gen 4080562048 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 1):
    n = r.randint(1, 10) if not big else 1000000
    a = [r.randint(0, 6) if not big else r.randint(0, 10**9) for _ in range(n)]
    if big and r.random() < 0.5:
        a[0] = a[-1] = 10**9
    print(n); print(*a)
```

## Hints
- Water stands in a basin between a left wall and a right wall that are both taller than the floor.
- Keep a non-increasing stack of indices. A taller bar closes basins: pop the floor, the new top is the left wall.
- Each layer adds `(i − left − 1) × (min(h[left], h[i]) − h[floor])`. If no left wall remains, the water spills.

## Solution
**Stack method (horizontal layers).** Keep indices with non-increasing heights: a descending staircase that can still hold water once a taller bar arrives. When `h[i]` is taller than the top, the top is the **floor** of a basin; the bar below it in the stack is the **left wall** and `i` is the **right wall**. Fill the layer between the walls from the floor up to the lower wall:

```text
h = 4 2 0 3 2 5
i=3 (3): pop 2 (floor 0), left wall 1 (2): width 1, depth min(2,3)-0 = 2   -> 2
         pop 1 (floor 2), left wall 0 (4): width 2, depth min(4,3)-2 = 1   -> 3
i=5 (5): pop 4 (floor 2), left 3 (3): width 1, depth 1                     -> 4
         pop 3 (floor 3), left 0 (4): width 4, depth 1                     -> 8
         pop 0: no left wall, stop
... total 9 (the last layer: the pop of index 0 contributes nothing)
```

Each layer is counted exactly once, when its floor is popped. Each index is pushed and popped once: O(n).

**Two-pointer alternative (O(1) memory).** Water above bar `i` is `min(maxLeft, maxRight) − h[i]`. Move two pointers inward from both ends, always from the side with the smaller maximum: that side's maximum is the binding wall, so its water is known.

The starter computes the same formula by rescanning, which is O(n²).

```cpp
#include <bits/stdc++.h>
using namespace std;

long long trapped_water(const vector<int>& h) {
    vector<int> st;                               // indices, heights non-increasing
    st.reserve(h.size());
    long long total = 0;
    for (int i = 0; i < (int)h.size(); ++i) {
        while (!st.empty() && h[st.back()] < h[i]) {
            int bottom = st.back(); st.pop_back();        // the floor of a basin
            if (st.empty()) break;                        // no left wall: water spills out
            int left = st.back();
            long long width = i - left - 1;
            long long depth = (long long)min(h[left], h[i]) - h[bottom];
            total += width * depth;                       // one horizontal layer
        }
        st.push_back(i);
    }
    return total;
}
```
