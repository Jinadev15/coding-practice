---
id: cpp-ms-histogram
title: Largest Rectangle in a Histogram
difficulty: Medium
order: 3
tags: monotonic stack, histogram, previous smaller element
time_limit: 1
---
## Statement
```cpp
long long largest_rectangle(const std::vector<int>& h);
```

A histogram has `n` bars of width 1 and heights `h[i] ≥ 0`. Return the area of the largest axis-aligned rectangle that fits inside it (made of consecutive bars, as tall as the shortest of them).

`[2, 1, 5, 6, 2, 3]` → **10** (bars 5 and 6, height 5, width 2).

**Input:** cases until the end of input: `n` + `n` heights (n ≤ 10⁶ in total, 0 ≤ h ≤ 10⁹). Areas can exceed 32 bits.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

long long largest_rectangle(const vector<int>& h) {
    long long best = 0;
    for (size_t i = 0; i < h.size(); ++i) {               // O(n^2): every start, extend right
        long long mn = LLONG_MAX;
        for (size_t j = i; j < h.size(); ++j) { mn = min<long long>(mn, h[j]); best = max(best, mn * (long long)(j - i + 1)); }
    }
    return best;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n;
    while (cin >> n) {
        vector<int> h(n); for (auto& x : h) cin >> x;
        cout << largest_rectangle(h) << '\n';
    }
}
```

## Tests
=== sample
6
2 1 5 6 2 3
3
4 4 4
---
10
12
=== hidden
1
0
1
1000000000
5
1 2 3 4 5
5
5 4 3 2 1
7
3 0 3 3 0 2 2
---
0
1000000000
9
9
6
=== hidden
8
1 2 3 0 1 4 5 5
3
5 4 2
7
2 2 5 0 0 4 3
8
1 4 5 0 1 3 4 1
5
5 3 5 0 3
9
3 2 3 2 2 1 5 1 3
---
12
8
6
8
9
10
=== hidden
6
5 4 1 1 3 2
5
2 4 2 0 3
7
3 5 2 4 3 1 1
4
2 2 1 1
7
1 3 4 2 3 0 3
4
3 4 2 3
---
8
6
10
4
8
8
=== hidden
2
4 1
5
3 1 4 3 1
8
1 4 4 5 4 1 4 2
4
3 2 2 0
8
3 1 3 0 0 4 2 0
2
5 2
---
4
6
16
6
4
5
=== hidden
@gen 767043893 big
=== hidden
@gen 767043894 big
=== hidden
@gen 767043895 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 1):
    n = r.randint(1, 10) if not big else 1000000
    mode = r.random()
    if big and mode < 0.4: a = sorted(r.randint(0, 10**9) for _ in range(n))
    elif big and mode < 0.7: a = [r.randint(999990000, 10**9) for _ in range(n)]
    else: a = [r.randint(0, 5) if not big else r.randint(0, 10**9) for _ in range(n)]
    print(n); print(*a)
```

## Hints
- Fix the rectangle's height to `h[j]`. How far can it extend left and right?
- It extends to the previous strictly smaller bar and the next smaller bar. Both come from a monotonic stack.
- Keep heights increasing on the stack. When you pop `j` at position `i`, the width is `i − (new top) − 1`. Add a sentinel at the end.

## Solution
The best rectangle has the height of some bar `j`, and then it should be as wide as possible: from just after the **previous smaller** bar to just before the **next smaller** bar.

A stack of indices with increasing heights finds both at once. When bar `i` is not taller than the top `j`, bar `i` is `j`'s right boundary, and the element **below** `j` in the stack is its left boundary (everything between them was popped because it was at least as tall as `j`). So pop `j` and evaluate `h[j] · (i − left)`.

```text
h = 2 1 5 6 2 3
i=1 (1): pop 0 (h=2): left=0, width 1 -> 2
i=4 (2): pop 3 (h=6): left=3, width 1 -> 6
         pop 2 (h=5): left=2, width 2 -> 10
i=6 (sentinel): pop 5 (3): width 1 -> 3; pop 4 (2): left=2, width 4 -> 8; pop 1 (1): width 6 -> 6
best = 10
```

Popping on `>=` (not `>`) handles equal heights: the earlier equal bar is evaluated with a too-short width, but the last of the equal bars is evaluated with the full width, so the maximum is still found.

The sentinel height −1 at position n forces every remaining bar to be evaluated. Complexity: O(n).

```cpp
#include <bits/stdc++.h>
using namespace std;

long long largest_rectangle(const vector<int>& h) {
    int n = h.size();
    vector<int> st;                                  // indices, heights strictly increasing
    st.reserve(n + 1);
    long long best = 0;
    for (int i = 0; i <= n; ++i) {
        int cur = (i == n) ? -1 : h[i];              // sentinel -1 flushes everything at the end
        while (!st.empty() && h[st.back()] >= cur) {
            long long height = h[st.back()];
            st.pop_back();
            int left = st.empty() ? 0 : st.back() + 1;   // previous smaller bar is the new top
            best = max(best, height * (i - left));       // i is the next smaller-or-equal bar
        }
        st.push_back(i);
    }
    return best;
}
```
